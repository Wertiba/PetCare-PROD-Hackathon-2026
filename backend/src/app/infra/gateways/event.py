from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.event_gateway import EventGateway
from app.domain.events.entity import Event
from app.domain.events.enums import EventStatus, EventType
from app.domain.events.ids import EventId
from app.domain.pets.entity import Pet
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class SqlAlchemyEventGateway(EventGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: EventId, *, user_id: UserId | None = None) -> Event | None:
        stmt = select(Event).where(Event.id == id_)
        if user_id is not None:
            stmt = self._owned(stmt, user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_user_id(
        self,
        user_id: UserId,
        offset: int,
        limit: int,
        *,
        pet_id: PetId | None = None,
        status: EventStatus | None = None,
        type_: EventType | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> list[Event]:
        stmt = self._apply_criteria(
            self._owned(select(Event), user_id), pet_id=pet_id, status=status, type_=type_, from_=from_, to=to
        )
        stmt = stmt.order_by(Event.schedule.desc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count_by_user_id(
        self,
        user_id: UserId,
        *,
        pet_id: PetId | None = None,
        status: EventStatus | None = None,
        type_: EventType | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> int:
        stmt = self._apply_criteria(
            self._owned(select(func.count()).select_from(Event), user_id),
            pet_id=pet_id,
            status=status,
            type_=type_,
            from_=from_,
            to=to,
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def get_upcoming(
        self, user_id: UserId, until: float, pet_id: PetId | None, offset: int, limit: int
    ) -> list[Event]:
        """Planned events due before `until`, overdue ones included, nearest first."""
        stmt = self._upcoming(select(Event), user_id, until, pet_id)
        stmt = stmt.order_by(Event.schedule.asc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count_upcoming(self, user_id: UserId, until: float, pet_id: PetId | None) -> int:
        stmt = self._upcoming(select(func.count()).select_from(Event), user_id, until, pet_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @classmethod
    def _upcoming(cls, stmt: Select, user_id: UserId, until: float, pet_id: PetId | None) -> Select:
        stmt = cls._owned(stmt, user_id).where(Event.status == EventStatus.PLANNED, Event.schedule <= until)
        if pet_id is not None:
            stmt = stmt.where(Event.pet_id == pet_id)
        return stmt

    @staticmethod
    def _owned(stmt: Select, user_id: UserId) -> Select:
        return stmt.join(Pet, Pet.id == Event.pet_id).where(Pet.user_id == user_id)

    @staticmethod
    def _apply_criteria(
        stmt: Select,
        *,
        pet_id: PetId | None = None,
        status: EventStatus | None = None,
        type_: EventType | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> Select:
        if pet_id is not None:
            stmt = stmt.where(Event.pet_id == pet_id)
        if status is not None:
            stmt = stmt.where(Event.status == status)
        if type_ is not None:
            stmt = stmt.where(Event.type == type_)
        if from_ is not None:
            stmt = stmt.where(Event.schedule >= from_)
        if to is not None:
            stmt = stmt.where(Event.schedule <= to)
        return stmt
