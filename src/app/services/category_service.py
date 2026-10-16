from typing import Any
from uuid import UUID

from app.core.exceptions.category_exs import CategoryNotFoundError, SystemCategoryReadOnlyError
from app.core.logger import Logger
from app.core.metrics import track
from app.core.schemas.category import (
    CategoryCreateBody,
    CategoryFilterQuery,
    CategoryReadResponse,
    CategoryUpdateBody,
)
from app.core.utils.paginated import Page, PaginationParams
from app.infrastructure.models import Category
from app.infrastructure.unit_of_work import UnitOfWork

logger = Logger.get_logger()

_FIELD_TO_COLUMN = {"name": "name", "kind": "kind", "type": "type", "unit": "unit"}


class CategoryService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _to_read_response(category: Category) -> CategoryReadResponse:
        return CategoryReadResponse(
            id=category.id,
            name=category.name,
            kind=category.kind,
            type=category.type,
            unit=category.unit,
            createdBy=category.created_by,
            isSystem=category.created_by is None,
            createdAt=category.created_at,
        )

    async def _require_own(self, user_id: UUID, category_id: UUID) -> Category:
        category = await self.uow.category_repo.get_visible(category_id, user_id)
        if category is None:
            raise CategoryNotFoundError
        if category.created_by is None:
            raise SystemCategoryReadOnlyError
        return category

    async def list_categories(
        self, user_id: UUID, pagination: PaginationParams, filters: CategoryFilterQuery
    ) -> Page[CategoryReadResponse]:
        async with self.uow:
            categories = await self.uow.category_repo.list_visible(
                user_id, filters, offset=pagination.offset, limit=pagination.limit
            )
            total = await self.uow.category_repo.count_visible(user_id, filters)
            items = [self._to_read_response(category) for category in categories]
            return Page.build(items=items, total=total, pagination=pagination)

    async def get_category(self, user_id: UUID, category_id: UUID) -> CategoryReadResponse:
        async with self.uow:
            category = await self.uow.category_repo.get_visible(category_id, user_id)
            if category is None:
                raise CategoryNotFoundError
            return self._to_read_response(category)

    async def create_category(self, user_id: UUID, data: CategoryCreateBody) -> CategoryReadResponse:
        async with self.uow:
            category = await self.uow.category_repo.add(
                Category(name=data.name, kind=data.kind, type=data.type, unit=data.unit, created_by=user_id)
            )
            logger.info("Category {} created by user {}", category.id, user_id)
            track("category", "created")
            return self._to_read_response(category)

    async def update_category(
        self, user_id: UUID, category_id: UUID, data: CategoryUpdateBody
    ) -> CategoryReadResponse:
        async with self.uow:
            category = await self._require_own(user_id, category_id)
            values: dict[str, Any] = {
                _FIELD_TO_COLUMN[field]: value for field, value in data.model_dump(exclude_unset=True).items()
            }
            if not values:
                return self._to_read_response(category)
            await self.uow.category_repo.update(category.id, values)
            updated = await self.uow.category_repo.get_visible(category.id, user_id)
            if updated is None:
                raise CategoryNotFoundError
            return self._to_read_response(updated)

    async def delete_category(self, user_id: UUID, category_id: UUID) -> None:
        async with self.uow:
            category = await self._require_own(user_id, category_id)
            await self.uow.category_repo.delete(category)
            logger.info("Category {} deleted by user {}", category_id, user_id)
            track("category", "deleted")
