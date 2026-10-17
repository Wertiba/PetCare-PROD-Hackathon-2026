from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.pagination import Pagination
from app.application.states.dto import StateCreateData, StateUpdateData
from app.application.states.interactors import (
    CreateState,
    DeleteState,
    GetState,
    ListStates,
    SummarizeStates,
    UpdateState,
)
from app.domain.categories.ids import CategoryId
from app.domain.pets.ids import PetId
from app.domain.states.ids import StateId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.responses import ErrorResponse
from app.presentation.http.schemas.state import (
    StateCreateBody,
    StateReadResponse,
    StateSummaryResponse,
    StateUpdateBody,
)

router = APIRouter(prefix="/states", tags=["States"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "State not found"}}
_UNPROCESSABLE = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "model": ErrorResponse,
        "description": "Pet or category is missing, or the value does not fit the category type",
    }
}


@router.get("", response_model=Page[StateReadResponse], status_code=status.HTTP_200_OK)
async def list_states(
    user: CurrentUserDep,
    interactor: FromDishka[ListStates],
    pagination: PaginationDep,
    petId: PetId | None = Query(None),
    categoryId: CategoryId | None = Query(None),
    from_: float | None = Query(None, alias="from", description="Inclusive lower bound of `time`", allow_inf_nan=False),
    to: float | None = Query(None, description="Inclusive upper bound of `time`", allow_inf_nan=False),
) -> Page[StateReadResponse]:
    """Newest first."""
    return Page[StateReadResponse].model_validate(
        await interactor(
            user.id,
            Pagination(page=pagination.page, size=pagination.size),
            pet_id=petId,
            category_id=categoryId,
            from_=from_,
            to=to,
        ),
        from_attributes=True,
    )


@router.get("/summary", response_model=StateSummaryResponse, status_code=status.HTTP_200_OK, responses=_UNPROCESSABLE)
async def summarize_states(
    user: CurrentUserDep,
    interactor: FromDishka[SummarizeStates],
    petId: PetId = Query(...),
    categoryId: CategoryId = Query(...),
    from_: float | None = Query(None, alias="from", description="Inclusive lower bound of `time`", allow_inf_nan=False),
    to: float | None = Query(None, description="Inclusive upper bound of `time`", allow_inf_nan=False),
) -> StateSummaryResponse:
    """Aggregate of one category for one pet over a period, computed by the category `kind`."""
    return StateSummaryResponse.model_validate(
        await interactor(user.id, pet_id=petId, category_id=categoryId, from_=from_, to=to), from_attributes=True
    )


@router.post("", response_model=StateReadResponse, status_code=status.HTTP_201_CREATED, responses=_UNPROCESSABLE)
async def create_state(
    user: CurrentUserDep, interactor: FromDishka[CreateState], body: StateCreateBody, response: Response
) -> StateReadResponse:
    created = await interactor(user.id, StateCreateData(**body.model_dump()))
    track("state", "created")
    response.headers["Location"] = f"/api/v1/states/{created.id}"
    return StateReadResponse.model_validate(created, from_attributes=True)


@router.get("/{state_id}", response_model=StateReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_state(user: CurrentUserDep, state_id: StateId, interactor: FromDishka[GetState]) -> StateReadResponse:
    return StateReadResponse.model_validate(await interactor(user.id, state_id), from_attributes=True)


@router.patch(
    "/{state_id}",
    response_model=StateReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_UNPROCESSABLE},
)
async def update_state(
    user: CurrentUserDep, state_id: StateId, interactor: FromDishka[UpdateState], body: StateUpdateBody
) -> StateReadResponse:
    return StateReadResponse.model_validate(
        await interactor(user.id, state_id, StateUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete("/{state_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
async def delete_state(user: CurrentUserDep, state_id: StateId, interactor: FromDishka[DeleteState]) -> None:
    await interactor(user.id, state_id)
    track("state", "deleted")
