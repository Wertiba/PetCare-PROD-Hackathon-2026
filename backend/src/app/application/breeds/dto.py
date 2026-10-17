from dataclasses import dataclass
from typing import Any

from app.domain.animals.ids import AnimalId
from app.domain.breeds.ids import BreedId
from app.domain.users.ids import UserId


@dataclass(kw_only=True)
class BreedCreateData:
    animalId: AnimalId
    name: str


@dataclass(kw_only=True)
class BreedUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class BreedResult:
    id: BreedId
    animalId: AnimalId
    name: str
    createdBy: UserId | None
    createdAt: float
