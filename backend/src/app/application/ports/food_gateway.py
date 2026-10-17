from typing import Protocol

from app.domain.foods.entity import Food
from app.domain.foods.ids import FoodId
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class FoodGateway(Protocol):
    async def get_by_id(self, id_: FoodId, *, user_id: UserId | None = None) -> Food | None: ...

    async def get_by_user_id(
        self,
        user_id: UserId,
        offset: int,
        limit: int,
        *,
        pet_id: PetId | None = None,
        is_approach: bool | None = None,
        is_tolerability: bool | None = None,
    ) -> list[Food]: ...

    async def count_by_user_id(
        self,
        user_id: UserId,
        *,
        pet_id: PetId | None = None,
        is_approach: bool | None = None,
        is_tolerability: bool | None = None,
    ) -> int: ...

    async def get_tolerated_before(self, pet_id: PetId, before: float, *, exclude_id: FoodId) -> list[Food]:
        """Foods of the pet marked as tolerated and fed before the given moment."""
        ...
