from time import time
from typing import Annotated

from pydantic import AfterValidator, Field, field_validator

from app.domain.events.enums import EventPeriod, EventStatus, EventType
from app.domain.events.ids import EventId
from app.domain.pets.ids import PetId
from app.presentation.http.schemas.base import (
    PyModel,
    strip_optional_text,
    strip_required_text,
    validate_timestamp,
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
    petId: PetId
    name: Annotated[str, Field(min_length=1, max_length=255)]
    type: EventType = EventType.OTHER
    status: EventStatus = EventStatus.PLANNED
    schedule: Annotated[float, AfterValidator(validate_timestamp)] = Field(
        description="Unix seconds in UTC; fractional seconds are supported."
    )
    period: EventPeriod = EventPeriod.NONE
    description: Annotated[str | None, Field(max_length=2000)] = None


class EventUpdateBody(_EventTextValidation):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    type: EventType | None = None
    status: EventStatus | None = None
    schedule: Annotated[float, AfterValidator(validate_timestamp)] | None = Field(
        None, description="Unix seconds in UTC; fractional seconds are supported."
    )
    period: EventPeriod | None = None
    description: Annotated[str | None, Field(max_length=2000)] = None

    @field_validator("type", "status", "schedule", "period", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


# Room for a client clock running ahead; a day keeps any time zone mix-up of "today" acceptable.
_DONE_AT_SKEW = 24 * 60 * 60


class EventCompleteBody(PyModel):
    doneAt: Annotated[float, AfterValidator(validate_timestamp)] | None = Field(
        None,
        description="Actual completion time in fractional Unix seconds (UTC); defaults to now. Not in the future.",
    )

    @field_validator("doneAt")
    @classmethod
    def done_not_in_future(cls, value: float | None) -> float | None:
        # A future completion date would also push the next occurrence of a repeating event out by that much.
        if value is not None and value > time() + _DONE_AT_SKEW:
            raise ValueError("doneAt must not be in the future")
        return value


class EventReadResponse(PyModel):
    id: EventId
    petId: PetId
    name: str
    type: EventType
    status: EventStatus
    schedule: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    period: EventPeriod
    description: str | None
    doneAt: float | None = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    isOverdue: bool = Field(description="Still planned, but the scheduled time has passed")
    nextSchedule: float | None = Field(
        description="Next occurrence in fractional Unix seconds (UTC), for a repeating event."
    )
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    updatedAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")


class EventCompleteResponse(PyModel):
    event: EventReadResponse
    nextEvent: EventReadResponse | None
