from typing import Annotated

from pydantic import Field, field_validator

from app.domain.animals.ids import AnimalId
from app.domain.users.ids import UserId
from app.presentation.http.schemas.base import PyModel, strip_required_text


class _AnimalNameValidation(PyModel):
    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def strip_name(cls, value: object) -> object:
        return strip_required_text(value)


class AnimalCreateBody(_AnimalNameValidation):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class AnimalUpdateBody(_AnimalNameValidation):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None


class AnimalReadResponse(PyModel):
    id: AnimalId
    name: str
    createdBy: UserId | None = Field(description="null for animals seeded by the migration")
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
