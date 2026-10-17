from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.users.enums import UserRole
from app.domain.users.ids import UserId


@dataclass(eq=False, kw_only=True)
class User:
    id: UserId = field(default_factory=uuid4)
    login: str
    password: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_by: UserId | None = None
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)
