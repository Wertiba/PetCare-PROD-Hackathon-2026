"""Standard-library JSON logging with an explicit, privacy-safe event schema."""

import json
import logging
import sys
import traceback
from contextvars import ContextVar
from datetime import UTC, datetime
from uuid import UUID

from app.infra.config import LoggingConfig

log_trace_id: ContextVar[UUID | None] = ContextVar("log_trace_id", default=None)

# Messages are static: neither request data nor exception text belongs in logs.
_EVENTS = {
    "application_started": "PetCare API started",
    "application_stopped": "PetCare API stopped",
    "http_request_completed": "HTTP request completed",
    "http_request_failed": "HTTP request failed",
    "unmapped_domain_error": "HTTP request raised an unmapped domain error",
    "application_error": "HTTP request raised an application error",
    "notification_poll_failed": "Collecting due notifications failed; the worker will retry",
    "notification_dispatch_failed": "Dispatching a due notification failed",
    "notification_delivered": "Notification delivered",
    "notification_delivery_failed": "Notification delivery failed",
    "web_push_rejected": "Web Push provider rejected delivery",
    "web_push_failed": "Web Push provider request failed",
    "avatar_generation_failed": "Avatar generation failed",
}
_UUID_FIELDS = frozenset({"notification_id", "event_id", "pet_id", "user_id", "trace_id"})
_FIELDS = frozenset({"http_method", "route", "status_code", "duration_ms", "channel", "reason", "retry_after_secs"})


def _uuid(value: object) -> str | None:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        return None


class JsonFormatter(logging.Formatter):
    def __init__(self, config: LoggingConfig) -> None:
        super().__init__()
        self.config = config

    def format(self, record: logging.LogRecord) -> str:
        event = record.msg if isinstance(record.msg, str) and record.name.startswith("app.") else None
        known_event = event in _EVENTS
        payload = {
            "env": self.config.env,
            "system": self.config.system,
            "inst": self.config.inst,
            "@timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": "WARN" if record.levelno == logging.WARNING else record.levelname,
            "logger": record.name,
            "event": event if known_event else "dependency_error",
            "message": _EVENTS[event] if known_event else "Dependency reported a runtime error",
        }
        if trace_id := _uuid(log_trace_id.get()):
            payload["trace_id"] = trace_id
        if known_event:
            for field in _UUID_FIELDS:
                if value := _uuid(getattr(record, field, None)):
                    payload[field] = value
            for field in _FIELDS:
                value = getattr(record, field, None)
                if value is not None:
                    payload[field] = value
        if record.exc_info and record.exc_info[1] is not None:
            # Do not use formatException: exception messages, SQL parameters, source
            # lines and locals can all contain personal information or credentials.
            payload["error_type"] = type(record.exc_info[1]).__name__
            payload["error_stack"] = [
                {"module": frame.f_globals.get("__name__", ""), "function": frame.f_code.co_name, "line": line}
                for frame, line in traceback.walk_tb(record.exc_info[2])
            ]
        return json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class EventFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        known_event = record.name.startswith("app.") and isinstance(record.msg, str) and record.msg in _EVENTS
        # Libraries can log URLs, credentials, SQL or payloads even at INFO. Only
        # preserve their errors, with a fixed message and sanitized exception data.
        return known_event or record.levelno >= logging.ERROR


class Logger:
    """Configure once at application bootstrap; call logging.getLogger(__name__) elsewhere."""

    def __init__(self, console_config: LoggingConfig) -> None:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(console_config))
        handler.addFilter(EventFilter())
        logging.basicConfig(handlers=[handler], level=console_config.level, force=True)
        # Remove library-owned console handlers so every runtime line uses the
        # same formatter. In particular, Uvicorn must not log raw access URLs.
        for item in logging.root.manager.loggerDict.values():
            if isinstance(item, logging.Logger):
                item.handlers.clear()
                item.propagate = True
                item.disabled = False
                item.setLevel(logging.NOTSET)
        logging.getLogger("uvicorn.access").disabled = True
