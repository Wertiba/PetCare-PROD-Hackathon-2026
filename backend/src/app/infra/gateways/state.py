from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.state_gateway import StateGateway
from app.domain.categories.enums import CategoryKind
from app.domain.categories.ids import CategoryId
from app.domain.pets.entity import Pet
from app.domain.pets.ids import PetId
from app.domain.states.entity import State
from app.domain.states.ids import StateId
from app.domain.users.ids import UserId

_AGGREGATES = {
    CategoryKind.SUM: func.sum,
    CategoryKind.AVG: func.avg,
    CategoryKind.MIN: func.min,
    CategoryKind.MAX: func.max,
}


class SqlAlchemyStateGateway(StateGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: StateId, *, user_id: UserId | None = None) -> State | None:
        stmt = select(State).where(State.id == id_)
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
        category_id: CategoryId | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> list[State]:
        stmt = self._apply_criteria(
            self._owned(select(State), user_id), pet_id=pet_id, category_id=category_id, from_=from_, to=to
        )
        stmt = stmt.order_by(State.time.desc(), State.created_at.desc()).offset(offset).limit(limit)
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
        category_id: CategoryId | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> int:
        stmt = self._apply_criteria(
            self._owned(select(func.count()).select_from(State), user_id),
            pet_id=pet_id,
            category_id=category_id,
            from_=from_,
            to=to,
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def aggregate(
        self, pet_id: PetId, category_id: CategoryId, kind: CategoryKind, from_: float | None, to: float | None
    ) -> tuple[float | None, int]:
        """Return (aggregated value, number of states) for one pet and category over [from_, to]."""
        count_stmt = self._apply_criteria(
            select(func.count()).select_from(State), pet_id=pet_id, category_id=category_id, from_=from_, to=to
        )
        try:
            count = (await self.session.execute(count_stmt)).scalar_one()
            if count == 0:
                return (None, 0)
            if kind == CategoryKind.COUNT:
                return (float(count), count)
            if kind == CategoryKind.LAST:
                last_stmt = self._apply_criteria(
                    select(State.value), pet_id=pet_id, category_id=category_id, from_=from_, to=to
                )
                last_stmt = last_stmt.order_by(State.time.desc(), State.created_at.desc()).limit(1)
                value = (await self.session.execute(last_stmt)).scalar_one()
                return (float(value), count)
            agg_stmt = self._apply_criteria(
                select(_AGGREGATES[kind](State.value)), pet_id=pet_id, category_id=category_id, from_=from_, to=to
            )
            value = (await self.session.execute(agg_stmt)).scalar_one()
            return (float(value) if value is not None else None, count)
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count_by_category_of_others(self, category_id: CategoryId, user_id: UserId) -> int:
        stmt = (
            select(func.count())
            .select_from(State)
            .join(Pet, Pet.id == State.pet_id)
            .where(State.category_id == category_id, Pet.user_id != user_id)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _owned(stmt: Select, user_id: UserId) -> Select:
        return stmt.join(Pet, Pet.id == State.pet_id).where(Pet.user_id == user_id)

    @staticmethod
    def _apply_criteria(
        stmt: Select,
        *,
        pet_id: PetId | None = None,
        category_id: CategoryId | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> Select:
        if pet_id is not None:
            stmt = stmt.where(State.pet_id == pet_id)
        if category_id is not None:
            stmt = stmt.where(State.category_id == category_id)
        if from_ is not None:
            stmt = stmt.where(State.time >= from_)
        if to is not None:
            stmt = stmt.where(State.time <= to)
        return stmt
