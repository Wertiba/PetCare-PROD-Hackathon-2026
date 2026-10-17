from dataclasses import dataclass
from typing import Any

from app.domain.animals.ids import AnimalId
from app.domain.breeds.ids import BreedId
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


@dataclass(kw_only=True)
class PetAnimalResult:
    id: AnimalId
    name: str


@dataclass(kw_only=True)
class PetBreedResult:
    id: BreedId
    name: str


@dataclass(kw_only=True)
class PetCreateData:
    name: str
    breedId: BreedId
    birthDate: float | None = None


@dataclass(kw_only=True)
class PetUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class PetResult:
    id: PetId
    userId: UserId
    name: str
    animal: PetAnimalResult | None
    breed: PetBreedResult | None
    birthDate: float | None
    ageMonths: int | None
    photoUrl: str | None
    createdAt: float
    updatedAt: float
