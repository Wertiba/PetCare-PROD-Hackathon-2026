from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.foods.ids import FoodId
from app.domain.pets.ids import PetId


@dataclass(eq=False, kw_only=True)
class Food:
    """One feeding: what the pet ate and how it went. None in an assessment means "not assessed yet"."""

    id: FoodId = field(default_factory=uuid4)
    pet_id: PetId
    name: str
    weight: int | None = None
    ingredients: list[str] = field(default_factory=list)
    is_approach: bool | None = None
    is_tolerability: bool | None = None
    consequences: str | None = None
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)
