from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import CategoryKind
from app.core.exceptions.base import RepositoryError
from app.core.schemas.state import StateFilterQuery
from app.infrastructure.models import Pet, State
from app.infrastructure.repositories.base_repo import BaseRepository

_AGGREGATES = {
    CategoryKind.SUM: func.sum,
    CategoryKind.AVG: func.avg,
    CategoryKind.MIN: func.min,
    CategoryKind.MAX: func.max,
}


class StateRepository(BaseRepository[State]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=State)

    async def get_for_user(self, state_id: UUID, user_id: UUID) -> State | None:
        stmt = (
            self._owned(select(State), user_id)
            .where(State.id == state_id)
            .execution_options(populate_existing=True)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def list_for_user(self, user_id: UUID, filters: StateFilterQuery, offset: int, limit: int) -> list[State]:
        stmt = self._apply_filters(self._owned(select(State), user_id), filters)
        stmt = stmt.order_by(State.time.desc(), State.created_at.desc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def count_for_user(self, user_id: UUID, filters: StateFilterQuery) -> int:
        stmt = self._apply_filters(self._owned(select(func.count()).select_from(State), user_id), filters)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def aggregate(
        self,
        pet_id: UUID,
        cat_id: UUID,
        kind: CategoryKind,
        from_: datetime | None,
        to: datetime | None,
    ) -> tuple[float | None, int]:
        """Return (aggregated value, number of states) for one pet and category over [from_, to]."""
        filters = StateFilterQuery(petId=pet_id, catId=cat_id, from_=from_, to=to)
        count_stmt = self._apply_filters(select(func.count()).select_from(State), filters)
        try:
            count = (await self.session.execute(count_stmt)).scalar_one()
            if count == 0:
                return None, 0
            if kind == CategoryKind.COUNT:
                return float(count), count
            if kind == CategoryKind.LAST:
                last_stmt = self._apply_filters(select(State.value), filters)
                last_stmt = last_stmt.order_by(State.time.desc(), State.created_at.desc()).limit(1)
                value = (await self.session.execute(last_stmt)).scalar_one()
                return float(value), count
            agg_stmt = self._apply_filters(select(_AGGREGATES[kind](State.value)), filters)
            value = (await self.session.execute(agg_stmt)).scalar_one()
            return (float(value) if value is not None else None), count
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    @staticmethod
    def _owned(stmt: Select, user_id: UUID) -> Select:
        return stmt.join(Pet, Pet.id == State.pet_id).where(Pet.user_id == user_id)

    @staticmethod
    def _apply_filters(stmt: Select, filters: StateFilterQuery) -> Select:
        if filters.petId is not None:
            stmt = stmt.where(State.pet_id == filters.petId)
        if filters.catId is not None:
            stmt = stmt.where(State.cat_id == filters.catId)
        if filters.from_ is not None:
            stmt = stmt.where(State.time >= filters.from_)
        if filters.to is not None:
            stmt = stmt.where(State.time <= filters.to)
        return stmt
