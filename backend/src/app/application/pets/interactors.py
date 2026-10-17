from dataclasses import dataclass
from typing import Any

from app.application.changes import apply_changes
from app.application.pagination import Page, Pagination
from app.application.pets.dto import PetAnimalResult, PetBreedResult, PetCreateData, PetResult, PetUpdateData
from app.application.ports.breed_gateway import BreedGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.photos import MAX_PHOTO_BYTES, PhotoStorage, PhotoUpload
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.breeds.entity import Breed
from app.domain.breeds.errors import RelatedBreedNotFoundError
from app.domain.breeds.ids import BreedId
from app.domain.pets.entity import Pet
from app.domain.pets.errors import FileTooLargeError, PetNotFoundError, UnsupportedFileTypeError
from app.domain.pets.ids import PetId
from app.domain.pets.rules import age_months
from app.domain.users.ids import UserId


@dataclass
class _PetContext:
    uow: UnitOfWork
    pet_gateway: PetGateway
    breed_gateway: BreedGateway

    @staticmethod
    def _to_read_response(pet: Pet) -> PetResult:
        birth_date = pet.birth_date
        breed = animal = None
        if pet.breed is not None:
            breed = PetBreedResult(id=pet.breed.id, name=pet.breed.name)
            if pet.breed.animal is not None:
                animal = PetAnimalResult(id=pet.breed.animal.id, name=pet.breed.animal.name)
        return PetResult(
            id=pet.id,
            userId=pet.user_id,
            name=pet.name,
            animal=animal,
            breed=breed,
            birthDate=birth_date,
            ageMonths=age_months(birth_date),
            photoUrl=pet.photo_url,
            createdAt=pet.created_at,
            updatedAt=pet.updated_at,
        )

    async def _require_breed(self, breed_id: BreedId) -> Breed:
        breed = await self.breed_gateway.get_by_id(breed_id)
        if breed is None:
            raise RelatedBreedNotFoundError
        return breed


class ListPets(_PetContext):
    async def __call__(self, user_id: UserId, pagination: Pagination) -> Page[PetResult]:
        pets = await self.pet_gateway.get_by_user_id(user_id, offset=pagination.offset, limit=pagination.limit)
        total = await self.pet_gateway.count_by_user_id(user_id)
        items = [self._to_read_response(pet) for pet in pets]
        return Page.build(items=items, total=total, pagination=pagination)


class GetPet(_PetContext):
    async def __call__(self, user_id: UserId, pet_id: PetId) -> PetResult:
        pet = await self.pet_gateway.get_by_id(pet_id, user_id=user_id)
        if pet is None:
            raise PetNotFoundError
        return self._to_read_response(pet)


class CreatePet(_PetContext):
    async def __call__(self, user_id: UserId, data: PetCreateData) -> PetResult:
        breed = await self._require_breed(data.breedId)
        pet = Pet(user_id=user_id, breed_id=breed.id, name=data.name, birth_date=data.birthDate, breed=breed)
        await self.uow.add(pet)
        result = self._to_read_response(pet)
        await self.uow.commit()
        return result


class UpdatePet(_PetContext):
    async def __call__(self, user_id: UserId, pet_id: PetId, data: PetUpdateData) -> PetResult:
        pet = await self.pet_gateway.get_by_id(pet_id, user_id=user_id)
        if pet is None:
            raise PetNotFoundError
        provided = data.changes
        values: dict[str, Any] = {}
        if "name" in provided:
            values["name"] = provided["name"]
        if "birthDate" in provided:
            values["birth_date"] = provided["birthDate"]
        if "breedId" in provided:
            breed = await self._require_breed(provided["breedId"])
            values["breed_id"] = breed.id
            values["breed"] = breed
        if values:
            apply_changes(pet, values)
        result = self._to_read_response(pet)
        await self.uow.commit()
        return result


@dataclass
class _PetPhotoContext(_PetContext):
    photos: PhotoStorage


class DeletePet(_PetPhotoContext):
    async def __call__(self, user_id: UserId, pet_id: PetId) -> None:
        pet = await self.pet_gateway.get_by_id(pet_id, user_id=user_id)
        if pet is None:
            raise PetNotFoundError
        photo_url = pet.photo_url
        await self.uow.delete(pet)
        await self.uow.commit()
        await self.photos.delete(photo_url)


def photo_extension(content_type: str | None) -> str:
    allowed = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    media_type = content_type.split(";", 1)[0].strip().lower() if content_type else ""
    if media_type not in allowed:
        raise UnsupportedFileTypeError
    return allowed[media_type]


class SetPetPhoto(_PetPhotoContext):
    async def __call__(self, user_id: UserId, pet_id: PetId, upload: PhotoUpload) -> PetResult:
        extension = photo_extension(upload.content_type)
        if len(upload.content) > MAX_PHOTO_BYTES:
            raise FileTooLargeError
        pet = await self.pet_gateway.get_by_id(pet_id, user_id=user_id)
        if pet is None:
            raise PetNotFoundError
        old_url = pet.photo_url
        new_url = await self.photos.save(upload.content, extension)
        try:
            apply_changes(pet, {"photo_url": new_url})
            result = self._to_read_response(pet)
            await self.uow.commit()
        except Exception:
            await self.photos.delete(new_url)
            raise
        if old_url and old_url != new_url:
            await self.photos.delete(old_url)
        return result
