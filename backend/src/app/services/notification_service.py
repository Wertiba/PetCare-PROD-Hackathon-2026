from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.exceptions.event_exs import RelatedEventNotFoundError
from app.core.exceptions.notification_exs import NotificationNotFoundError
from app.core.metrics import track
from app.core.schemas.notification import (
    NotificationCreateBody,
    NotificationFilterQuery,
    NotificationReadResponse,
    NotificationUpdateBody,
)
from app.core.utils.paginated import Page, PaginationParams
from app.infrastructure.models import Notification
from app.infrastructure.unit_of_work import UnitOfWork

_FIELD_TO_COLUMN = {"type": "type", "status": "status", "time": "time"}


class NotificationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _to_read_response(notification: Notification) -> NotificationReadResponse:
        return NotificationReadResponse(
            id=notification.id,
            eventId=notification.event_id,
            petId=notification.event.pet_id,
            eventName=notification.event.name,
            type=notification.type,
            status=notification.status,
            time=notification.time,
            createdAt=notification.created_at,
        )

    async def _require_notification(self, user_id: UUID, notification_id: UUID) -> Notification:
        notification = await self.uow.notification_repo.get_for_user(notification_id, user_id)
        if notification is None:
            raise NotificationNotFoundError
        return notification

    async def list_notifications(
        self, user_id: UUID, pagination: PaginationParams, filters: NotificationFilterQuery
    ) -> Page[NotificationReadResponse]:
        async with self.uow:
            now = datetime.now(UTC)
            notifications = await self.uow.notification_repo.list_for_user(
                user_id, filters, now, offset=pagination.offset, limit=pagination.limit
            )
            total = await self.uow.notification_repo.count_for_user(user_id, filters, now)
            items = [self._to_read_response(notification) for notification in notifications]
            return Page.build(items=items, total=total, pagination=pagination)

    async def get_notification(self, user_id: UUID, notification_id: UUID) -> NotificationReadResponse:
        async with self.uow:
            return self._to_read_response(await self._require_notification(user_id, notification_id))

    async def create_notification(self, user_id: UUID, data: NotificationCreateBody) -> NotificationReadResponse:
        async with self.uow:
            event = await self.uow.event_repo.get_for_user(data.eventId, user_id)
            if event is None:
                raise RelatedEventNotFoundError
            notification = await self.uow.notification_repo.add(
                Notification(
                    event_id=event.id,
                    type=data.type,
                    status=data.status,
                    time=data.time or event.schedule,
                )
            )
            track("notification", "created")
            return self._to_read_response(await self._require_notification(user_id, notification.id))

    async def update_notification(
        self, user_id: UUID, notification_id: UUID, data: NotificationUpdateBody
    ) -> NotificationReadResponse:
        async with self.uow:
            notification = await self._require_notification(user_id, notification_id)
            values: dict[str, Any] = {
                _FIELD_TO_COLUMN[field]: value for field, value in data.model_dump(exclude_unset=True).items()
            }
            if not values:
                return self._to_read_response(notification)
            await self.uow.notification_repo.update(notification.id, values)
            return self._to_read_response(await self._require_notification(user_id, notification_id))

    async def delete_notification(self, user_id: UUID, notification_id: UUID) -> None:
        async with self.uow:
            notification = await self._require_notification(user_id, notification_id)
            await self.uow.notification_repo.delete(notification)
            track("notification", "deleted")
