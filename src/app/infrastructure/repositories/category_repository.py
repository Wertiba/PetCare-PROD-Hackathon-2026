from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import RepositoryError
from app.core.schemas.category import CategoryFilterQuery
from app.infrastructure.models import Category
from app.infrastructure.repositories.base_repo import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Users see built-in categories (created_by IS NULL) plus their own."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=Category)

    async def get_visible(self, category_id: UUID, user_id: UUID) -> Category | None:
        stmt = (
            self._visible(select(Category), user_id)
            .where(Category.id == category_id)
            .execution_options(populate_existing=True)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def list_visible(
        self, user_id: UUID, filters: CategoryFilterQuery, offset: int, limit: int
    ) -> list[Category]:
        stmt = self._apply_filters(self._visible(select(Category), user_id), filters)
        stmt = stmt.order_by(Category.created_by.is_not(None), Category.name).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def count_visible(self, user_id: UUID, filters: CategoryFilterQuery) -> int:
        stmt = self._apply_filters(self._visible(select(func.count()).select_from(Category), user_id), filters)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    @staticmethod
    def _visible(stmt: Select, user_id: UUID) -> Select:
        return stmt.where(or_(Category.created_by.is_(None), Category.created_by == user_id))

    @staticmethod
    def _apply_filters(stmt: Select, filters: CategoryFilterQuery) -> Select:
        if filters.type is not None:
            stmt = stmt.where(Category.type == filters.type)
        if filters.q:
            stmt = stmt.where(Category.name.ilike(f"%{filters.q}%"))
        return stmt
