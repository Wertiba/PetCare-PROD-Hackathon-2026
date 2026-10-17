from typing import Protocol

from app.domain.breeds.entity import Breed
from app.domain.breeds.ids import BreedId
from app.domain.pets.enums import PetType


class BreedGateway(Protocol):
    async def get_by_id(self, id_: BreedId) -> Breed | None: ...

    async def get_all(
        self, offset: int, limit: int, *, type_: PetType | None = None, name: str | None = None
    ) -> list[Breed]: ...

    async def count(self, *, type_: PetType | None = None, name: str | None = None) -> int: ...
