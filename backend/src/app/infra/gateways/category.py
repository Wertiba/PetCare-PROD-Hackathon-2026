from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.category_gateway import CategoryGateway
from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryType
from app.domain.categories.ids import CategoryId
from app.domain.users.ids import UserId


class SqlAlchemyCategoryGateway(CategoryGateway):
    """Users see built-in categories (created_by IS NULL) plus their own."""

    async def get_by_id(self, id_: CategoryId, *, user_id: UserId | None = None) -> Category | None:
        stmt = select(Category).where(Category.id == id_)
        if user_id is not None:
            stmt = self._visible(stmt, user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(
        self, user_id: UserId, offset: int, limit: int, *, type_: CategoryType | None = None, name: str | None = None
    ) -> list[Category]:
        stmt = self._apply_criteria(self._visible(select(Category), user_id), type_=type_, name=name)
        stmt = stmt.order_by(Category.created_by.is_not(None), Category.name).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count_by_user_id(
        self, user_id: UserId, *, type_: CategoryType | None = None, name: str | None = None
    ) -> int:
        stmt = self._apply_criteria(
            self._visible(select(func.count()).select_from(Category), user_id), type_=type_, name=name
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _visible(stmt: Select, user_id: UserId) -> Select:
        return stmt.where(or_(Category.created_by.is_(None), Category.created_by == user_id))

    @staticmethod
    def _apply_criteria(stmt: Select, *, type_: CategoryType | None = None, name: str | None = None) -> Select:
        if type_ is not None:
            stmt = stmt.where(Category.type == type_)
        if name:
            stmt = stmt.where(Category.name.ilike(f"%{name}%"))
        return stmt
