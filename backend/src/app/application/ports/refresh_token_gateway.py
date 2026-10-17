from typing import Protocol

from app.domain.refresh_tokens.entity import RefreshToken
from app.domain.refresh_tokens.ids import RefreshTokenId
from app.domain.users.ids import UserId


class RefreshTokenGateway(Protocol):
    async def get_by_id(self, id_: RefreshTokenId) -> RefreshToken | None: ...

    async def get_by_user_and_hash(self, user_id: UserId, hashed_token: str) -> RefreshToken | None: ...

    async def get_by_hash(self, hashed_token: str) -> RefreshToken | None: ...
