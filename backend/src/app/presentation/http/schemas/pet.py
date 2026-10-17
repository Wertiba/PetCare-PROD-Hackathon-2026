from datetime import UTC, datetime
from typing import Annotated

from pydantic import Field, field_validator

from app.domain.breeds.ids import BreedId
from app.domain.pets.enums import PetType
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId
from app.presentation.http.schemas.base import PyModel


class PetBreedReadResponse(PyModel):
    id: BreedId
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
    def birth_date_not_future(cls, value: float | None) -> float | None:
        if value is None:
            return None
        try:
            birth_date = datetime.fromtimestamp(value, UTC).date()
        except (OverflowError, OSError, ValueError) as exc:
            raise ValueError("birthDate is outside the supported date range") from exc
        if birth_date > datetime.now(UTC).date():
            raise ValueError("birthDate must not be in the future")
        return datetime.combine(birth_date, datetime.min.time(), UTC).timestamp()


class PetCreateBody(_PetNameBirthValidation):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    type: PetType
    breedId: BreedId | None = None
    birthDate: float | None = Field(None, description="Birth date as Unix seconds at UTC midnight.")


class PetUpdateBody(_PetNameBirthValidation):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    type: PetType | None = None
    breedId: BreedId | None = None
    birthDate: float | None = Field(None, description="Birth date as Unix seconds at UTC midnight.")


class PetReadResponse(PyModel):
    id: PetId
    userId: UserId
    name: str
    type: PetType
    breed: PetBreedReadResponse | None
    birthDate: float | None = Field(description="Birth date as Unix seconds at UTC midnight.")
    ageMonths: int | None
    photoUrl: str | None
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    updatedAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
