from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.core.enums import NotificationStatus, NotificationType
from app.core.schemas.base import PyModel, TimestampsResponse, UtcDatetime


class NotificationCreateBody(PyModel):
    eventId: UUID
    type: NotificationType = NotificationType.APP
    status: NotificationStatus = NotificationStatus.PENDING
    time: UtcDatetime | None = Field(None, description="Defaults to the event schedule")


class NotificationUpdateBody(PyModel):
    type: NotificationType | None = None
    status: NotificationStatus | None = None
    time: UtcDatetime | None = None

    @field_validator("type", "status", "time", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


class NotificationReadResponse(TimestampsResponse):
    id: UUID
    eventId: UUID
    petId: UUID
    eventName: str
    type: NotificationType
    status: NotificationStatus
    time: datetime
    createdAt: datetime


class NotificationFilterQuery(PyModel):
    eventId: UUID | None = None
    petId: UUID | None = None
    status: NotificationStatus | None = None
    due: bool = False
