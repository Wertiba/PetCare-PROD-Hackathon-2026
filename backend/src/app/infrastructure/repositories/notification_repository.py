from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import NotificationStatus
from app.core.exceptions.base import RepositoryError
from app.core.schemas.notification import NotificationFilterQuery
from app.infrastructure.models import Event, Notification, Pet
from app.infrastructure.repositories.base_repo import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=Notification)

    async def get_for_user(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        stmt = (
            self._owned(select(Notification), user_id)
            .where(Notification.id == notification_id)
            .execution_options(populate_existing=True)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def list_for_user(
        self,
        user_id: UUID,
        filters: NotificationFilterQuery,
        now: datetime,
        offset: int,
        limit: int,
    ) -> list[Notification]:
        stmt = self._apply_filters(self._owned(select(Notification), user_id), filters, now)
        stmt = stmt.order_by(Notification.time.desc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def count_for_user(self, user_id: UUID, filters: NotificationFilterQuery, now: datetime) -> int:
        stmt = self._apply_filters(self._owned(select(func.count()).select_from(Notification), user_id), filters, now)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    @staticmethod
    def _owned(stmt: Select, user_id: UUID) -> Select:
        return (
            stmt.join(Event, Event.id == Notification.event_id)
            .join(Pet, Pet.id == Event.pet_id)
            .where(Pet.user_id == user_id)
        )

    @staticmethod
    def _apply_filters(stmt: Select, filters: NotificationFilterQuery, now: datetime) -> Select:
        if filters.eventId is not None:
            stmt = stmt.where(Notification.event_id == filters.eventId)
        if filters.petId is not None:
            stmt = stmt.where(Event.pet_id == filters.petId)
        if filters.status is not None:
            stmt = stmt.where(Notification.status == filters.status)
        if filters.due:
            stmt = stmt.where(Notification.status == NotificationStatus.PENDING, Notification.time <= now)
        return stmt
