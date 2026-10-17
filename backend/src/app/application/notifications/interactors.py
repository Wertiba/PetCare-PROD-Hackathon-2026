from dataclasses import dataclass
from time import time
from typing import Any

from app.application.changes import apply_changes
from app.application.notifications.dto import NotificationCreateData, NotificationResult, NotificationUpdateData
from app.application.pagination import Page, Pagination
from app.application.ports.event_gateway import EventGateway
from app.application.ports.notification_gateway import NotificationGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.events.errors import RelatedEventNotFoundError
from app.domain.events.ids import EventId
from app.domain.notifications.entity import Notification
from app.domain.notifications.enums import NotificationStatus
from app.domain.notifications.errors import NotificationNotFoundError
from app.domain.notifications.ids import NotificationId
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId

_FIELD_TO_COLUMN = {"type": "type", "status": "status", "time": "time"}


@dataclass
class _NotificationContext:
    uow: UnitOfWork
    notification_gateway: NotificationGateway
    event_gateway: EventGateway

    @staticmethod
    def _to_read_response(notification: Notification) -> NotificationResult:
        return NotificationResult(
            id=notification.id,
            eventId=notification.event_id,
            petId=notification.event.pet_id,
            eventName=notification.event.name,
            type=notification.type,
            status=notification.status,
            time=notification.time,
            createdAt=notification.created_at,
        )

    async def _require_notification(self, user_id: UserId, notification_id: NotificationId) -> Notification:
        notification = await self.notification_gateway.get_by_id(notification_id, user_id=user_id)
        if notification is None:
            raise NotificationNotFoundError
        return notification


class ListNotifications(_NotificationContext):
    async def __call__(
        self,
        user_id: UserId,
        pagination: Pagination,
        *,
        event_id: EventId | None = None,
        pet_id: PetId | None = None,
        status: NotificationStatus | None = None,
        due: bool = False,
    ) -> Page[NotificationResult]:
        now = time()
        notifications = await self.notification_gateway.get_by_user_id(
            user_id,
            now,
            offset=pagination.offset,
            limit=pagination.limit,
            event_id=event_id,
            pet_id=pet_id,
            status=status,
            due=due,
        )
        total = await self.notification_gateway.count_by_user_id(
            user_id, now, event_id=event_id, pet_id=pet_id, status=status, due=due
        )
        items = [self._to_read_response(notification) for notification in notifications]
        return Page.build(items=items, total=total, pagination=pagination)


class GetNotification(_NotificationContext):
    async def __call__(self, user_id: UserId, notification_id: NotificationId) -> NotificationResult:
        return self._to_read_response(await self._require_notification(user_id, notification_id))


class CreateNotification(_NotificationContext):
    async def __call__(self, user_id: UserId, data: NotificationCreateData) -> NotificationResult:
        event = await self.event_gateway.get_by_id(data.eventId, user_id=user_id)
        if event is None:
            raise RelatedEventNotFoundError
        notification = Notification(
            event_id=event.id,
            type=data.type,
            status=data.status,
            time=data.time if data.time is not None else event.schedule,
            event=event,
        )
        await self.uow.add(notification)
        result = self._to_read_response(notification)
        await self.uow.commit()
        return result


class UpdateNotification(_NotificationContext):
    async def __call__(
        self, user_id: UserId, notification_id: NotificationId, data: NotificationUpdateData
    ) -> NotificationResult:
        notification = await self._require_notification(user_id, notification_id)
        values: dict[str, Any] = {_FIELD_TO_COLUMN[field]: value for field, value in data.changes.items()}
        if not values:
            result = self._to_read_response(notification)
            await self.uow.commit()
            return result
        apply_changes(notification, values)
        result = self._to_read_response(notification)
        await self.uow.commit()
        return result


class DeleteNotification(_NotificationContext):
    async def __call__(self, user_id: UserId, notification_id: NotificationId) -> None:
        notification = await self._require_notification(user_id, notification_id)
        await self.uow.delete(notification)
        await self.uow.commit()
