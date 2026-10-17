from typing import Protocol

from app.domain.users.entity import User
from app.domain.users.ids import UserId


class UserGateway(Protocol):
    async def get_by_id(self, id_: UserId) -> User | None: ...

    async def get_by_login(self, login: str) -> User | None: ...
