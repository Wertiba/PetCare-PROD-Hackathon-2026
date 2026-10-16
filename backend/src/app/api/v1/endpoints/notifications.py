from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.v1.dependencies import CurrentUserDep, NotificationFilterDep, NotificationServiceDep, PaginationDep
from app.core.schemas.notification import (
    NotificationCreateBody,
    NotificationReadResponse,
    NotificationUpdateBody,
)
from app.core.schemas.responses import ErrorResponse
from app.core.utils import Page

router = APIRouter(prefix="/notifications", tags=["Notifications"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Notification not found"}}


@router.get("", response_model=Page[NotificationReadResponse], status_code=status.HTTP_200_OK)
async def list_notifications(
    user: CurrentUserDep,
    notification_service: NotificationServiceDep,
    pagination: PaginationDep,
    filters: NotificationFilterDep,
) -> Page[NotificationReadResponse]:
    """Latest first. `due=true` gives what should be shown to the user right now."""
    return await notification_service.list_notifications(user.id, pagination, filters)


@router.post(
    "",
    response_model=NotificationReadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Event not found"},
    },
)
async def create_notification(
    user: CurrentUserDep,
    notification_service: NotificationServiceDep,
    body: NotificationCreateBody,
    response: Response,
) -> NotificationReadResponse:
    created = await notification_service.create_notification(user.id, body)
    response.headers["Location"] = f"/api/v1/notifications/{created.id}"
    return created


@router.get(
    "/{notification_id}",
    response_model=NotificationReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def get_notification(
    user: CurrentUserDep, notification_id: UUID, notification_service: NotificationServiceDep
) -> NotificationReadResponse:
    return await notification_service.get_notification(user.id, notification_id)


@router.patch(
    "/{notification_id}",
    response_model=NotificationReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def update_notification(
    user: CurrentUserDep,
    notification_id: UUID,
    notification_service: NotificationServiceDep,
    body: NotificationUpdateBody,
) -> NotificationReadResponse:
    return await notification_service.update_notification(user.id, notification_id, body)


@router.delete(
    "/{notification_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_NOT_FOUND,
)
async def delete_notification(
    user: CurrentUserDep, notification_id: UUID, notification_service: NotificationServiceDep
) -> None:
    await notification_service.delete_notification(user.id, notification_id)
