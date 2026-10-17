from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.categories.ids import CategoryId
from app.domain.pets.ids import PetId
from app.domain.states.ids import StateId


@dataclass(eq=False, kw_only=True)
class State:
    id: StateId = field(default_factory=uuid4)
    pet_id: PetId
    cat_id: CategoryId
    value: int
    note: str | None = None
    time: float
    created_at: float = field(default_factory=time)
