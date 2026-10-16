from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.v1.dependencies import CurrentUserDep, EventFilterDep, EventServiceDep, PaginationDep
from app.core.schemas.event import (
    EventCompleteBody,
    EventCompleteResponse,
    EventCreateBody,
    EventReadResponse,
    EventUpdateBody,
)
from app.core.schemas.responses import ErrorResponse
from app.core.utils import Page

router = APIRouter(prefix="/events", tags=["Events"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Event not found"}}
_PET_MISSING = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Pet not found"},
}


@router.get("", response_model=Page[EventReadResponse], status_code=status.HTTP_200_OK)
async def list_events(
    user: CurrentUserDep,
    event_service: EventServiceDep,
    pagination: PaginationDep,
    filters: EventFilterDep,
) -> Page[EventReadResponse]:
    """All events, latest schedule first. Health map: filter by `petId` and `type`."""
    return await event_service.list_events(user.id, pagination, filters)


@router.get("/upcoming", response_model=Page[EventReadResponse], status_code=status.HTTP_200_OK)
async def list_upcoming_events(
    user: CurrentUserDep,
    event_service: EventServiceDep,
    pagination: PaginationDep,
    days: int = Query(30, ge=1, le=366, description="How far ahead to look"),
    petId: UUID | None = Query(None),
) -> Page[EventReadResponse]:
    """Planned events due within `days`, overdue ones included, nearest first."""
    return await event_service.list_upcoming(user.id, pagination, days, petId)


@router.post(
    "",
    response_model=EventReadResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_PET_MISSING,
)
async def create_event(
    user: CurrentUserDep,
    event_service: EventServiceDep,
    body: EventCreateBody,
    response: Response,
) -> EventReadResponse:
    created = await event_service.create_event(user.id, body)
    response.headers["Location"] = f"/api/v1/events/{created.id}"
    return created


@router.get(
    "/{event_id}",
    response_model=EventReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def get_event(user: CurrentUserDep, event_id: UUID, event_service: EventServiceDep) -> EventReadResponse:
    return await event_service.get_event(user.id, event_id)


@router.patch(
    "/{event_id}",
    response_model=EventReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def update_event(
    user: CurrentUserDep,
    event_id: UUID,
    event_service: EventServiceDep,
    body: EventUpdateBody,
) -> EventReadResponse:
    """Setting `status` from planned to done plans the next occurrence of a repeating event."""
    return await event_service.update_event(user.id, event_id, body)


@router.post(
    "/{event_id}/complete",
    response_model=EventCompleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        **_NOT_FOUND,
        status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Event is not planned"},
    },
)
async def complete_event(
    user: CurrentUserDep,
    event_id: UUID,
    event_service: EventServiceDep,
    body: EventCompleteBody | None = None,
) -> EventCompleteResponse:
    """Mark done and, for a repeating event, plan the next one. Returns both."""
    return await event_service.complete_event(user.id, event_id, body.doneAt if body else None)


@router.delete(
    "/{event_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_NOT_FOUND,
)
async def delete_event(user: CurrentUserDep, event_id: UUID, event_service: EventServiceDep) -> None:
    await event_service.delete_event(user.id, event_id)
