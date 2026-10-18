import asyncio
import io
import json
import logging
import sys
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.application.exceptions import WebPushDeliveryError
from app.application.ports.web_push import WebPushMessage
from app.domain.pets.errors import AvatarGenerationFailedError
from app.infra.avatars.spirit import SpiritAvatarGenerator
from app.infra.config import LoggingConfig, NotificationsConfig, WebPushConfig
from app.infra.logger import EventFilter, JsonFormatter, Logger, log_trace_id
from app.infra.notifications import worker
from app.infra.webpush.sender import PyWebPushSender

pytestmark = pytest.mark.req("P.OBS")


@pytest.fixture
def json_logs():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter(LoggingConfig(LOG_ENV="test", LOG_INST="test-01")))
    handler.addFilter(EventFilter())
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        yield stream
    finally:
        root.removeHandler(handler)


def records(stream):
    return [json.loads(line) for line in stream.getvalue().splitlines()]


def assert_private_data_absent(stream):
    for value in ("private@example.com", "secret", "private note", "private-image", "private title"):
        assert value not in stream.getvalue()


def test_json_has_sage_fields_and_drops_arbitrary_data(json_logs):
    notification_id, trace_id = uuid4(), uuid4()
    token = log_trace_id.set(trace_id)
    try:
        logging.getLogger("app.test").warning(
            "notification_delivery_failed",
            extra={
                "notification_id": notification_id,
                "event_id": "private@example.com",
                "channel": "web_push",
                "reason": "delivery_failed",
                "password": "secret",
                "body": "private note",
            },
        )
    finally:
        log_trace_id.reset(token)
    (event,) = records(json_logs)
    assert (event["env"], event["system"], event["inst"]) == ("test", "petcare", "test-01")
    assert datetime.fromisoformat(event["@timestamp"]).tzinfo == UTC
    assert event["level"] == "WARN"
    assert event["notification_id"] == str(notification_id)
    assert event["trace_id"] == str(trace_id)
    assert event["reason"] == "delivery_failed"
    assert "event_id" not in event
    assert_private_data_absent(json_logs)


@pytest.mark.parametrize(
    ("field", "value"),
    [("LOG_ENV", "Production"), ("LOG_SYSTEM", "pet care"), ("LOG_INST", "host/private"), ("LOG_CONSOLE_LEVEL", "bad")],
)
def test_invalid_log_configuration_is_rejected(field, value):
    with pytest.raises(ValidationError):
        LoggingConfig(**{field: value})


def test_library_logs_and_exception_details_cannot_leak(json_logs):
    lib = logging.getLogger("httpx")
    lib.info("GET https://host/private@example.com?token=secret")
    try:
        raise IntegrityError(
            "INSERT INTO users VALUES ('private@example.com')", {"password": "secret"}, ValueError("secret")
        )
    except IntegrityError:
        lib.exception("SQL error for private@example.com with secret")
    (event,) = records(json_logs)
    assert (event["event"], event["logger"], event["error_type"]) == ("dependency_error", "httpx", "IntegrityError")
    assert event["error_stack"][-1]["function"] == "test_library_logs_and_exception_details_cannot_leak"
    assert "INSERT" not in json_logs.getvalue()
    assert_private_data_absent(json_logs)


def test_bootstrap_routes_all_logging_to_json_without_duplicate_handlers(monkeypatch):
    root = logging.getLogger()
    old_handlers, old_level = root.handlers[:], root.level
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)
    try:
        Logger(LoggingConfig(LOG_ENV="test"))
        Logger(LoggingConfig(LOG_ENV="test"))
        logging.getLogger("app.main").info("application_started")
        logging.getLogger("uvicorn.access").error("private URL")
        logging.getLogger("httpx").info("private URL")
        (event,) = records(stdout)
        assert event["event"] == "application_started"
        assert event["inst"]
    finally:
        root.handlers = old_handlers
        root.setLevel(old_level)


def test_requests_log_template_status_duration_and_safe_trace(client, json_logs):
    trace_id, pet_id = uuid4(), uuid4()
    client.get(
        f"/api/v1/pets/{pet_id}?email=private@example.com&token=secret",
        headers={"X-Trace-Id": str(trace_id), "Authorization": "Bearer secret", "Cookie": "session=secret"},
    )
    (event,) = records(json_logs)
    assert event["event"] == "http_request_completed"
    assert event["route"] == "/api/v1/pets/{pet_id}"
    assert event["status_code"] == 401
    assert event["http_method"] == "GET"
    assert event["pet_id"] == str(pet_id)
    assert event["trace_id"] == str(trace_id)
    assert event["duration_ms"] >= 0
    assert log_trace_id.get() is None
    assert_private_data_absent(json_logs)


def test_unmatched_paths_and_arbitrary_trace_headers_are_not_logged(client, json_logs):
    client.get("/private@example.com", headers={"X-Trace-Id": "private@example.com-secret"})
    (event,) = records(json_logs)
    assert event["route"] == "<unmatched>"
    UUID(event["trace_id"])
    assert_private_data_absent(json_logs)


def test_successful_probes_are_quiet(client, json_logs):
    for path in ("/api/v1/health/liveness", "/api/v1/health/readiness", "/metrics"):
        client.get(path)
    assert not records(json_logs)


def test_unhandled_request_error_keeps_trace_and_safe_stack(client, json_logs):
    @client.app.get("/test-failure/{value}")
    async def fail(value: str):
        raise RuntimeError(f"private value: {value}, password=secret")

    trace_id = uuid4()
    with TestClient(client.app, raise_server_exceptions=False) as safe_client:
        response = safe_client.get("/test-failure/private@example.com", headers={"X-Trace-Id": str(trace_id)})
    assert response.status_code == 500
    (event,) = [r for r in records(json_logs) if r["event"] == "http_request_failed"]
    assert event["route"] == "/test-failure/{value}"
    assert event["trace_id"] == str(trace_id)
    assert event["error_type"] == "RuntimeError"
    assert event["error_stack"][-1]["function"] == "fail"
    assert_private_data_absent(json_logs)


async def test_notification_poll_failure_has_retry_context_and_safe_error(monkeypatch, json_logs):
    stop = asyncio.Event()

    async def fail(*args):
        stop.set()
        raise RuntimeError("database password=secret, private@example.com")

    monkeypatch.setattr(worker, "_dispatch_once", fail)
    await worker.run_notification_dispatch(None, None, NotificationsConfig(NOTIFICATIONS_DISPATCH_INTERVAL=3), stop)
    (event,) = records(json_logs)
    assert event["event"] == "notification_poll_failed"
    assert event["retry_after_secs"] == 3
    assert event["error_type"] == "RuntimeError"
    assert_private_data_absent(json_logs)


async def test_notification_delivery_failure_has_resource_context(monkeypatch, json_logs):
    reminder = SimpleNamespace(notification_id=uuid4(), event_id=uuid4(), pet_id=uuid4())
    dispatcher = SimpleNamespace(
        collect=AsyncMock(return_value=[reminder]),
        deliver=AsyncMock(side_effect=ValueError("private@example.com secret")),
    )
    session = AsyncMock()
    session.in_transaction = lambda: False
    session.__aenter__.return_value = session
    monkeypatch.setattr(worker, "_dispatcher", lambda *args: dispatcher)
    await worker._dispatch_once(
        SimpleNamespace(session_factory=lambda: session), None, NotificationsConfig(), asyncio.Event()
    )
    (event,) = records(json_logs)
    assert event["event"] == "notification_dispatch_failed"
    assert event["notification_id"] == str(reminder.notification_id)
    assert event["event_id"] == str(reminder.event_id)
    assert event["pet_id"] == str(reminder.pet_id)
    assert event["error_type"] == "ValueError"
    assert_private_data_absent(json_logs)


async def test_avatar_provider_logs_reason_without_request_or_response(json_logs):
    def respond(request):
        return httpx.Response(503, text="private@example.com token=secret")

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        generator = SpiritAvatarGenerator(
            base_url="https://example.com", api_key="secret", model="test", tool_model="test", timeout=1, client=client
        )
        with pytest.raises(AvatarGenerationFailedError):
            await generator.generate(b"private-image", "image/png")
    (event,) = records(json_logs)
    assert event["reason"] == "provider_http_error"
    assert event["status_code"] == 503
    assert event["error_type"] == "HTTPStatusError"
    assert_private_data_absent(json_logs)


async def test_push_failure_logs_ids_without_subscription_secrets(monkeypatch, json_logs):
    monkeypatch.setattr(
        "app.infra.webpush.sender.webpush_async", AsyncMock(side_effect=RuntimeError("private@example.com secret"))
    )
    sender = PyWebPushSender(
        WebPushConfig(VAPID_PUBLIC_KEY="public", VAPID_PRIVATE_KEY="secret", VAPID_SUBJECT="mailto:private@example.com")
    )
    message = WebPushMessage(title="private title", body="private note", notification_id=str(uuid4()))
    with pytest.raises(WebPushDeliveryError):
        await sender.send(endpoint="https://fcm.googleapis.com/secret", p256dh="secret", auth="secret", message=message)
    (event,) = records(json_logs)
    assert event["event"] == "web_push_failed"
    assert event["notification_id"] == message.notification_id
    assert event["error_type"] == "RuntimeError"
    assert_private_data_absent(json_logs)
