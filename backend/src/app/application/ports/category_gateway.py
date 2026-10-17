from typing import Protocol

from app.domain.categories.entity import Category
from app.domain.categories.enums import CategoryType
from app.domain.categories.ids import CategoryId


class CategoryGateway(Protocol):
    """Categories are shared: whoever creates one, every user can record states in it."""

    async def get_by_id(self, id_: CategoryId) -> Category | None: ...

    async def get_all(
        self, offset: int, limit: int, *, type_: CategoryType | None = None, name: str | None = None
    ) -> list[Category]: ...

    async def count(self, *, type_: CategoryType | None = None, name: str | None = None) -> int: ...
