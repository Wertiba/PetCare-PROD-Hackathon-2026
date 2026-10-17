from dataclasses import dataclass
from typing import Any

from app.domain.animals.ids import AnimalId
from app.domain.users.ids import UserId


@dataclass(kw_only=True)
class AnimalCreateData:
    name: str


@dataclass(kw_only=True)
class AnimalUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class AnimalResult:
    id: AnimalId
    name: str
    createdBy: UserId | None
    createdAt: float
