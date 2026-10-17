from collections.abc import Sequence
from typing import Protocol

from app.domain.pets.entity import Pet
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class PetGateway(Protocol):
    async def get_by_id(self, id_: PetId, *, user_id: UserId | None = None) -> Pet | None: ...

    async def get_by_ids(self, user_id: UserId, ids: Sequence[PetId]) -> list[Pet]: ...

    async def get_by_user_id(self, user_id: UserId, offset: int, limit: int) -> list[Pet]: ...

    async def count_by_user_id(self, user_id: UserId) -> int: ...
