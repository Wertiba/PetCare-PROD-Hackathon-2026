from dataclasses import dataclass
from typing import Any

from app.application.categories.dto import CategoryCreateData, CategoryResult, CategoryUpdateData
from app.application.changes import apply_changes
from app.application.pagination import Page, Pagination
from app.application.ports.category_gateway import CategoryGateway
from app.application.ports.state_gateway import StateGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_gateway import UserGateway
from app.application.users.access import is_admin
from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryType
from app.domain.categories.errors import CategoryInUseError, CategoryNotFoundError, SystemCategoryReadOnlyError
from app.domain.categories.ids import CategoryId
from app.domain.users.errors import ForbiddenError
from app.domain.users.ids import UserId

_FIELD_TO_COLUMN = {"name": "name", "kind": "kind", "type": "type", "unit": "unit"}
# Changing these reinterprets values other users have already recorded.
_MEANING_FIELDS = {"kind", "type"}


@dataclass
class _CategoryContext:
    uow: UnitOfWork
    category_gateway: CategoryGateway
    state_gateway: StateGateway
    user_gateway: UserGateway

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

    async def _require_category(self, category_id: CategoryId) -> Category:
        category = await self.category_gateway.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError
        return category

    async def _require_editable(self, user_id: UserId, category_id: CategoryId) -> Category:
        """Everyone uses every category, but only its author or an admin changes it."""
        category = await self._require_category(category_id)
        if category.created_by == user_id or await is_admin(self.user_gateway, user_id):
            return category
        if category.created_by is None:
            raise SystemCategoryReadOnlyError
        raise ForbiddenError

    async def _ensure_unused_by_others(self, user_id: UserId, category_id: CategoryId) -> None:
        if await self.state_gateway.count_by_category_of_others(category_id, user_id) > 0:
            raise CategoryInUseError


class ListCategories(_CategoryContext):
    async def __call__(
        self, pagination: Pagination, *, type_: CategoryType | None = None, name: str | None = None
    ) -> Page[CategoryResult]:
        categories = await self.category_gateway.get_all(
            offset=pagination.offset, limit=pagination.limit, type_=type_, name=name
        )
        total = await self.category_gateway.count(type_=type_, name=name)
        items = [self._to_read_response(category) for category in categories]
        return Page.build(items=items, total=total, pagination=pagination)


class GetCategory(_CategoryContext):
    async def __call__(self, category_id: CategoryId) -> CategoryResult:
        return self._to_read_response(await self._require_category(category_id))


class CreateCategory(_CategoryContext):
    async def __call__(self, user_id: UserId, data: CategoryCreateData) -> CategoryResult:
        category = Category(name=data.name, kind=data.kind, type=data.type, unit=data.unit, created_by=user_id)
        await self.uow.add(category)
        result = self._to_read_response(category)
        await self.uow.commit()
        return result


class UpdateCategory(_CategoryContext):
    async def __call__(self, user_id: UserId, category_id: CategoryId, data: CategoryUpdateData) -> CategoryResult:
        category = await self._require_editable(user_id, category_id)
        values: dict[str, Any] = {
            _FIELD_TO_COLUMN[field]: value
            for field, value in data.changes.items()
            if getattr(category, _FIELD_TO_COLUMN[field]) != value
        }
        if values.keys() & _MEANING_FIELDS:
            await self._ensure_unused_by_others(user_id, category_id)
        if values:
            apply_changes(category, values)
        result = self._to_read_response(category)
        await self.uow.commit()
        return result


class DeleteCategory(_CategoryContext):
    async def __call__(self, user_id: UserId, category_id: CategoryId) -> None:
        """Deletes the user's own states in the category too; refuses if anyone else uses it."""
        category = await self._require_editable(user_id, category_id)
        await self._ensure_unused_by_others(user_id, category_id)
        await self.uow.delete(category)
        await self.uow.commit()
