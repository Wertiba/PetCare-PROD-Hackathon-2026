from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, field_validator

from app.core.enums import CategoryKind, CategoryUnit
from app.core.schemas.base import PyModel, TimestampsResponse, UtcDatetime, strip_optional_text


class _StateNoteValidation(PyModel):
    @field_validator("note", mode="before", check_fields=False)
    @classmethod
    def strip_note(cls, value: object) -> object:
        return strip_optional_text(value)


class StateCreateBody(_StateNoteValidation):
    petId: UUID
    catId: UUID
    value: int
    time: UtcDatetime | None = Field(None, description="Defaults to now")
    note: Annotated[str | None, Field(max_length=1000)] = None


class StateUpdateBody(_StateNoteValidation):
    value: int | None = None
    time: UtcDatetime | None = None
    note: Annotated[str | None, Field(max_length=1000)] = None

    @field_validator("value", "time", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


class StateReadResponse(TimestampsResponse):
    id: UUID
    petId: UUID
    catId: UUID
    value: int
    note: str | None
    time: datetime
    createdAt: datetime


class StateFilterQuery(PyModel):
    petId: UUID | None = None
    catId: UUID | None = None
    from_: datetime | None = None
    to: datetime | None = None


class StateSummaryQuery(PyModel):
    petId: UUID
    catId: UUID
    from_: datetime | None = None
    to: datetime | None = None


class StateSummaryResponse(TimestampsResponse):
    petId: UUID
    catId: UUID
    kind: CategoryKind
    unit: CategoryUnit
    value: float | None = Field(description="Aggregated by the category kind; null when there are no states")
    count: int
    from_: datetime | None = Field(serialization_alias="from")
    to: datetime | None
