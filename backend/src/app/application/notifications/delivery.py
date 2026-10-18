from dataclasses import dataclass

from app.application.notifications.dto import ChannelDeliveryResult, NotificationSettingsResult, TestDeliveryResult
from app.application.notifications.messages import TEST_BODY, TEST_TITLE, reminder_parts
from app.application.ports.notification_gateway import NotificationGateway
from app.application.ports.notification_settings_gateway import NotificationSettingsGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.web_push import WebPushMessage, WebPushSender
from app.application.ports.web_push_subscription_gateway import WebPushSubscriptionGateway
from app.domain.events.ids import EventId
from app.domain.notifications.entity import Notification
from app.domain.notifications.errors import WebPushSubscriptionGoneError
from app.domain.notifications.ids import NotificationId
from app.domain.notifications.settings import NotificationSettings, WebPushSubscription
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId

WEB_PUSH = "web_push"


@dataclass(frozen=True, kw_only=True)
class DueReminder:
    notification_id: NotificationId
    event_id: EventId
    pet_id: PetId
    user_id: UserId
    event_name: str
    pet_name: str
    time: float


def reminder_from_notification(notification: Notification) -> DueReminder | None:
    event = notification.event
    pet = event.pet
    if pet is None:
        return None
    return DueReminder(
        notification_id=notification.id,
        event_id=notification.event_id,
        pet_id=pet.id,
        user_id=pet.user_id,
        event_name=event.name,
        pet_name=pet.name,
        time=notification.time,
    )


def settings_view(settings: NotificationSettings, webpush: WebPushSender) -> NotificationSettingsResult:
    return NotificationSettingsResult(
        webPushEnabled=settings.web_push_enabled,
        webPushAvailable=webpush.configured(),
    )


async def send_external(
    *,
    settings: NotificationSettings,
    subscriptions: list[WebPushSubscription],
    webpush: WebPushSender,
    uow: UnitOfWork,
    message: WebPushMessage,
) -> list[ChannelDeliveryResult]:
    if not settings.web_push_enabled:
        return []
    return [await _send_web_push(subscriptions, webpush, uow, message)]


async def _send_web_push(
    subscriptions: list[WebPushSubscription], webpush: WebPushSender, uow: UnitOfWork, message: WebPushMessage
) -> ChannelDeliveryResult:
    if not webpush.configured():
        return ChannelDeliveryResult(channel=WEB_PUSH, ok=False, error="not_configured")
    if not subscriptions:
        return ChannelDeliveryResult(channel=WEB_PUSH, ok=False, error="no_subscriptions")
    delivered = 0
    failed = 0
    removed: list[WebPushSubscription] = []
    for subscription in subscriptions:
        try:
            await webpush.send(
                endpoint=subscription.endpoint, p256dh=subscription.p256dh, auth=subscription.auth, message=message
            )
        except WebPushSubscriptionGoneError:
            removed.append(subscription)
        except Exception:
            failed += 1
        else:
            delivered += 1
    for subscription in removed:
        await uow.delete(subscription)
    if removed:
        await uow.commit()
    if delivered:
        error = "partial_failure" if failed else None
        return ChannelDeliveryResult(channel=WEB_PUSH, ok=True, error=error)
    if failed:
        return ChannelDeliveryResult(channel=WEB_PUSH, ok=False, error="delivery_failed")
    return ChannelDeliveryResult(channel=WEB_PUSH, ok=False, error="subscription_gone")


@dataclass
class DispatchDueNotifications:
    notification_gateway: NotificationGateway
    settings_gateway: NotificationSettingsGateway
    subscription_gateway: WebPushSubscriptionGateway
    uow: UnitOfWork
    webpush: WebPushSender

    async def collect(self, *, now: float, earliest: float) -> list[DueReminder]:
        rows = await self.notification_gateway.list_pending_undelivered(now=now, earliest=earliest)
        reminders: list[DueReminder] = []
        for row in rows:
            reminder = reminder_from_notification(row)
            if reminder is not None:
                reminders.append(reminder)
        return reminders

    async def deliver(self, reminder: DueReminder, *, now: float) -> list[ChannelDeliveryResult]:
        if not self.webpush.configured():
            return []
        claimed = await self.notification_gateway.claim_delivery(reminder.notification_id, now)
        if not claimed:
            return []
        settings = await self.settings_gateway.get_by_user_id(reminder.user_id)
        subscriptions = []
        if settings is not None and settings.web_push_enabled:
            subscriptions = await self.subscription_gateway.list_by_user_id(reminder.user_id)
        if settings is None or not settings.web_push_enabled:
            return []
        title, body = reminder_parts(reminder.event_name, reminder.pet_name, reminder.time)
        results = await send_external(
            settings=settings,
            subscriptions=subscriptions,
            webpush=self.webpush,
            uow=self.uow,
            message=WebPushMessage(
                title=title,
                body=body,
                notification_id=str(reminder.notification_id),
                event_id=str(reminder.event_id),
                pet_id=str(reminder.pet_id),
                url="/",
            ),
        )
        # Total failure only. A later tick retries until the reminder is older than MAX_LATENESS.
        if any(result.error == "delivery_failed" for result in results):
            await self.notification_gateway.release_delivery(reminder.notification_id, now)
        return results


@dataclass
class SendTestNotification:
    settings_gateway: NotificationSettingsGateway
    subscription_gateway: WebPushSubscriptionGateway
    uow: UnitOfWork
    webpush: WebPushSender

    async def __call__(self, user_id: UserId) -> TestDeliveryResult:
        settings = await self.settings_gateway.get_by_user_id(user_id)
        if settings is None:
            return TestDeliveryResult(channels=[])
        subscriptions = []
        if settings.web_push_enabled:
            subscriptions = await self.subscription_gateway.list_by_user_id(user_id)
        channels = await send_external(
            settings=settings,
            subscriptions=subscriptions,
            webpush=self.webpush,
            uow=self.uow,
            message=WebPushMessage(title=TEST_TITLE, body=TEST_BODY, url="/"),
        )
        return TestDeliveryResult(channels=channels)
