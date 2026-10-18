from typing import Protocol

from app.domain.animals.ids import AnimalId
from app.domain.breeds.entity import Breed
from app.domain.breeds.ids import BreedId


class BreedGateway(Protocol):
    async def get_by_id(self, id_: BreedId) -> Breed | None: ...

    async def get_by_name(self, animal_id: AnimalId, name: str) -> Breed | None:
        """Case-insensitive, within one animal."""
        ...

    async def get_all(
        self, offset: int, limit: int, *, animal_id: AnimalId | None = None, name: str | None = None
    ) -> list[Breed]: ...

    async def count(self, *, animal_id: AnimalId | None = None, name: str | None = None) -> int: ...
