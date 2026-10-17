from dataclasses import dataclass, field
from uuid import uuid4

from app.domain.breeds.ids import BreedId
from app.domain.pets.enums import PetType


@dataclass(eq=False, kw_only=True)
class Breed:
    id: BreedId = field(default_factory=uuid4)
    type: PetType
    name: str
