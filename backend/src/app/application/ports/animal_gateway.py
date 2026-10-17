from typing import Protocol

from app.domain.animals.entity import Animal
from app.domain.animals.ids import AnimalId


class AnimalGateway(Protocol):
    async def get_by_id(self, id_: AnimalId) -> Animal | None: ...

    async def get_all(self, offset: int, limit: int, *, name: str | None = None) -> list[Animal]: ...

    async def count(self, *, name: str | None = None) -> int: ...
