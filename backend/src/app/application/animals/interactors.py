from dataclasses import dataclass

from app.application.animals.dto import AnimalCreateData, AnimalResult, AnimalUpdateData
from app.application.changes import apply_changes
from app.application.exceptions import DuplicateError
from app.application.pagination import Page, Pagination
from app.application.ports.animal_gateway import AnimalGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.application.ports.user_gateway import UserGateway
from app.application.users.access import require_admin
from app.domain.animals.entity import Animal
from app.domain.animals.errors import AnimalNotFoundError
from app.domain.animals.ids import AnimalId
from app.domain.users.ids import UserId


@dataclass
class _AnimalContext:
    uow: UnitOfWork
    animal_gateway: AnimalGateway
    user_gateway: UserGateway

    @staticmethod
    def _to_read_response(animal: Animal) -> AnimalResult:
        return AnimalResult(id=animal.id, name=animal.name, createdBy=animal.created_by, createdAt=animal.created_at)

    async def _require_animal(self, animal_id: AnimalId) -> Animal:
        animal = await self.animal_gateway.get_by_id(animal_id)
        if animal is None:
            raise AnimalNotFoundError
        return animal

    async def _ensure_name_free(self, name: str, animal_id: AnimalId | None = None) -> None:
        # The unique constraint is case-sensitive, so "кошка" would otherwise sit next to "Кошка".
        existing = await self.animal_gateway.get_by_name(name)
        if existing is not None and existing.id != animal_id:
            raise DuplicateError("Animal with this name already exists")


class ListAnimals(_AnimalContext):
    async def __call__(self, pagination: Pagination, *, name: str | None = None) -> Page[AnimalResult]:
        animals = await self.animal_gateway.get_all(offset=pagination.offset, limit=pagination.limit, name=name)
        total = await self.animal_gateway.count(name=name)
        items = [self._to_read_response(animal) for animal in animals]
        return Page.build(items=items, total=total, pagination=pagination)


class GetAnimal(_AnimalContext):
    async def __call__(self, animal_id: AnimalId) -> AnimalResult:
        return self._to_read_response(await self._require_animal(animal_id))


class CreateAnimal(_AnimalContext):
    async def __call__(self, user_id: UserId, data: AnimalCreateData) -> AnimalResult:
        await require_admin(self.user_gateway, user_id)
        await self._ensure_name_free(data.name)
        animal = Animal(name=data.name, created_by=user_id)
        await self.uow.add(animal)
        result = self._to_read_response(animal)
        await self.uow.commit()
        return result


class UpdateAnimal(_AnimalContext):
    async def __call__(self, user_id: UserId, animal_id: AnimalId, data: AnimalUpdateData) -> AnimalResult:
        await require_admin(self.user_gateway, user_id)
        animal = await self._require_animal(animal_id)
        if "name" in data.changes:
            await self._ensure_name_free(data.changes["name"], animal.id)
            apply_changes(animal, {"name": data.changes["name"]})
        result = self._to_read_response(animal)
        await self.uow.commit()
        return result


class DeleteAnimal(_AnimalContext):
    async def __call__(self, user_id: UserId, animal_id: AnimalId) -> None:
        await require_admin(self.user_gateway, user_id)
        animal = await self._require_animal(animal_id)
        await self.uow.delete(animal)
        await self.uow.commit()
