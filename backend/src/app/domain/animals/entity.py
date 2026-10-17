from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.animals.ids import AnimalId
from app.domain.users.ids import UserId


@dataclass(eq=False, kw_only=True)
class Animal:
    id: AnimalId = field(default_factory=uuid4)
    name: str
    created_by: UserId | None = None
    created_at: float = field(default_factory=time)
