from dataclasses import dataclass, field
from typing import Any

from app.domain.foods.ids import FoodId
from app.domain.pets.ids import PetId


@dataclass(kw_only=True)
class FoodCreateData:
    petId: PetId
    name: str
    weight: int | None = None
    ingredients: list[str] = field(default_factory=list)
    isApproach: bool | None = None
    isTolerability: bool | None = None
    consequences: str | None = None


@dataclass(kw_only=True)
class FoodUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class FoodResult:
    id: FoodId
    petId: PetId
    name: str
    weight: int | None
    ingredients: list[str]
    isApproach: bool | None
    isTolerability: bool | None
    consequences: str | None
    createdAt: float
    updatedAt: float


@dataclass(kw_only=True)
class FoodSuspectsResult:
    foodId: FoodId
    petId: PetId
    suspects: list[str]
    comparedFoods: int
