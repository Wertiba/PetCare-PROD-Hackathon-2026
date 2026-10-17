from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.notifications.dto import NotificationCreateData, NotificationUpdateData
from app.application.notifications.interactors import (
    CreateNotification,
    DeleteNotification,
    GetNotification,
    ListNotifications,
    UpdateNotification,
)
from app.application.pagination import Pagination
from app.domain.events.ids import EventId
from app.domain.notifications.enums import NotificationStatus
from app.domain.notifications.ids import NotificationId
from app.domain.pets.ids import PetId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.notification import (
    NotificationCreateBody,
    NotificationReadResponse,
    NotificationUpdateBody,
)
from app.presentation.http.schemas.responses import ErrorResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Notification not found"}}


@router.get("", response_model=Page[NotificationReadResponse], status_code=status.HTTP_200_OK)
async def list_notifications(
    user: CurrentUserDep,
    interactor: FromDishka[ListNotifications],
    pagination: PaginationDep,
    eventId: EventId | None = Query(None),
    petId: PetId | None = Query(None),
    status: NotificationStatus | None = Query(None),
    due: bool = Query(False, description="Only pending notifications whose time has come"),
) -> Page[NotificationReadResponse]:
    """Latest first. `due=true` gives what should be shown to the user right now."""
    return Page[NotificationReadResponse].model_validate(
        await interactor(
            user.id,
            Pagination(page=pagination.page, size=pagination.size),
            event_id=eventId,
            pet_id=petId,
            status=status,
            due=due,
        ),
        from_attributes=True,
    )


@router.post(
    "",
    response_model=NotificationReadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Event not found"}},
)
async def create_notification(
    user: CurrentUserDep, interactor: FromDishka[CreateNotification], body: NotificationCreateBody, response: Response
) -> NotificationReadResponse:
    created = await interactor(user.id, NotificationCreateData(**body.model_dump()))
    track("notification", "created")
    response.headers["Location"] = f"/api/v1/notifications/{created.id}"
    return NotificationReadResponse.model_validate(created, from_attributes=True)


@router.get(
    "/{notification_id}", response_model=NotificationReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND
)
async def get_notification(
    user: CurrentUserDep, notification_id: NotificationId, interactor: FromDishka[GetNotification]
) -> NotificationReadResponse:
    return NotificationReadResponse.model_validate(await interactor(user.id, notification_id), from_attributes=True)


@router.patch(
    "/{notification_id}", response_model=NotificationReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND
)
async def update_notification(
    user: CurrentUserDep,
    notification_id: NotificationId,
    interactor: FromDishka[UpdateNotification],
    body: NotificationUpdateBody,
) -> NotificationReadResponse:
    return NotificationReadResponse.model_validate(
        await interactor(user.id, notification_id, NotificationUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete("/{notification_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
async def delete_notification(
    user: CurrentUserDep, notification_id: NotificationId, interactor: FromDishka[DeleteNotification]
) -> None:
    await interactor(user.id, notification_id)
    track("notification", "deleted")
