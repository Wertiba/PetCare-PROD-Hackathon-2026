import json

from py_vapid import Vapid
from pywebpush import WebPushException, webpush_async

from app.application.exceptions import WebPushDeliveryError
from app.application.ports.web_push import WebPushMessage, WebPushSender
from app.domain.notifications.errors import WebPushNotConfiguredError, WebPushSubscriptionGoneError
from app.infra.config import WebPushConfig
from app.infra.logger import Logger

logger = Logger.get_logger()
_GONE = frozenset({404, 410})


class PyWebPushSender(WebPushSender):
    def __init__(self, config: WebPushConfig) -> None:
        self._config = config

    def configured(self) -> bool:
        return self._config.configured()

    def public_key(self) -> str:
        if not self.configured():
            raise WebPushNotConfiguredError
        return self._config.public_key.strip()

    async def send(self, *, endpoint: str, p256dh: str, auth: str, message: WebPushMessage) -> None:
        if not self.configured():
            raise WebPushNotConfiguredError
        data = json.dumps(
            {
                "title": message.title,
                "body": message.body,
                "notificationId": message.notification_id,
                "eventId": message.event_id,
                "petId": message.pet_id,
                "url": message.url,
            },
            ensure_ascii=False,
        )
        try:
            await webpush_async(
                subscription_info={"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}},
                data=data,
                vapid_private_key=self._private_key(),
                vapid_claims={"sub": self._config.subject.strip()},
                ttl=3600,
            )
        except WebPushException as exc:
            if exc.status_code in _GONE:
                raise WebPushSubscriptionGoneError from exc
            logger.warning("Web Push rejected endpoint status {}", exc.status_code)
            raise WebPushDeliveryError("Web Push delivery failed") from exc
        except Exception as exc:
            logger.opt(exception=exc).error("Web Push delivery failed")
            raise WebPushDeliveryError("Web Push delivery failed") from exc

    def _private_key(self) -> Vapid | str:
        key = self._config.private_key.strip()
        if "BEGIN" in key:
            return Vapid.from_pem(key.encode())
        return key
