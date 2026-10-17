from typing import Protocol

from app.domain.categories.enums import CategoryKind
from app.domain.categories.ids import CategoryId
from app.domain.pets.ids import PetId
from app.domain.states.entity import State
from app.domain.states.ids import StateId
from app.domain.users.ids import UserId


class StateGateway(Protocol):
    async def get_by_id(self, id_: StateId, *, user_id: UserId | None = None) -> State | None: ...

    async def get_by_user_id(
        self,
        user_id: UserId,
        offset: int,
        limit: int,
        *,
        pet_id: PetId | None = None,
        cat_id: CategoryId | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> list[State]: ...

    async def count_by_user_id(
        self,
        user_id: UserId,
        *,
        pet_id: PetId | None = None,
        cat_id: CategoryId | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> int: ...

    async def aggregate(
        self, pet_id: PetId, cat_id: CategoryId, kind: CategoryKind, from_: float | None, to: float | None
    ) -> tuple[float | None, int]: ...

    async def count_by_category_of_others(self, cat_id: CategoryId, user_id: UserId) -> int:
        """States in the category recorded for pets that do not belong to the user."""
        ...
