from typing import Annotated

from pydantic import Field, field_validator

from app.domain.categories.enums import CategoryKind, CategoryUnit
from app.domain.categories.ids import CategoryId
from app.domain.pets.ids import PetId
from app.domain.states.ids import StateId
from app.presentation.http.schemas.base import PyModel, strip_optional_text


class _StateNoteValidation(PyModel):
    @field_validator("note", mode="before", check_fields=False)
    @classmethod
    def strip_note(cls, value: object) -> object:
        return strip_optional_text(value)


class StateCreateBody(_StateNoteValidation):
    petId: PetId
    categoryId: CategoryId
    value: int
    time: float | None = Field(
        None, description="Defaults to now. Unix seconds in UTC; fractional seconds are supported."
    )
    note: Annotated[str | None, Field(max_length=1000)] = None


class StateUpdateBody(_StateNoteValidation):
    value: int | None = None
    time: float | None = Field(None, description="Unix seconds in UTC; fractional seconds are supported.")
    note: Annotated[str | None, Field(max_length=1000)] = None

    @field_validator("value", "time", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("value cannot be null")
        return value


class StateReadResponse(PyModel):
    id: StateId
    petId: PetId
    categoryId: CategoryId
    value: int
    note: str | None
    time: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")


class StateSummaryResponse(PyModel):
    petId: PetId
    categoryId: CategoryId
    kind: CategoryKind
    unit: CategoryUnit
    value: float | None = Field(description="Aggregated by the category kind; null when there are no states")
    count: int
    from_: float | None = Field(
        serialization_alias="from", description="Unix seconds in UTC; fractional seconds are supported."
    )
    to: float | None = Field(description="Unix seconds in UTC; fractional seconds are supported.")
