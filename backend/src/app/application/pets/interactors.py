from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.application.changes import apply_changes
from app.application.pagination import Page, Pagination
from app.application.pets.dto import PetAnimalResult, PetBreedResult, PetCreateData, PetResult, PetUpdateData
from app.application.ports.avatar_generator import AvatarGenerator
from app.application.ports.breed_gateway import BreedGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.photos import MAX_PHOTO_BYTES, PhotoStorage, PhotoUpload
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.breeds.entity import Breed
from app.domain.breeds.errors import RelatedBreedNotFoundError
from app.domain.breeds.ids import BreedId
from app.domain.pets.entity import Pet
from app.domain.pets.enums import AvatarSource
from app.domain.pets.errors import (
    FileTooLargeError,
    GeneratedAvatarMissingError,
    PetNotFoundError,
    PetPhotoRequiredError,
    UnsupportedFileTypeError,
)
from app.domain.pets.ids import PetId
from app.domain.pets.rules import age_months
from app.domain.users.ids import UserId

_PHOTO_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
_EXTENSION_TYPES = {extension: media_type for media_type, extension in _PHOTO_EXTENSIONS.items()}
_EXTENSION_TYPES[".jpeg"] = "image/jpeg"


def photo_media_type(content_type: str | None) -> str:
    media_type = content_type.split(";", 1)[0].strip().lower() if content_type else ""
    if media_type not in _PHOTO_EXTENSIONS:
        raise UnsupportedFileTypeError
    return media_type


def photo_extension(content_type: str | None) -> str:
    return _PHOTO_EXTENSIONS[photo_media_type(content_type)]


def content_type_for_key(key: str) -> str:
    dot = key.rfind(".")
    if dot < 0:
        return "application/octet-stream"
    return _EXTENSION_TYPES.get(key[dot:].lower(), "application/octet-stream")


@dataclass
class _PetContext:
    uow: UnitOfWork
    pet_gateway: PetGateway
    breed_gateway: BreedGateway
    photos: PhotoStorage

    def _to_read_response(self, pet: Pet) -> PetResult:
        birth_date = pet.birth_date
        breed = animal = None
        if pet.breed is not None:
            breed = PetBreedResult(id=pet.breed.id, name=pet.breed.name)
            if pet.breed.animal is not None:
                animal = PetAnimalResult(id=pet.breed.animal.id, name=pet.breed.animal.name)
        source = pet.avatar_source if isinstance(pet.avatar_source, AvatarSource) else AvatarSource(pet.avatar_source)
        photo_url = self.photos.url(pet.photo_key)
        generated_url = self.photos.url(pet.generated_avatar_key)
        avatar_url = generated_url if source == AvatarSource.GENERATED else photo_url
        return PetResult(
            id=pet.id,
            userId=pet.user_id,
            name=pet.name,
            animal=animal,
            breed=breed,
            birthDate=birth_date,
            ageMonths=age_months(birth_date),
            photoUrl=photo_url,
            generatedAvatarUrl=generated_url,
            avatarSource=source,
            avatarUrl=avatar_url,
            createdAt=pet.created_at,
            updatedAt=pet.updated_at,
        )

    async def _require_breed(self, breed_id: BreedId) -> Breed:
        breed = await self.breed_gateway.get_by_id(breed_id)
        if breed is None:
            raise RelatedBreedNotFoundError
        return breed

    async def _require_pet(self, user_id: UserId, pet_id: PetId) -> Pet:
        pet = await self.pet_gateway.get_by_id(pet_id, user_id=user_id)
        if pet is None:
            raise PetNotFoundError
        return pet


class ListPets(_PetContext):
    async def __call__(self, user_id: UserId, pagination: Pagination) -> Page[PetResult]:
        pets = await self.pet_gateway.get_by_user_id(user_id, offset=pagination.offset, limit=pagination.limit)
        total = await self.pet_gateway.count_by_user_id(user_id)
        items = [self._to_read_response(pet) for pet in pets]
        return Page.build(items=items, total=total, pagination=pagination)


class GetPet(_PetContext):
    async def __call__(self, user_id: UserId, pet_id: PetId) -> PetResult:
        return self._to_read_response(await self._require_pet(user_id, pet_id))


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
        pet = await self._require_pet(user_id, pet_id)
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


class DeletePet(_PetContext):
    async def __call__(self, user_id: UserId, pet_id: PetId) -> None:
        pet = await self._require_pet(user_id, pet_id)
        photo_key = pet.photo_key
        avatar_key = pet.generated_avatar_key
        await self.uow.delete(pet)
        await self.uow.commit()
        await self.photos.delete(photo_key)
        await self.photos.delete(avatar_key)


class SetPetPhoto(_PetContext):
    async def __call__(self, user_id: UserId, pet_id: PetId, upload: PhotoUpload) -> PetResult:
        media_type = photo_media_type(upload.content_type)
        extension = _PHOTO_EXTENSIONS[media_type]
        if len(upload.content) > MAX_PHOTO_BYTES:
            raise FileTooLargeError
        pet = await self._require_pet(user_id, pet_id)
        old_photo = pet.photo_key
        old_avatar = pet.generated_avatar_key
        new_key = f"pets/{pet.id}/photo/{uuid4()}{extension}"
        await self.photos.save(new_key, upload.content, media_type)
        try:
            apply_changes(
                pet,
                {"photo_key": new_key, "generated_avatar_key": None, "avatar_source": AvatarSource.PHOTO},
            )
            result = self._to_read_response(pet)
            await self.uow.commit()
        except Exception:
            await self.photos.delete(new_key)
            raise
        if old_photo and old_photo != new_key:
            await self.photos.delete(old_photo)
        if old_avatar:
            await self.photos.delete(old_avatar)
        return result


@dataclass
class GeneratePetAvatar(_PetContext):
    avatars: AvatarGenerator

    async def __call__(self, user_id: UserId, pet_id: PetId) -> PetResult:
        pet = await self._require_pet(user_id, pet_id)
        if not pet.photo_key:
            raise PetPhotoRequiredError
        original = await self.photos.load(pet.photo_key)
        generated = await self.avatars.generate(original, content_type_for_key(pet.photo_key))
        extension = generated.extension if generated.extension.startswith(".") else f".{generated.extension}"
        new_key = f"pets/{pet.id}/avatar/{uuid4()}{extension}"
        await self.photos.save(new_key, generated.content, generated.content_type)
        old_avatar = pet.generated_avatar_key
        try:
            apply_changes(pet, {"generated_avatar_key": new_key})
            result = self._to_read_response(pet)
            await self.uow.commit()
        except Exception:
            await self.photos.delete(new_key)
            raise
        if old_avatar and old_avatar != new_key:
            await self.photos.delete(old_avatar)
        return result


class SelectPetAvatar(_PetContext):
    async def __call__(self, user_id: UserId, pet_id: PetId, source: AvatarSource) -> PetResult:
        pet = await self._require_pet(user_id, pet_id)
        if source == AvatarSource.GENERATED:
            if not pet.generated_avatar_key:
                raise GeneratedAvatarMissingError
        elif not pet.photo_key:
            raise PetPhotoRequiredError
        apply_changes(pet, {"avatar_source": source})
        result = self._to_read_response(pet)
        await self.uow.commit()
        return result
