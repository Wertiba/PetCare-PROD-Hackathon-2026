from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.animals.entity import Animal
from app.domain.animals.ids import AnimalId
from app.domain.breeds.ids import BreedId
from app.domain.users.ids import UserId


@dataclass(eq=False, kw_only=True)
class Breed:
    id: BreedId = field(default_factory=uuid4)
    animal_id: AnimalId
    name: str
    created_by: UserId | None = None
    created_at: float = field(default_factory=time)
    animal: Animal | None = None
