from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, field_validator

from app.core.enums import EventPeriod, EventStatus, EventType
from app.core.schemas.base import (
    PyModel,
    TimestampsResponse,
    UtcDatetime,
    strip_optional_text,
    strip_required_text,
)


class _EventTextValidation(PyModel):
    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def strip_name(cls, value: object) -> object:
        return strip_required_text(value)

    @field_validator("description", mode="before", check_fields=False)
    @classmethod
    def strip_description(cls, value: object) -> object:
        return strip_optional_text(value)


class EventCreateBody(_EventTextValidation):
    petId: UUID
    name: Annotated[str, Field(min_length=1, max_length=255)]
    type: EventType = EventType.OTHER
    status: EventStatus = EventStatus.PLANNED
    schedule: UtcDatetime
    period: EventPeriod = EventPeriod.NONE
    description: Annotated[str | None, Field(max_length=2000)] = None


class EventUpdateBody(_EventTextValidation):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    type: EventType | None = None
    status: EventStatus | None = None
    schedule: UtcDatetime | None = None
    period: EventPeriod | None = None
    description: Annotated[str | None, Field(max_length=2000)] = None

    @field_validator("type", "status", "schedule", "period", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


class EventCompleteBody(PyModel):
    doneAt: UtcDatetime | None = Field(None, description="When the procedure was actually done. Defaults to now")


class EventReadResponse(TimestampsResponse):
    id: UUID
    petId: UUID
    name: str
    type: EventType
    status: EventStatus
    schedule: datetime
    period: EventPeriod
    description: str | None
    doneAt: datetime | None
    isOverdue: bool = Field(description="Still planned, but the scheduled time has passed")
    nextSchedule: datetime | None = Field(description="When the next occurrence is due for a repeating event")
    createdAt: datetime
    updatedAt: datetime


class EventCompleteResponse(PyModel):
    event: EventReadResponse
    nextEvent: EventReadResponse | None


class EventFilterQuery(PyModel):
    petId: UUID | None = None
    status: EventStatus | None = None
    type: EventType | None = None
    from_: datetime | None = None
    to: datetime | None = None
