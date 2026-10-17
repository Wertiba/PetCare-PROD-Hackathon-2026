from typing import Annotated

from pydantic import Field, field_validator

from app.domain.animals.ids import AnimalId
from app.domain.breeds.ids import BreedId
from app.domain.users.ids import UserId
from app.presentation.http.schemas.base import PyModel, strip_required_text


class _BreedValidation(PyModel):
    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def strip_name(cls, value: object) -> object:
        return strip_required_text(value)

    @field_validator("animalId", mode="before", check_fields=False)
    @classmethod
    def animal_not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("animalId cannot be null")
        return value


class BreedCreateBody(_BreedValidation):
    animalId: AnimalId
    name: Annotated[str, Field(min_length=1, max_length=100)]


class BreedUpdateBody(_BreedValidation):
    animalId: AnimalId | None = None
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None


class BreedReadResponse(PyModel):
    id: BreedId
    animalId: AnimalId
    name: str
    createdBy: UserId | None = Field(description="null for breeds seeded by the migration")
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
