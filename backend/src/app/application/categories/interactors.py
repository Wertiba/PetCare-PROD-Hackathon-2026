from dataclasses import dataclass
from typing import Any

from app.application.categories.dto import CategoryCreateData, CategoryResult, CategoryUpdateData
from app.application.changes import apply_changes
from app.application.pagination import Page, Pagination
from app.application.ports.category_gateway import CategoryGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryType
from app.domain.categories.errors import CategoryNotFoundError, SystemCategoryReadOnlyError
from app.domain.categories.ids import CategoryId
from app.domain.users.ids import UserId

_FIELD_TO_COLUMN = {"name": "name", "kind": "kind", "type": "type", "unit": "unit"}


@dataclass
class _CategoryContext:
    uow: UnitOfWork
    category_gateway: CategoryGateway

    @staticmethod
    def _to_read_response(category: Category) -> CategoryResult:
        return CategoryResult(
            id=category.id,
            name=category.name,
            kind=category.kind,
            type=category.type,
            unit=category.unit,
            createdBy=category.created_by,
            isSystem=category.created_by is None,
            createdAt=category.created_at,
        )

    async def _require_own(self, user_id: UserId, category_id: CategoryId) -> Category:
        category = await self.category_gateway.get_by_id(category_id, user_id=user_id)
        if category is None:
            raise CategoryNotFoundError
        if category.created_by is None:
            raise SystemCategoryReadOnlyError
        return category


class ListCategories(_CategoryContext):
    async def __call__(
        self, user_id: UserId, pagination: Pagination, *, type_: CategoryType | None = None, name: str | None = None
    ) -> Page[CategoryResult]:
        categories = await self.category_gateway.get_by_user_id(
            user_id, offset=pagination.offset, limit=pagination.limit, type_=type_, name=name
        )
        total = await self.category_gateway.count_by_user_id(user_id, type_=type_, name=name)
        items = [self._to_read_response(category) for category in categories]
        return Page.build(items=items, total=total, pagination=pagination)


class GetCategory(_CategoryContext):
    async def __call__(self, user_id: UserId, category_id: CategoryId) -> CategoryResult:
        category = await self.category_gateway.get_by_id(category_id, user_id=user_id)
        if category is None:
            raise CategoryNotFoundError
        return self._to_read_response(category)


class CreateCategory(_CategoryContext):
    async def __call__(self, user_id: UserId, data: CategoryCreateData) -> CategoryResult:
        category = Category(name=data.name, kind=data.kind, type=data.type, unit=data.unit, created_by=user_id)
        await self.uow.add(category)
        result = self._to_read_response(category)
        await self.uow.commit()
        return result


class UpdateCategory(_CategoryContext):
    async def __call__(self, user_id: UserId, category_id: CategoryId, data: CategoryUpdateData) -> CategoryResult:
        category = await self._require_own(user_id, category_id)
        values: dict[str, Any] = {_FIELD_TO_COLUMN[field]: value for field, value in data.changes.items()}
        if not values:
            result = self._to_read_response(category)
            await self.uow.commit()
            return result
        apply_changes(category, values)
        result = self._to_read_response(category)
        await self.uow.commit()
        return result


class DeleteCategory(_CategoryContext):
    async def __call__(self, user_id: UserId, category_id: CategoryId) -> None:
        category = await self._require_own(user_id, category_id)
        await self.uow.delete(category)
        await self.uow.commit()
