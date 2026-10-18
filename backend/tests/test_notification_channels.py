import os
import uuid
from time import time
from types import SimpleNamespace

import pytest
from dishka import Provider, Scope, provide
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.application.notifications.delivery import DispatchDueNotifications
from app.application.notifications.dto import ChannelDeliveryResult
from app.application.ports.avatar_generator import AvatarGenerator
from app.application.ports.web_push import WebPushMessage, WebPushSender
from app.bootstrap import build_container
from app.domain.notifications.errors import WebPushNotConfiguredError, WebPushSubscriptionGoneError
from app.domain.notifications.settings import NotificationSettings, WebPushSubscription
from app.infra.config import WebPushConfig
from app.infra.database.db_helper import DatabaseHelper
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infra.gateways.notification import SqlAlchemyNotificationGateway
from app.infra.gateways.notification_settings import SqlAlchemyNotificationSettingsGateway
from app.infra.gateways.web_push_subscription import SqlAlchemyWebPushSubscriptionGateway
from app.infra.webpush.sender import PyWebPushSender
from app.main import create_app
from conftest import register_user

pytestmark = pytest.mark.req("5.4.7")

ENDPOINT_A = "https://push.example.com/subscription/a"
ENDPOINT_B = "https://push.example.com/subscription/b"


class FakeWebPush:
    def __init__(self) -> None:
        self.enabled = True
        self.key = "test-public-key"
        self.sent: list[tuple[str, WebPushMessage]] = []
        self.gone: set[str] = set()
        self.fail: set[str] = set()

    def configured(self) -> bool:
        return self.enabled

    def public_key(self) -> str:
        if not self.enabled:
            raise WebPushNotConfiguredError
        return self.key

    def allows_endpoint(self, endpoint: str) -> bool:
        hosts = os.environ.get(
            "WEB_PUSH_ALLOWED_HOSTS",
            "fcm.googleapis.com,push.services.mozilla.com,notify.windows.com,push.apple.com,example.com",
        )
        return PyWebPushSender(WebPushConfig(WEB_PUSH_ALLOWED_HOSTS=hosts)).allows_endpoint(endpoint)

    async def send(self, *, endpoint: str, p256dh: str, auth: str, message: WebPushMessage) -> None:
        if endpoint in self.gone:
            raise WebPushSubscriptionGoneError
        if endpoint in self.fail:
            raise RuntimeError("push down")
        self.sent.append((endpoint, message))


@pytest.fixture
async def ready(db_session_factory, catalog, generator):
    webpush = FakeWebPush()

    class Overrides(Provider):
        @provide(scope=Scope.APP, override=True)
        def database(self) -> DatabaseHelper:
            return SimpleNamespace(session_factory=db_session_factory)

        @provide(scope=Scope.APP, override=True)
        def avatars(self) -> AvatarGenerator:
            return generator

        @provide(scope=Scope.APP, override=True)
        def webpush(self) -> WebPushSender:
            return webpush

    application = create_app(build_container(Overrides()))
    with TestClient(application, base_url="https://testserver") as test_client:
        yield test_client, webpush


def test_settings_when_web_push_is_not_configured(client, auth):
    client.cookies.clear()
    assert client.get("/api/v1/notifications/settings").status_code == 401
    settings = client.get("/api/v1/notifications/settings", headers=auth)
    assert settings.status_code == 200, settings.text
    assert settings.json() == {"webPushEnabled": False, "webPushAvailable": False}
    missing_key = client.get("/api/v1/notifications/web-push/public-key", headers=auth)
    assert missing_key.status_code == 503
    assert missing_key.json()["code"] == "WEB_PUSH_NOT_CONFIGURED"
    enable_push = client.patch("/api/v1/notifications/settings", json={"webPushEnabled": True}, headers=auth)
    assert enable_push.status_code == 503
    assert enable_push.json()["code"] == "WEB_PUSH_NOT_CONFIGURED"


async def test_settings_web_push_and_test_message(ready):
    client, webpush = ready
    _, headers = register_user(client, login="owner")
    current = client.get("/api/v1/notifications/settings", headers=headers)
    assert current.json()["webPushAvailable"] is True
    disabled = client.post("/api/v1/notifications/test", headers=headers)
    assert disabled.status_code == 200
    assert disabled.json()["channels"] == []
    enabled = client.patch("/api/v1/notifications/settings", json={"webPushEnabled": True}, headers=headers)
    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["webPushEnabled"] is True
    waiting = client.post("/api/v1/notifications/test", headers=headers)
    assert waiting.json()["channels"] == [{"channel": "web_push", "ok": False, "error": "no_subscriptions"}]
    created = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": ENDPOINT_A, "expirationTime": None, "keys": {"p256dh": "p256", "auth": "auth"}},
        headers=headers,
    )
    assert created.status_code == 204, created.text
    again = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": ENDPOINT_A, "keys": {"p256dh": "p256-new", "auth": "auth-new"}},
        headers=headers,
    )
    assert again.status_code == 204
    public = client.get("/api/v1/notifications/web-push/public-key", headers=headers)
    assert public.status_code == 200
    assert public.json() == {"publicKey": "test-public-key"}
    tested = client.post("/api/v1/notifications/test", headers=headers)
    assert tested.status_code == 200, tested.text
    assert tested.json()["channels"] == [{"channel": "web_push", "ok": True, "error": None}]
    assert webpush.sent[0][0] == ENDPOINT_A
    assert webpush.sent[0][1].title == "Проверка уведомлений"
    assert webpush.sent[0][1].url == "/"


async def test_web_push_subscription_ownership(ready, db_session_factory):
    client, _ = ready
    owner_id, owner = register_user(client, login="push-owner")
    other_id, other = register_user(client, login="push-other")
    body = {"endpoint": ENDPOINT_A, "keys": {"p256dh": "p256", "auth": "auth"}}
    assert client.post("/api/v1/notifications/web-push/subscriptions", json=body, headers=owner).status_code == 204
    assert await _subscription_user(db_session_factory, ENDPOINT_A) == owner_id
    kept = client.delete("/api/v1/notifications/web-push/subscriptions", params={"endpoint": ENDPOINT_A}, headers=other)
    assert kept.status_code == 204
    assert await _subscription_user(db_session_factory, ENDPOINT_A) == owner_id
    moved = dict(body)
    moved["keys"] = {"p256dh": "other", "auth": "other"}
    assert client.post("/api/v1/notifications/web-push/subscriptions", json=moved, headers=other).status_code == 204
    assert await _subscription_user(db_session_factory, ENDPOINT_A) == other_id
    ignored = client.request(
        "DELETE", "/api/v1/notifications/web-push/subscriptions", json={"endpoint": ENDPOINT_A}, headers=owner
    )
    assert ignored.status_code == 204
    assert await _subscription_user(db_session_factory, ENDPOINT_A) == other_id
    removed = client.delete(
        "/api/v1/notifications/web-push/subscriptions", params={"endpoint": ENDPOINT_A}, headers=other
    )
    assert removed.status_code == 204
    assert await _subscription_user(db_session_factory, ENDPOINT_A) is None
    missing = client.delete("/api/v1/notifications/web-push/subscriptions", headers=other)
    assert missing.status_code == 422
    bad = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "not-a-url", "keys": {"p256dh": "p", "auth": "a"}},
        headers=owner,
    )
    assert bad.status_code == 422


async def test_dispatcher_delivers_due_notification_once_and_leaves_status(client, auth, pet_id, db_session_factory):
    user_id = client.get("/api/v1/users/me", headers=auth).json()["id"]
    event_id = client.post(
        "/api/v1/events", json={"petId": pet_id, "name": "Таблетка", "schedule": time() + 3600}, headers=auth
    ).json()["id"]
    due = client.post("/api/v1/notifications", json={"eventId": event_id, "time": time() - 30}, headers=auth).json()
    stale = client.post(
        "/api/v1/notifications", json={"eventId": event_id, "time": time() - 90000}, headers=auth
    ).json()
    await _enable_web_push(db_session_factory, user_id, [ENDPOINT_A, ENDPOINT_B])
    webpush = FakeWebPush()
    webpush.gone.add(ENDPOINT_B)
    now = time()
    await _dispatch(db_session_factory, webpush, now=now, lateness=86400)
    assert [item[0] for item in webpush.sent] == [ENDPOINT_A]
    message = webpush.sent[0][1]
    assert message.title == "Напоминание: Таблетка"
    assert "Барсик" in message.body
    assert message.notification_id == due["id"]
    assert message.event_id == event_id
    assert message.pet_id == pet_id
    assert message.url == "/"
    body = client.get(f"/api/v1/notifications/{due['id']}", headers=auth).json()
    assert body["status"] == "pending"
    assert body["deliveredAt"] is not None
    stale_body = client.get(f"/api/v1/notifications/{stale['id']}", headers=auth).json()
    assert stale_body["status"] == "pending"
    assert stale_body["deliveredAt"] is None
    assert await _subscription_user(db_session_factory, ENDPOINT_B) is None
    await _dispatch(db_session_factory, webpush, now=time(), lateness=86400)
    assert len(webpush.sent) == 1
    async with db_session_factory() as session:
        claimed = await SqlAlchemyNotificationGateway(session).claim_delivery(uuid.UUID(due["id"]), time())
    assert claimed is False


async def test_failed_subscription_does_not_block_the_other(client, auth, pet_id, db_session_factory):
    user_id = client.get("/api/v1/users/me", headers=auth).json()["id"]
    event_id = client.post(
        "/api/v1/events", json={"petId": pet_id, "name": "Корм", "schedule": time() + 60}, headers=auth
    ).json()["id"]
    created = client.post("/api/v1/notifications", json={"eventId": event_id, "time": time() - 5}, headers=auth).json()
    await _enable_web_push(db_session_factory, user_id, [ENDPOINT_A, ENDPOINT_B])
    webpush = FakeWebPush()
    webpush.fail.add(ENDPOINT_B)
    outcomes = await _dispatch(db_session_factory, webpush, now=time(), lateness=86400)
    assert outcomes == [ChannelDeliveryResult(channel="web_push", ok=True, error="partial_failure")]
    assert {item[0] for item in webpush.sent} == {ENDPOINT_A}
    assert await _subscription_user(db_session_factory, ENDPOINT_B) == user_id
    body = client.get(f"/api/v1/notifications/{created['id']}", headers=auth).json()
    assert body["status"] == "pending"
    assert body["deliveredAt"] is not None
    assert await _dispatch(db_session_factory, webpush, now=time(), lateness=86400) == []
    assert len(webpush.sent) == 1


async def test_web_push_sender_turns_410_into_gone(monkeypatch):
    from pywebpush import WebPushException

    async def fail(**kwargs):
        raise WebPushException("gone", response=SimpleNamespace(status_code=410, text="gone", reason="Gone"))

    monkeypatch.setattr("app.infra.webpush.sender.webpush_async", fail)
    sender = PyWebPushSender(
        WebPushConfig(
            VAPID_PUBLIC_KEY="pub",
            VAPID_PRIVATE_KEY="priv",
            VAPID_SUBJECT="mailto:pet@example.com",
            WEB_PUSH_ALLOWED_HOSTS="example.com",
        )
    )
    with pytest.raises(WebPushSubscriptionGoneError):
        await sender.send(
            endpoint=ENDPOINT_A,
            p256dh="p",
            auth="a",
            message=WebPushMessage(title="Напоминание", body="текст", notification_id="1", event_id="2", pet_id="3"),
        )


async def test_dispatcher_waits_until_web_push_can_send(client, auth, pet_id, db_session_factory):
    user_id = client.get("/api/v1/users/me", headers=auth).json()["id"]
    notification_id = _due_notification(client, auth, pet_id, name="Прогулка")
    webpush = FakeWebPush()
    assert await _dispatch(db_session_factory, webpush, now=time(), lateness=86400) == []
    assert _delivered_at(client, auth, notification_id) is None

    await _set_push_enabled(db_session_factory, user_id, enabled=False)
    assert await _dispatch(db_session_factory, webpush, now=time(), lateness=86400) == []
    assert _delivered_at(client, auth, notification_id) is None

    await _set_push_enabled(db_session_factory, user_id, enabled=True)
    assert await _dispatch(db_session_factory, webpush, now=time(), lateness=86400) == []
    assert _delivered_at(client, auth, notification_id) is None

    await _add_subscriptions(db_session_factory, user_id, [ENDPOINT_A])
    outcomes = await _dispatch(db_session_factory, webpush, now=time(), lateness=86400)
    assert outcomes == [ChannelDeliveryResult(channel="web_push", ok=True, error=None)]
    assert [item[0] for item in webpush.sent] == [ENDPOINT_A]
    assert _delivered_at(client, auth, notification_id) is not None


async def test_unconfigured_web_push_does_not_claim(client, auth, pet_id, db_session_factory):
    user_id = client.get("/api/v1/users/me", headers=auth).json()["id"]
    notification_id = _due_notification(client, auth, pet_id, name="Вода")
    await _enable_web_push(db_session_factory, user_id, [ENDPOINT_A])
    webpush = FakeWebPush()
    webpush.enabled = False
    assert await _dispatch(db_session_factory, webpush, now=time(), lateness=86400) == []
    assert webpush.sent == []
    assert _delivered_at(client, auth, notification_id) is None
    webpush.enabled = True
    outcomes = await _dispatch(db_session_factory, webpush, now=time(), lateness=86400)
    assert outcomes[0].ok is True
    assert _delivered_at(client, auth, notification_id) is not None


async def test_total_push_failure_is_retried(client, auth, pet_id, db_session_factory):
    user_id = client.get("/api/v1/users/me", headers=auth).json()["id"]
    notification_id = _due_notification(client, auth, pet_id, name="Кормление")
    await _enable_web_push(db_session_factory, user_id, [ENDPOINT_A, ENDPOINT_B])
    webpush = FakeWebPush()
    webpush.fail.update({ENDPOINT_A, ENDPOINT_B})
    failed = await _dispatch(db_session_factory, webpush, now=time(), lateness=86400)
    assert failed == [ChannelDeliveryResult(channel="web_push", ok=False, error="delivery_failed")]
    assert webpush.sent == []
    assert _delivered_at(client, auth, notification_id) is None
    webpush.fail.clear()
    delivered = await _dispatch(db_session_factory, webpush, now=time(), lateness=86400)
    assert delivered == [ChannelDeliveryResult(channel="web_push", ok=True, error=None)]
    assert {item[0] for item in webpush.sent} == {ENDPOINT_A, ENDPOINT_B}
    assert _delivered_at(client, auth, notification_id) is not None
    assert await _dispatch(db_session_factory, webpush, now=time(), lateness=86400) == []


async def test_revoked_subscriptions_stay_delivered(client, auth, pet_id, db_session_factory):
    user_id = client.get("/api/v1/users/me", headers=auth).json()["id"]
    notification_id = _due_notification(client, auth, pet_id, name="Визит")
    await _enable_web_push(db_session_factory, user_id, [ENDPOINT_A])
    webpush = FakeWebPush()
    webpush.gone.add(ENDPOINT_A)
    outcomes = await _dispatch(db_session_factory, webpush, now=time(), lateness=86400)
    assert outcomes == [ChannelDeliveryResult(channel="web_push", ok=False, error="subscription_gone")]
    assert webpush.sent == []
    assert await _subscription_user(db_session_factory, ENDPOINT_A) is None
    assert _delivered_at(client, auth, notification_id) is not None
    assert await _dispatch(db_session_factory, webpush, now=time(), lateness=86400) == []


async def test_subscription_endpoint_is_https_and_allowlisted(client, auth):
    http_endpoint = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "http://fcm.googleapis.com/push", "keys": {"p256dh": "p", "auth": "a"}},
        headers=auth,
    )
    assert http_endpoint.status_code == 422
    assert http_endpoint.json()["fieldErrors"][0]["field"] == "endpoint"
    foreign = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "https://push.evil.test/subscription", "keys": {"p256dh": "p", "auth": "a"}},
        headers=auth,
    )
    assert foreign.status_code == 422
    assert foreign.json()["details"] == {"field": "endpoint"}
    lookalike = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "https://notfcm.googleapis.com/push", "keys": {"p256dh": "p", "auth": "a"}},
        headers=auth,
    )
    assert lookalike.status_code == 422
    assert lookalike.json()["details"] == {"field": "endpoint"}
    accepted = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "https://updates.fcm.googleapis.com/subscription", "keys": {"p256dh": "p", "auth": "a"}},
        headers=auth,
    )
    assert accepted.status_code == 204, accepted.text


async def test_web_push_keys_longer_than_255_are_rejected(client, auth):
    too_long = "k" * 256
    p256 = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "https://fcm.googleapis.com/keys", "keys": {"p256dh": too_long, "auth": "a"}},
        headers=auth,
    )
    assert p256.status_code == 422
    assert p256.json()["fieldErrors"][0]["field"] == "keys.p256dh"
    auth_key = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "https://fcm.googleapis.com/keys", "keys": {"p256dh": "p", "auth": too_long}},
        headers=auth,
    )
    assert auth_key.status_code == 422
    assert auth_key.json()["fieldErrors"][0]["field"] == "keys.auth"
    accepted = client.post(
        "/api/v1/notifications/web-push/subscriptions",
        json={"endpoint": "https://fcm.googleapis.com/keys", "keys": {"p256dh": "p" * 255, "auth": "a" * 255}},
        headers=auth,
    )
    assert accepted.status_code == 204, accepted.text


def test_vapid_subject_must_be_mailto_or_https():
    WebPushConfig(VAPID_SUBJECT="")
    WebPushConfig(VAPID_SUBJECT="mailto:pet@example.com")
    WebPushConfig(VAPID_SUBJECT="https://pet.example.com")
    assert WebPushConfig(VAPID_PUBLIC_KEY="p", VAPID_PRIVATE_KEY="k", VAPID_SUBJECT="").configured() is False
    assert WebPushConfig(VAPID_PUBLIC_KEY="p", VAPID_PRIVATE_KEY="k", VAPID_SUBJECT="mailto:a@b.c").configured() is True
    with pytest.raises(ValidationError):
        WebPushConfig(VAPID_SUBJECT="pet@example.com")
    with pytest.raises(ValidationError):
        WebPushConfig(VAPID_SUBJECT="http://pet.example.com")


def test_web_push_timeout_must_be_positive():
    assert WebPushConfig().timeout == 10
    with pytest.raises(ValidationError):
        WebPushConfig(WEB_PUSH_TIMEOUT=0)


async def test_web_push_sender_passes_timeout(monkeypatch):
    captured: dict = {}

    async def ok(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr("app.infra.webpush.sender.webpush_async", ok)
    sender = PyWebPushSender(
        WebPushConfig(
            VAPID_PUBLIC_KEY="pub",
            VAPID_PRIVATE_KEY="priv",
            VAPID_SUBJECT="mailto:pet@example.com",
            WEB_PUSH_TIMEOUT=4.5,
            WEB_PUSH_ALLOWED_HOSTS="example.com",
        )
    )
    await sender.send(
        endpoint=ENDPOINT_A,
        p256dh="p",
        auth="a",
        message=WebPushMessage(title="Напоминание", body="текст"),
    )
    assert captured["timeout"] == 4.5


async def test_sender_drops_endpoint_outside_allowlist(monkeypatch):
    async def unexpected(**kwargs):
        raise AssertionError(kwargs["subscription_info"]["endpoint"])

    monkeypatch.setattr("app.infra.webpush.sender.webpush_async", unexpected)
    sender = PyWebPushSender(
        WebPushConfig(VAPID_PUBLIC_KEY="pub", VAPID_PRIVATE_KEY="priv", VAPID_SUBJECT="mailto:pet@example.com")
    )
    with pytest.raises(WebPushSubscriptionGoneError):
        await sender.send(
            endpoint="https://evil.example/push",
            p256dh="p",
            auth="a",
            message=WebPushMessage(title="Напоминание", body="текст"),
        )


async def _enable_web_push(db_session_factory, user_id: str, endpoints: list[str]) -> None:
    async with db_session_factory() as session:
        session.add(NotificationSettings(user_id=uuid.UUID(user_id), web_push_enabled=True))
        for endpoint in endpoints:
            session.add(WebPushSubscription(user_id=uuid.UUID(user_id), endpoint=endpoint, p256dh="p256", auth="auth"))
        await session.commit()


async def _subscription_user(db_session_factory, endpoint: str) -> str | None:
    async with db_session_factory() as session:
        row = await SqlAlchemyWebPushSubscriptionGateway(session).get_by_endpoint(endpoint)
        return None if row is None else str(row.user_id)


def _due_notification(client, auth, pet_id: str, *, name: str) -> str:
    event_id = client.post(
        "/api/v1/events", json={"petId": pet_id, "name": name, "schedule": time() + 60}, headers=auth
    ).json()["id"]
    return client.post("/api/v1/notifications", json={"eventId": event_id, "time": time() - 5}, headers=auth).json()[
        "id"
    ]


def _delivered_at(client, auth, notification_id: str):
    return client.get(f"/api/v1/notifications/{notification_id}", headers=auth).json()["deliveredAt"]


async def _set_push_enabled(db_session_factory, user_id: str, *, enabled: bool) -> None:
    async with db_session_factory() as session:
        existing = await SqlAlchemyNotificationSettingsGateway(session).get_by_user_id(uuid.UUID(user_id))
        if existing is None:
            session.add(NotificationSettings(user_id=uuid.UUID(user_id), web_push_enabled=enabled))
        else:
            existing.web_push_enabled = enabled
        await session.commit()


async def _add_subscriptions(db_session_factory, user_id: str, endpoints: list[str]) -> None:
    async with db_session_factory() as session:
        for endpoint in endpoints:
            session.add(WebPushSubscription(user_id=uuid.UUID(user_id), endpoint=endpoint, p256dh="p256", auth="auth"))
        await session.commit()


async def _dispatch(db_session_factory, webpush, *, now: float, lateness: int) -> list[ChannelDeliveryResult]:
    async with db_session_factory() as session:
        dispatcher = DispatchDueNotifications(
            notification_gateway=SqlAlchemyNotificationGateway(session),
            settings_gateway=SqlAlchemyNotificationSettingsGateway(session),
            subscription_gateway=SqlAlchemyWebPushSubscriptionGateway(session),
            uow=SqlAlchemyUnitOfWork(session),
            webpush=webpush,
        )
        reminders = await dispatcher.collect(now=now, earliest=now - lateness)
        if session.in_transaction():
            await session.rollback()
    outcomes: list[ChannelDeliveryResult] = []
    for reminder in reminders:
        async with db_session_factory() as session:
            outcomes.extend(
                await DispatchDueNotifications(
                    notification_gateway=SqlAlchemyNotificationGateway(session),
                    settings_gateway=SqlAlchemyNotificationSettingsGateway(session),
                    subscription_gateway=SqlAlchemyWebPushSubscriptionGateway(session),
                    uow=SqlAlchemyUnitOfWork(session),
                    webpush=webpush,
                ).deliver(reminder, now=now)
            )
    return outcomes
