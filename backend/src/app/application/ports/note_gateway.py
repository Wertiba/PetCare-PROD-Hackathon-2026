from typing import Protocol

from app.domain.notes.entity import Note
from app.domain.notes.ids import NoteId
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class NoteGateway(Protocol):
    async def get_by_id(self, id_: NoteId, *, user_id: UserId | None = None) -> Note | None: ...

    async def get_by_user_id(
        self, user_id: UserId, offset: int, limit: int, *, pet_id: PetId | None = None, query: str | None = None
    ) -> list[Note]: ...

    async def count_by_user_id(
        self, user_id: UserId, *, pet_id: PetId | None = None, query: str | None = None
    ) -> int: ...
