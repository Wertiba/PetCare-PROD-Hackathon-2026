from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.categories.enums import CategoryKind, CategoryType, CategoryUnit
from app.domain.categories.ids import CategoryId
from app.domain.users.ids import UserId


@dataclass(eq=False, kw_only=True)
class Category:
    id: CategoryId = field(default_factory=uuid4)
    name: str
    kind: CategoryKind
    type: CategoryType
    unit: CategoryUnit
    created_by: UserId | None = None
    created_at: float = field(default_factory=time)
