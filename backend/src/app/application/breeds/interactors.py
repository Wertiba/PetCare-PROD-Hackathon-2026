from dataclasses import dataclass
from typing import Any

from app.application.breeds.dto import BreedCreateData, BreedResult, BreedUpdateData
from app.application.changes import apply_changes
from app.application.pagination import Page, Pagination
from app.application.ports.animal_gateway import AnimalGateway
from app.application.ports.breed_gateway import BreedGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_gateway import UserGateway
from app.application.users.access import require_admin
from app.domain.animals.errors import RelatedAnimalNotFoundError
from app.domain.animals.ids import AnimalId
from app.domain.breeds.entity import Breed
from app.domain.breeds.errors import BreedNotFoundError
from app.domain.breeds.ids import BreedId
from app.domain.users.ids import UserId


@dataclass
class _BreedContext:
    uow: UnitOfWork
    breed_gateway: BreedGateway
    animal_gateway: AnimalGateway
    user_gateway: UserGateway

    @staticmethod
    def _to_read_response(breed: Breed) -> BreedResult:
        return BreedResult(
            id=breed.id,
            animalId=breed.animal_id,
            name=breed.name,
            createdBy=breed.created_by,
            createdAt=breed.created_at,
        )

    async def _require_breed(self, breed_id: BreedId) -> Breed:
        breed = await self.breed_gateway.get_by_id(breed_id)
        if breed is None:
            raise BreedNotFoundError
        return breed

    async def _require_animal(self, animal_id: AnimalId) -> None:
        if await self.animal_gateway.get_by_id(animal_id) is None:
            raise RelatedAnimalNotFoundError


class ListBreeds(_BreedContext):
    async def __call__(
        self, pagination: Pagination, *, animal_id: AnimalId | None = None, name: str | None = None
    ) -> Page[BreedResult]:
        breeds = await self.breed_gateway.get_all(
            offset=pagination.offset, limit=pagination.limit, animal_id=animal_id, name=name
        )
        total = await self.breed_gateway.count(animal_id=animal_id, name=name)
        items = [self._to_read_response(breed) for breed in breeds]
        return Page.build(items=items, total=total, pagination=pagination)


class GetBreed(_BreedContext):
    async def __call__(self, breed_id: BreedId) -> BreedResult:
        return self._to_read_response(await self._require_breed(breed_id))


class CreateBreed(_BreedContext):
    async def __call__(self, user_id: UserId, data: BreedCreateData) -> BreedResult:
        await require_admin(self.user_gateway, user_id)
        await self._require_animal(data.animalId)
        breed = Breed(animal_id=data.animalId, name=data.name, created_by=user_id)
        await self.uow.add(breed)
        result = self._to_read_response(breed)
        await self.uow.commit()
        return result


class UpdateBreed(_BreedContext):
    async def __call__(self, user_id: UserId, breed_id: BreedId, data: BreedUpdateData) -> BreedResult:
        await require_admin(self.user_gateway, user_id)
        breed = await self._require_breed(breed_id)
        provided = data.changes
        values: dict[str, Any] = {}
        if "name" in provided:
            values["name"] = provided["name"]
        if "animalId" in provided:
            await self._require_animal(provided["animalId"])
            values["animal_id"] = provided["animalId"]
        if values:
            apply_changes(breed, values)
        result = self._to_read_response(breed)
        await self.uow.commit()
        return result


class DeleteBreed(_BreedContext):
    async def __call__(self, user_id: UserId, breed_id: BreedId) -> None:
        """Pets of the breed stay, without a breed."""
        await require_admin(self.user_gateway, user_id)
        breed = await self._require_breed(breed_id)
        await self.uow.delete(breed)
        await self.uow.commit()
