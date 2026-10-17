from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.categories.dto import CategoryCreateData, CategoryUpdateData
from app.application.categories.interactors import (
    CreateCategory,
    DeleteCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
)
from app.application.pagination import Pagination
from app.domain.categories.enums import CategoryType
from app.domain.categories.ids import CategoryId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.category import CategoryCreateBody, CategoryReadResponse, CategoryUpdateBody
from app.presentation.http.schemas.responses import ErrorResponse

router = APIRouter(prefix="/categories", tags=["Categories"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Category not found"}}
_READ_ONLY = {status.HTTP_403_FORBIDDEN: {"model": ErrorResponse, "description": "Built-in category is read-only"}}


@router.get("", response_model=Page[CategoryReadResponse], status_code=status.HTTP_200_OK)
async def list_categories(
    user: CurrentUserDep,
    interactor: FromDishka[ListCategories],
    pagination: PaginationDep,
    type: CategoryType | None = Query(None),
    q: str | None = Query(None, description="Substring of the category name"),
) -> Page[CategoryReadResponse]:
    """Built-in categories first, then the user's own."""
    return Page[CategoryReadResponse].model_validate(
        await interactor(user.id, Pagination(page=pagination.page, size=pagination.size), type_=type, name=q),
        from_attributes=True,
    )


@router.post("", response_model=CategoryReadResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    user: CurrentUserDep, interactor: FromDishka[CreateCategory], body: CategoryCreateBody, response: Response
) -> CategoryReadResponse:
    created = await interactor(user.id, CategoryCreateData(**body.model_dump()))
    track("category", "created")
    response.headers["Location"] = f"/api/v1/categories/{created.id}"
    return CategoryReadResponse.model_validate(created, from_attributes=True)


@router.get("/{category_id}", response_model=CategoryReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_category(
    user: CurrentUserDep, category_id: CategoryId, interactor: FromDishka[GetCategory]
) -> CategoryReadResponse:
    return CategoryReadResponse.model_validate(await interactor(user.id, category_id), from_attributes=True)


@router.patch(
    "/{category_id}",
    response_model=CategoryReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_READ_ONLY},
)
async def update_category(
    user: CurrentUserDep, category_id: CategoryId, interactor: FromDishka[UpdateCategory], body: CategoryUpdateBody
) -> CategoryReadResponse:
    return CategoryReadResponse.model_validate(
        await interactor(user.id, category_id, CategoryUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete(
    "/{category_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**_NOT_FOUND, **_READ_ONLY},
)
async def delete_category(
    user: CurrentUserDep, category_id: CategoryId, interactor: FromDishka[DeleteCategory]
) -> None:
    """Deleting a category also deletes all states recorded in it."""
    await interactor(user.id, category_id)
    track("category", "deleted")
