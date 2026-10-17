from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.events.dto import EventCreateData, EventUpdateData
from app.application.events.interactors import (
    CompleteEvent,
    CreateEvent,
    DeleteEvent,
    GetEvent,
    ListEvents,
    ListUpcomingEvents,
    UpdateEvent,
)
from app.application.pagination import Pagination
from app.domain.events.enums import EventStatus, EventType
from app.domain.events.ids import EventId
from app.domain.pets.ids import PetId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.event import (
    EventCompleteBody,
    EventCompleteResponse,
    EventCreateBody,
    EventReadResponse,
    EventUpdateBody,
)
from app.presentation.http.schemas.responses import ErrorResponse

router = APIRouter(prefix="/events", tags=["Events"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Event not found"}}
_PET_MISSING = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Pet not found"}}


@router.get("", response_model=Page[EventReadResponse], status_code=status.HTTP_200_OK)
async def list_events(
    user: CurrentUserDep,
    interactor: FromDishka[ListEvents],
    pagination: PaginationDep,
    petId: PetId | None = Query(None),
    status: EventStatus | None = Query(None),
    type: EventType | None = Query(None),
    from_: float | None = Query(
        None, alias="from", description="Inclusive lower bound of `schedule`", allow_inf_nan=False
    ),
    to: float | None = Query(None, description="Inclusive upper bound of `schedule`", allow_inf_nan=False),
) -> Page[EventReadResponse]:
    """All events, latest schedule first. Health map: filter by `petId` and `type`."""
    return Page[EventReadResponse].model_validate(
        await interactor(
            user.id,
            Pagination(page=pagination.page, size=pagination.size),
            pet_id=petId,
            status=status,
            type_=type,
            from_=from_,
            to=to,
        ),
        from_attributes=True,
    )


@router.get("/upcoming", response_model=Page[EventReadResponse], status_code=status.HTTP_200_OK)
async def list_upcoming_events(
    user: CurrentUserDep,
    interactor: FromDishka[ListUpcomingEvents],
    pagination: PaginationDep,
    days: int = Query(30, ge=1, le=366, description="How far ahead to look"),
    petId: PetId | None = Query(None),
) -> Page[EventReadResponse]:
    """Planned events due within `days`, overdue ones included, nearest first."""
    return Page[EventReadResponse].model_validate(
        await interactor(user.id, Pagination(page=pagination.page, size=pagination.size), days, petId),
        from_attributes=True,
    )


@router.post("", response_model=EventReadResponse, status_code=status.HTTP_201_CREATED, responses=_PET_MISSING)
async def create_event(
    user: CurrentUserDep, interactor: FromDishka[CreateEvent], body: EventCreateBody, response: Response
) -> EventReadResponse:
    created = await interactor(user.id, EventCreateData(**body.model_dump()))
    track("event", "created")
    response.headers["Location"] = f"/api/v1/events/{created.id}"
    return EventReadResponse.model_validate(created, from_attributes=True)


@router.get("/{event_id}", response_model=EventReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_event(user: CurrentUserDep, event_id: EventId, interactor: FromDishka[GetEvent]) -> EventReadResponse:
    return EventReadResponse.model_validate(await interactor(user.id, event_id), from_attributes=True)


@router.patch("/{event_id}", response_model=EventReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def update_event(
    user: CurrentUserDep,
    event_id: EventId,
    interactor: FromDishka[UpdateEvent],
    body: EventUpdateBody,
    get_event: FromDishka[GetEvent],
) -> EventReadResponse:
    """Setting `status` from planned to done plans the next occurrence of a repeating event."""
    previous = await get_event(user.id, event_id) if body.status == EventStatus.DONE else None
    result = await interactor(user.id, event_id, EventUpdateData(changes=body.model_dump(exclude_unset=True)))
    if previous is not None and previous.status == EventStatus.PLANNED:
        track("event", "completed")
        if result.nextSchedule is not None:
            track("event", "auto_planned")
    return EventReadResponse.model_validate(result, from_attributes=True)


@router.post(
    "/{event_id}/complete",
    response_model=EventCompleteResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Event is not planned"}},
)
async def complete_event(
    user: CurrentUserDep,
    event_id: EventId,
    interactor: FromDishka[CompleteEvent],
    body: EventCompleteBody | None = None,
) -> EventCompleteResponse:
    """Mark done and, for a repeating event, plan the next one. Returns both."""
    result = await interactor(user.id, event_id, body.doneAt if body else None)
    track("event", "completed")
    if result.nextEvent is not None:
        track("event", "auto_planned")
    return EventCompleteResponse.model_validate(result, from_attributes=True)


@router.delete("/{event_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
async def delete_event(user: CurrentUserDep, event_id: EventId, interactor: FromDishka[DeleteEvent]) -> None:
    await interactor(user.id, event_id)
    track("event", "deleted")
