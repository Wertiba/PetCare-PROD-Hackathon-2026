from dataclasses import dataclass

from app.application.breeds.dto import BreedResult
from app.application.pagination import Page, Pagination
from app.application.ports.breed_gateway import BreedGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.breeds.entity import Breed
from app.domain.pets.enums import PetType


@dataclass
class _BreedContext:
    uow: UnitOfWork
    breed_gateway: BreedGateway

    @staticmethod
    def _to_read_response(breed: Breed) -> BreedResult:
        return BreedResult(id=breed.id, type=breed.type, name=breed.name)


class ListBreeds(_BreedContext):
    async def __call__(
        self, pagination: Pagination, *, type_: PetType | None = None, name: str | None = None
    ) -> Page[BreedResult]:
        breeds = await self.breed_gateway.get_all(
            offset=pagination.offset, limit=pagination.limit, type_=type_, name=name
        )
        total = await self.breed_gateway.count(type_=type_, name=name)
        items = [self._to_read_response(breed) for breed in breeds]
        return Page.build(items=items, total=total, pagination=pagination)
