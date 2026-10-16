from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.v1.dependencies import (
    CurrentUserDep,
    PaginationDep,
    StateFilterDep,
    StateServiceDep,
    StateSummaryDep,
)
from app.core.schemas.responses import ErrorResponse
from app.core.schemas.state import StateCreateBody, StateReadResponse, StateSummaryResponse, StateUpdateBody
from app.core.utils import Page

router = APIRouter(prefix="/states", tags=["States"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "State not found"}}
_UNPROCESSABLE = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "model": ErrorResponse,
        "description": "Pet or category is missing, or the value does not fit the category type",
    },
}


@router.get("", response_model=Page[StateReadResponse], status_code=status.HTTP_200_OK)
async def list_states(
    user: CurrentUserDep,
    state_service: StateServiceDep,
    pagination: PaginationDep,
    filters: StateFilterDep,
) -> Page[StateReadResponse]:
    """Newest first."""
    return await state_service.list_states(user.id, pagination, filters)


@router.get(
    "/summary",
    response_model=StateSummaryResponse,
    status_code=status.HTTP_200_OK,
    responses=_UNPROCESSABLE,
)
async def summarize_states(
    user: CurrentUserDep,
    state_service: StateServiceDep,
    query: StateSummaryDep,
) -> StateSummaryResponse:
    """Aggregate of one category for one pet over a period, computed by the category `kind`."""
    return await state_service.summarize(user.id, query)


@router.post(
    "",
    response_model=StateReadResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_UNPROCESSABLE,
)
async def create_state(
    user: CurrentUserDep,
    state_service: StateServiceDep,
    body: StateCreateBody,
    response: Response,
) -> StateReadResponse:
    created = await state_service.create_state(user.id, body)
    response.headers["Location"] = f"/api/v1/states/{created.id}"
    return created


@router.get(
    "/{state_id}",
    response_model=StateReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def get_state(user: CurrentUserDep, state_id: UUID, state_service: StateServiceDep) -> StateReadResponse:
    return await state_service.get_state(user.id, state_id)


@router.patch(
    "/{state_id}",
    response_model=StateReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_UNPROCESSABLE},
)
async def update_state(
    user: CurrentUserDep,
    state_id: UUID,
    state_service: StateServiceDep,
    body: StateUpdateBody,
) -> StateReadResponse:
    return await state_service.update_state(user.id, state_id, body)


@router.delete(
    "/{state_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_NOT_FOUND,
)
async def delete_state(user: CurrentUserDep, state_id: UUID, state_service: StateServiceDep) -> None:
    await state_service.delete_state(user.id, state_id)
