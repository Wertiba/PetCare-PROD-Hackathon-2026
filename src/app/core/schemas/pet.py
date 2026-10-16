from datetime import UTC, date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, field_validator

from app.core.enums import PetType
from app.core.schemas.base import DatetimeResponse, PyModel


class PetBreedReadResponse(PyModel):
    id: UUID
    name: str


class _PetNameBirthValidation(PyModel):
    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def strip_name(cls, value: object) -> object:
        if value is None:
            raise ValueError("name cannot be null")
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("birthDate", check_fields=False)
    @classmethod
    def birth_date_not_future(cls, value: date | None) -> date | None:
        if value is not None and value > datetime.now(UTC).date():
            raise ValueError("birthDate must not be in the future")
        return value


class PetCreateBody(_PetNameBirthValidation):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    type: PetType
    breedId: UUID | None = None
    birthDate: date | None = None


class PetUpdateBody(_PetNameBirthValidation):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    type: PetType | None = None
    breedId: UUID | None = None
    birthDate: date | None = None


class PetReadResponse(DatetimeResponse):
    id: UUID
    userId: UUID
    name: str
    type: PetType
    breed: PetBreedReadResponse | None
    birthDate: date | None
    ageMonths: int | None
    photoUrl: str | None
    createdAt: datetime
    updatedAt: datetime
