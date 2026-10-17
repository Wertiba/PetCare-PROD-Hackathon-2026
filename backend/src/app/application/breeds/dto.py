from dataclasses import dataclass

from app.domain.breeds.ids import BreedId
from app.domain.pets.enums import PetType


@dataclass(kw_only=True)
class BreedResult:
    id: BreedId
    type: PetType
    name: str
