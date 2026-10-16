from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import RepositoryError
from app.core.schemas.breed import BreedFilterQuery
from app.infrastructure.models import Breed
from app.infrastructure.repositories.base_repo import BaseRepository


class BreedRepository(BaseRepository[Breed]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=Breed)

    async def get_filtered(self, filters: BreedFilterQuery, offset: int, limit: int) -> list[Breed]:
        stmt = self._apply_filters(select(Breed), filters)
        stmt = stmt.order_by(Breed.name).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def count_filtered(self, filters: BreedFilterQuery) -> int:
        stmt = self._apply_filters(select(func.count()).select_from(Breed), filters)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    @staticmethod
    def _apply_filters(stmt: Select, filters: BreedFilterQuery) -> Select:
        if filters.type is not None:
            stmt = stmt.where(Breed.type == filters.type)
        if filters.q:
            stmt = stmt.where(Breed.name.ilike(f"%{filters.q}%"))
        return stmt
