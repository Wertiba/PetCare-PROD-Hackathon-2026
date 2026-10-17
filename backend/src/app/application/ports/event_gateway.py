from typing import Protocol

from app.domain.events.entity import Event
from app.domain.events.enums import EventStatus, EventType
from app.domain.events.ids import EventId
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class EventGateway(Protocol):
    async def get_by_id(self, id_: EventId, *, user_id: UserId | None = None) -> Event | None: ...

    async def get_by_user_id(
        self,
        user_id: UserId,
        offset: int,
        limit: int,
        *,
        pet_id: PetId | None = None,
        status: EventStatus | None = None,
        type_: EventType | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> list[Event]: ...

    async def count_by_user_id(
        self,
        user_id: UserId,
        *,
        pet_id: PetId | None = None,
        status: EventStatus | None = None,
        type_: EventType | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> int: ...

    async def get_upcoming(
        self, user_id: UserId, until: float, pet_id: PetId | None, offset: int, limit: int
    ) -> list[Event]: ...

    async def count_upcoming(self, user_id: UserId, until: float, pet_id: PetId | None) -> int: ...
