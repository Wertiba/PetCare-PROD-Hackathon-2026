from dataclasses import dataclass
from typing import Any

from app.domain.categories.enums import CategoryKind, CategoryType, CategoryUnit
from app.domain.categories.ids import CategoryId
from app.domain.users.ids import UserId


@dataclass(kw_only=True)
class CategoryCreateData:
    name: str
    kind: CategoryKind
    type: CategoryType
    unit: CategoryUnit = CategoryUnit.NONE


@dataclass(kw_only=True)
class CategoryUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class CategoryResult:
    id: CategoryId
    name: str
    kind: CategoryKind
    type: CategoryType
    unit: CategoryUnit
    createdBy: UserId | None
    isSystem: bool
    createdAt: float
