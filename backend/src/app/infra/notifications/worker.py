import asyncio
import logging
from time import time

from dishka import AsyncContainer

from app.application.notifications.delivery import DispatchDueNotifications
from app.application.ports.web_push import WebPushSender
from app.infra.config import NotificationsConfig
from app.infra.database.db_helper import DatabaseHelper
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infra.gateways.notification import SqlAlchemyNotificationGateway
from app.infra.gateways.notification_settings import SqlAlchemyNotificationSettingsGateway
from app.infra.gateways.web_push_subscription import SqlAlchemyWebPushSubscriptionGateway

logger = logging.getLogger(__name__)


def _dispatcher(session, webpush: WebPushSender) -> DispatchDueNotifications:
    return DispatchDueNotifications(
        notification_gateway=SqlAlchemyNotificationGateway(session),
        settings_gateway=SqlAlchemyNotificationSettingsGateway(session),
        subscription_gateway=SqlAlchemyWebPushSubscriptionGateway(session),
        uow=SqlAlchemyUnitOfWork(session),
        webpush=webpush,
    )


async def run_notification_dispatch(
    database: DatabaseHelper,
    webpush: WebPushSender,
    config: NotificationsConfig,
    stop: asyncio.Event,
) -> None:
    while not stop.is_set():
        try:
            await _dispatch_once(database, webpush, config, stop)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("notification_poll_failed", extra={"retry_after_secs": config.dispatch_interval}, exc_info=exc)
        if await _wait(stop, config.dispatch_interval):
            return


async def _dispatch_once(
    database: DatabaseHelper,
    webpush: WebPushSender,
    config: NotificationsConfig,
    stop: asyncio.Event,
) -> None:
    now = time()
    async with database.session_factory() as session:
        reminders = await _dispatcher(session, webpush).collect(now=now, earliest=now - config.max_lateness)
        if session.in_transaction():
            await session.rollback()
    for reminder in reminders:
        if stop.is_set():
            return
        try:
            async with database.session_factory() as session:
                outcomes = await _dispatcher(session, webpush).deliver(reminder, now=now)
                if session.in_transaction():
                    await session.rollback()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "notification_dispatch_failed",
                extra={
                    "notification_id": reminder.notification_id,
                    "event_id": reminder.event_id,
                    "pet_id": reminder.pet_id,
                },
                exc_info=exc,
            )
            continue
        for outcome in outcomes:
            context = {
                "notification_id": reminder.notification_id,
                "event_id": reminder.event_id,
                "pet_id": reminder.pet_id,
                "channel": outcome.channel,
            }
            if outcome.ok:
                logger.info("notification_delivered", extra=context)
            else:
                # The application returns fixed result codes, never provider text.
                reason = (
                    outcome.error
                    if outcome.error in {"not_configured", "no_subscriptions", "delivery_failed", "subscription_gone"}
                    else "unknown"
                )
                logger.error("notification_delivery_failed", extra={**context, "reason": reason})


async def _wait(stop: asyncio.Event, seconds: float) -> bool:
    if seconds <= 0:
        return stop.is_set()
    try:
        await asyncio.wait_for(stop.wait(), timeout=seconds)
    except TimeoutError:
        return False
    return True


async def start_notification_workers(container: AsyncContainer, stop: asyncio.Event) -> list[asyncio.Task[None]]:
    """Dispatch is safe on every instance: each notification is claimed with a conditional update."""
    notifications = await container.get(NotificationsConfig)
    if not notifications.worker_enabled:
        return []
    database = await container.get(DatabaseHelper)
    webpush = await container.get(WebPushSender)
    return [
        asyncio.create_task(
            run_notification_dispatch(database, webpush, notifications, stop),
            name="notification-dispatch",
        )
    ]
