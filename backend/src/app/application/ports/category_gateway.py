from typing import Protocol

from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryType
from app.domain.categories.ids import CategoryId
from app.domain.users.ids import UserId


class CategoryGateway(Protocol):
    async def get_by_id(self, id_: CategoryId, *, user_id: UserId | None = None) -> Category | None: ...

    async def get_by_user_id(
        self, user_id: UserId, offset: int, limit: int, *, type_: CategoryType | None = None, name: str | None = None
    ) -> list[Category]: ...

    async def count_by_user_id(
        self, user_id: UserId, *, type_: CategoryType | None = None, name: str | None = None
    ) -> int: ...
