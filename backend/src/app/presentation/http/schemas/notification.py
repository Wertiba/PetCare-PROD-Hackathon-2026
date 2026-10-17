from typing import Annotated

from pydantic import AfterValidator, Field, field_validator

from app.domain.events.ids import EventId
from app.domain.notifications.enums import NotificationStatus, NotificationType
from app.domain.notifications.ids import NotificationId
from app.domain.pets.ids import PetId
from app.presentation.http.schemas.base import PyModel, validate_timestamp


class NotificationCreateBody(PyModel):
    eventId: EventId
    type: NotificationType = NotificationType.APP
    status: NotificationStatus = NotificationStatus.PENDING
    time: Annotated[float, AfterValidator(validate_timestamp)] | None = Field(
        None, description="Defaults to the event schedule. Unix seconds in UTC; fractional seconds are supported."
    )


class NotificationUpdateBody(PyModel):
    type: NotificationType | None = None
    status: NotificationStatus | None = None
    time: Annotated[float, AfterValidator(validate_timestamp)] | None = Field(
        None, description="Unix seconds in UTC; fractional seconds are supported."
    )

    @field_validator("type", "status", "time", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


class NotificationReadResponse(PyModel):
    id: NotificationId
    eventId: EventId
    petId: PetId
    eventName: str
    type: NotificationType
    status: NotificationStatus
    time: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
