from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.refresh_tokens.ids import RefreshTokenId
from app.domain.users.entity import User
from app.domain.users.ids import UserId


@dataclass(eq=False, kw_only=True)
class RefreshToken:
    id: RefreshTokenId = field(default_factory=uuid4)
    user_id: UserId
    hashed_token: str
    expires_at: float
    created_at: float = field(default_factory=time)
    user: User | None = field(default=None, init=False, repr=False)
