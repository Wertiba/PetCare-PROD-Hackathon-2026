from dataclasses import dataclass
from typing import Any

from app.domain.breeds.ids import BreedId
from app.domain.pets.enums import PetType
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


@dataclass(kw_only=True)
class PetBreedResult:
    id: BreedId
    name: str


@dataclass(kw_only=True)
class PetCreateData:
    name: str
    type: PetType
    breedId: BreedId | None = None
    birthDate: float | None = None


@dataclass(kw_only=True)
class PetUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class PetResult:
    id: PetId
    userId: UserId
    name: str
    type: PetType
    breed: PetBreedResult | None
    birthDate: float | None
    ageMonths: int | None
    photoUrl: str | None
    createdAt: float
    updatedAt: float
