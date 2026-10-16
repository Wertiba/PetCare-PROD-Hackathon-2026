from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EventStatus
from app.core.exceptions.base import RepositoryError
from app.core.schemas.event import EventFilterQuery
from app.infrastructure.models import Event, Pet
from app.infrastructure.repositories.base_repo import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=Event)

    async def get_for_user(self, event_id: UUID, user_id: UUID) -> Event | None:
        stmt = (
            self._owned(select(Event), user_id)
            .where(Event.id == event_id)
            .execution_options(populate_existing=True)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def list_for_user(self, user_id: UUID, filters: EventFilterQuery, offset: int, limit: int) -> list[Event]:
        stmt = self._apply_filters(self._owned(select(Event), user_id), filters)
        stmt = stmt.order_by(Event.schedule.desc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def count_for_user(self, user_id: UUID, filters: EventFilterQuery) -> int:
        stmt = self._apply_filters(self._owned(select(func.count()).select_from(Event), user_id), filters)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def list_upcoming(
        self, user_id: UUID, until: datetime, pet_id: UUID | None, offset: int, limit: int
    ) -> list[Event]:
        """Planned events due before `until`, overdue ones included, nearest first."""
        stmt = self._upcoming(select(Event), user_id, until, pet_id)
        stmt = stmt.order_by(Event.schedule.asc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def count_upcoming(self, user_id: UUID, until: datetime, pet_id: UUID | None) -> int:
        stmt = self._upcoming(select(func.count()).select_from(Event), user_id, until, pet_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def update(self, event_id: UUID, data: dict[str, Any]) -> Event | None:
        data["updated_at"] = datetime.now(UTC)
        return await super().update(event_id, data)

    @classmethod
    def _upcoming(cls, stmt: Select, user_id: UUID, until: datetime, pet_id: UUID | None) -> Select:
        stmt = cls._owned(stmt, user_id).where(Event.status == EventStatus.PLANNED, Event.schedule <= until)
        if pet_id is not None:
            stmt = stmt.where(Event.pet_id == pet_id)
        return stmt

    @staticmethod
    def _owned(stmt: Select, user_id: UUID) -> Select:
        return stmt.join(Pet, Pet.id == Event.pet_id).where(Pet.user_id == user_id)

    @staticmethod
    def _apply_filters(stmt: Select, filters: EventFilterQuery) -> Select:
        if filters.petId is not None:
            stmt = stmt.where(Event.pet_id == filters.petId)
        if filters.status is not None:
            stmt = stmt.where(Event.status == filters.status)
        if filters.type is not None:
            stmt = stmt.where(Event.type == filters.type)
        if filters.from_ is not None:
            stmt = stmt.where(Event.schedule >= filters.from_)
        if filters.to is not None:
            stmt = stmt.where(Event.schedule <= filters.to)
        return stmt
