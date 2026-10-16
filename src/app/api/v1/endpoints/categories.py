from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.v1.dependencies import CategoryFilterDep, CategoryServiceDep, CurrentUserDep, PaginationDep
from app.core.schemas.category import CategoryCreateBody, CategoryReadResponse, CategoryUpdateBody
from app.core.schemas.responses import ErrorResponse
from app.core.utils import Page

router = APIRouter(prefix="/categories", tags=["Categories"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Category not found"}}
_READ_ONLY = {status.HTTP_403_FORBIDDEN: {"model": ErrorResponse, "description": "Built-in category is read-only"}}


@router.get("", response_model=Page[CategoryReadResponse], status_code=status.HTTP_200_OK)
async def list_categories(
    user: CurrentUserDep,
    category_service: CategoryServiceDep,
    pagination: PaginationDep,
    filters: CategoryFilterDep,
) -> Page[CategoryReadResponse]:
    """Built-in categories first, then the user's own."""
    return await category_service.list_categories(user.id, pagination, filters)


@router.post("", response_model=CategoryReadResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    user: CurrentUserDep,
    category_service: CategoryServiceDep,
    body: CategoryCreateBody,
    response: Response,
) -> CategoryReadResponse:
    created = await category_service.create_category(user.id, body)
    response.headers["Location"] = f"/api/v1/categories/{created.id}"
    return created


@router.get(
    "/{category_id}",
    response_model=CategoryReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def get_category(
    user: CurrentUserDep, category_id: UUID, category_service: CategoryServiceDep
) -> CategoryReadResponse:
    return await category_service.get_category(user.id, category_id)


@router.patch(
    "/{category_id}",
    response_model=CategoryReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_READ_ONLY},
)
async def update_category(
    user: CurrentUserDep,
    category_id: UUID,
    category_service: CategoryServiceDep,
    body: CategoryUpdateBody,
) -> CategoryReadResponse:
    return await category_service.update_category(user.id, category_id, body)


@router.delete(
    "/{category_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**_NOT_FOUND, **_READ_ONLY},
)
async def delete_category(user: CurrentUserDep, category_id: UUID, category_service: CategoryServiceDep) -> None:
    """Deleting a category also deletes all states recorded in it."""
    await category_service.delete_category(user.id, category_id)
