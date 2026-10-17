from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.foods.dto import FoodCreateData, FoodUpdateData
from app.application.foods.interactors import (
    CreateFood,
    DeleteFood,
    FindSuspectIngredients,
    GetFood,
    ListFoods,
    UpdateFood,
)
from app.application.pagination import Pagination
from app.domain.foods.ids import FoodId
from app.domain.pets.ids import PetId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.food import FoodCreateBody, FoodReadResponse, FoodSuspectsResponse, FoodUpdateBody
from app.presentation.http.schemas.responses import ErrorResponse

router = APIRouter(prefix="/foods", tags=["Foods"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Food not found"}}
_UNPROCESSABLE = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Pet not found"}}


@router.get("", response_model=Page[FoodReadResponse], status_code=status.HTTP_200_OK)
async def list_foods(
    user: CurrentUserDep,
    interactor: FromDishka[ListFoods],
    pagination: PaginationDep,
    petId: PetId | None = Query(None),
    isApproach: bool | None = Query(None),
    isTolerability: bool | None = Query(None),
) -> Page[FoodReadResponse]:
    """Feeding journal, newest first."""
    return Page[FoodReadResponse].model_validate(
        await interactor(
            user.id,
            Pagination(page=pagination.page, size=pagination.size),
            pet_id=petId,
            is_approach=isApproach,
            is_tolerability=isTolerability,
        ),
        from_attributes=True,
    )


@router.post("", response_model=FoodReadResponse, status_code=status.HTTP_201_CREATED, responses=_UNPROCESSABLE)
async def create_food(
    user: CurrentUserDep, interactor: FromDishka[CreateFood], body: FoodCreateBody, response: Response
) -> FoodReadResponse:
    created = await interactor(user.id, FoodCreateData(**body.model_dump()))
    track("food", "created")
    response.headers["Location"] = f"/api/v1/foods/{created.id}"
    return FoodReadResponse.model_validate(created, from_attributes=True)


@router.get("/{food_id}", response_model=FoodReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_food(user: CurrentUserDep, food_id: FoodId, interactor: FromDishka[GetFood]) -> FoodReadResponse:
    return FoodReadResponse.model_validate(await interactor(user.id, food_id), from_attributes=True)


@router.patch("/{food_id}", response_model=FoodReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def update_food(
    user: CurrentUserDep, food_id: FoodId, interactor: FromDishka[UpdateFood], body: FoodUpdateBody
) -> FoodReadResponse:
    return FoodReadResponse.model_validate(
        await interactor(user.id, food_id, FoodUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete("/{food_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
async def delete_food(user: CurrentUserDep, food_id: FoodId, interactor: FromDishka[DeleteFood]) -> None:
    await interactor(user.id, food_id)
    track("food", "deleted")


@router.get(
    "/{food_id}/suspects",
    response_model=FoodSuspectsResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def find_suspect_ingredients(
    user: CurrentUserDep, food_id: FoodId, interactor: FromDishka[FindSuspectIngredients]
) -> FoodSuspectsResponse:
    """For a food the pet reacted badly to: its ingredients that none of the pet's earlier tolerated foods
    (isTolerability=true, fed before this one) contained. Without such foods every ingredient is a suspect."""
    return FoodSuspectsResponse.model_validate(await interactor(user.id, food_id), from_attributes=True)
