from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.breeds.entity import Breed
from app.domain.breeds.ids import BreedId
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


@dataclass(eq=False, kw_only=True)
class Pet:
    """The pet's animal is its breed's animal; breed_id is None only after an admin deleted the breed."""

    id: PetId = field(default_factory=uuid4)
    user_id: UserId
    breed_id: BreedId | None = None
    name: str
    birth_date: float | None = None
    photo_url: str | None = None
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)
    breed: Breed | None = None
