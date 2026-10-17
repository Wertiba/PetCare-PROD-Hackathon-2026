from dataclasses import dataclass
from typing import Any

from app.domain.categories.enums import CategoryKind, CategoryUnit
from app.domain.categories.ids import CategoryId
from app.domain.pets.ids import PetId
from app.domain.states.ids import StateId


@dataclass(kw_only=True)
class StateCreateData:
    petId: PetId
    catId: CategoryId
    value: int
    time: float | None = None
    note: str | None = None


@dataclass(kw_only=True)
class StateUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class StateResult:
    id: StateId
    petId: PetId
    catId: CategoryId
    value: int
    note: str | None
    time: float
    createdAt: float


@dataclass(kw_only=True)
class StateSummaryResult:
    petId: PetId
    catId: CategoryId
    kind: CategoryKind
    unit: CategoryUnit
    value: float | None
    count: int
    from_: float | None
    to: float | None
