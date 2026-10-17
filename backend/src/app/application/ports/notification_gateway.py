from typing import Protocol

from app.domain.events.ids import EventId
from app.domain.notifications.entity import Notification
from app.domain.notifications.enums import NotificationStatus
from app.domain.notifications.ids import NotificationId
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class NotificationGateway(Protocol):
    async def get_by_id(self, id_: NotificationId, *, user_id: UserId | None = None) -> Notification | None: ...

    async def get_by_user_id(
        self,
        user_id: UserId,
        now: float,
        offset: int,
        limit: int,
        *,
        event_id: EventId | None = None,
        pet_id: PetId | None = None,
        status: NotificationStatus | None = None,
        due: bool = False,
    ) -> list[Notification]: ...

    async def count_by_user_id(
        self,
        user_id: UserId,
        now: float,
        *,
        event_id: EventId | None = None,
        pet_id: PetId | None = None,
        status: NotificationStatus | None = None,
        due: bool = False,
    ) -> int: ...
