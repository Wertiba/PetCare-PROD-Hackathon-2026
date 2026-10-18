from dataclasses import dataclass

from app.application.notifications.delivery import settings_view
from app.application.notifications.dto import NotificationSettingsPatch, NotificationSettingsResult
from app.application.ports.notification_settings_gateway import NotificationSettingsGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.web_push import WebPushSender
from app.application.ports.web_push_subscription_gateway import WebPushSubscriptionGateway
from app.domain.notifications.errors import WebPushEndpointRequiredError, WebPushNotConfiguredError
from app.domain.notifications.settings import NotificationSettings, WebPushSubscription
from app.domain.users.ids import UserId


@dataclass
class _SettingsContext:
    uow: UnitOfWork
    settings_gateway: NotificationSettingsGateway
    webpush: WebPushSender

    async def _current(self, user_id: UserId) -> NotificationSettingsResult:
        settings = await self.settings_gateway.get_by_user_id(user_id)
        if settings is None:
            settings = NotificationSettings(user_id=user_id)
        return settings_view(settings, self.webpush)

    async def _persist(self, settings: NotificationSettings, *, created: bool) -> NotificationSettingsResult:
        if created:
            await self.uow.add(settings)
        await self.uow.commit()
        return settings_view(settings, self.webpush)


class GetNotificationSettings(_SettingsContext):
    async def __call__(self, user_id: UserId) -> NotificationSettingsResult:
        return await self._current(user_id)


class UpdateNotificationSettings(_SettingsContext):
    async def __call__(self, user_id: UserId, data: NotificationSettingsPatch) -> NotificationSettingsResult:
        if not data.changes:
            return await self._current(user_id)
        existing = await self.settings_gateway.get_by_user_id(user_id)
        created = existing is None
        settings = existing or NotificationSettings(user_id=user_id)
        if "webPushEnabled" in data.changes:
            enabled = bool(data.changes["webPushEnabled"])
            if enabled and not self.webpush.configured():
                raise WebPushNotConfiguredError
            settings.web_push_enabled = enabled
        return await self._persist(settings, created=created)


class GetWebPushPublicKey:
    def __init__(self, webpush: WebPushSender) -> None:
        self.webpush = webpush

    async def __call__(self) -> str:
        if not self.webpush.configured():
            raise WebPushNotConfiguredError
        return self.webpush.public_key()


@dataclass
class _SubscriptionContext:
    uow: UnitOfWork
    subscription_gateway: WebPushSubscriptionGateway


class SaveWebPushSubscription(_SubscriptionContext):
    async def __call__(self, user_id: UserId, endpoint: str, p256dh: str, auth: str) -> None:
        existing = await self.subscription_gateway.get_by_endpoint(endpoint)
        if existing is None:
            await self.uow.add(WebPushSubscription(user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth))
        else:
            existing.user_id = user_id
            existing.p256dh = p256dh
            existing.auth = auth
        await self.uow.commit()


class DeleteWebPushSubscription(_SubscriptionContext):
    async def __call__(self, user_id: UserId, endpoint: str | None) -> None:
        if endpoint is None or not endpoint.strip():
            raise WebPushEndpointRequiredError
        existing = await self.subscription_gateway.get_by_endpoint(endpoint.strip())
        if existing is None or existing.user_id != user_id:
            return
        await self.uow.delete(existing)
        await self.uow.commit()
