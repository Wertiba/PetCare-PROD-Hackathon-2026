from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import anyio
from fastapi import UploadFile

from app.core.config import get_media_dir
from app.core.enums import PetType
from app.core.exceptions.breed_exs import BreedNotFoundError, BreedTypeMismatchError
from app.core.exceptions.pet_exs import FileTooLargeError, PetNotFoundError, UnsupportedFileTypeError
from app.core.logger import Logger
from app.core.metrics import track
from app.core.schemas.pet import PetBreedReadResponse, PetCreateBody, PetReadResponse, PetUpdateBody
from app.core.utils.paginated import Page, PaginationParams
from app.infrastructure.models import Pet
from app.infrastructure.unit_of_work import UnitOfWork

logger = Logger.get_logger()

MAX_PHOTO_BYTES = 5 * 1024 * 1024
_PHOTO_CHUNK_BYTES = 64 * 1024
_PHOTO_URL_PREFIX = "/media/pets/"
_ALLOWED_PHOTO_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _extension_for(content_type: str | None) -> str:
    if not content_type:
        raise UnsupportedFileTypeError
    media_type = content_type.split(";", 1)[0].strip().lower()
    extension = _ALLOWED_PHOTO_TYPES.get(media_type)
    if extension is None:
        raise UnsupportedFileTypeError
    return extension


async def _read_upload(upload: UploadFile) -> tuple[bytes, str]:
    extension = _extension_for(upload.content_type)
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(_PHOTO_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_PHOTO_BYTES:
            raise FileTooLargeError
        chunks.append(chunk)
    return b"".join(chunks), extension


async def _write_photo(content: bytes, extension: str) -> str:
    filename = f"{uuid4()}{extension}"
    directory = get_media_dir() / "pets"
    await anyio.Path(directory).mkdir(parents=True, exist_ok=True)
    await anyio.Path(directory / filename).write_bytes(content)
    return f"{_PHOTO_URL_PREFIX}{filename}"


def _path_for_photo_url(photo_url: str) -> Path | None:
    if not photo_url.startswith(_PHOTO_URL_PREFIX):
        return None
    name = photo_url.removeprefix(_PHOTO_URL_PREFIX)
    if not name or "/" in name or "\\" in name or ".." in name:
        return None
    return get_media_dir() / "pets" / name


async def _delete_photo_file(photo_url: str | None) -> None:
    if not photo_url:
        return
    path = _path_for_photo_url(photo_url)
    if path is None:
        return
    file_path = anyio.Path(path)
    if await file_path.exists():
        await file_path.unlink()


def _as_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def _age_months(birth_date: date | None, today: date | None = None) -> int | None:
    if birth_date is None:
        return None
    today = today or datetime.now(UTC).date()
    months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
    if today.day < birth_date.day:
        months -= 1
    return max(months, 0)


class PetService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _to_read_response(pet: Pet) -> PetReadResponse:
        birth_date = _as_date(pet.birth_date)
        breed = None
        if pet.breed is not None:
            breed = PetBreedReadResponse(id=pet.breed.id, name=pet.breed.name)
        return PetReadResponse(
            id=pet.id,
            userId=pet.user_id,
            name=pet.name,
            type=pet.type,
            breed=breed,
            birthDate=birth_date,
            ageMonths=_age_months(birth_date),
            photoUrl=pet.photo_url,
            createdAt=pet.created_at,
            updatedAt=pet.updated_at,
        )

    async def _require_breed(self, breed_id: UUID, pet_type: PetType):
        breed = await self.uow.breed_repo.get_by_id(breed_id)
        if breed is None:
            raise BreedNotFoundError
        if breed.type != pet_type:
            raise BreedTypeMismatchError
        return breed

    async def list_pets(self, user_id: UUID, pagination: PaginationParams) -> Page[PetReadResponse]:
        async with self.uow:
            pets = await self.uow.pet_repo.list_for_user(user_id, offset=pagination.offset, limit=pagination.limit)
            total = await self.uow.pet_repo.count_for_user(user_id)
            items = [self._to_read_response(pet) for pet in pets]
            return Page.build(items=items, total=total, pagination=pagination)

    async def get_pet(self, user_id: UUID, pet_id: UUID) -> PetReadResponse:
        async with self.uow:
            pet = await self.uow.pet_repo.get_for_user(pet_id, user_id)
            if pet is None:
                raise PetNotFoundError
            return self._to_read_response(pet)

    async def create_pet(self, user_id: UUID, data: PetCreateBody) -> PetReadResponse:
        async with self.uow:
            if data.breedId is not None:
                await self._require_breed(data.breedId, data.type)
            pet = await self.uow.pet_repo.add(
                Pet(
                    user_id=user_id,
                    type=data.type,
                    breed_id=data.breedId,
                    name=data.name,
                    birth_date=data.birthDate,
                )
            )
            created = await self.uow.pet_repo.get_for_user(pet.id, user_id)
            if created is None:
                raise PetNotFoundError
            logger.info("Pet {} created by user {}", pet.id, user_id)
            track("pet", "created")
            return self._to_read_response(created)

    async def update_pet(self, user_id: UUID, pet_id: UUID, data: PetUpdateBody) -> PetReadResponse:
        async with self.uow:
            pet = await self.uow.pet_repo.get_for_user(pet_id, user_id)
            if pet is None:
                raise PetNotFoundError

            provided = data.model_dump(exclude_unset=True)
            new_type = provided["type"] if "type" in provided else pet.type
            values: dict[str, Any] = {}

            if "name" in provided:
                values["name"] = provided["name"]
            if "type" in provided:
                values["type"] = new_type
            if "birthDate" in provided:
                values["birth_date"] = provided["birthDate"]

            if "breedId" in provided:
                breed_id = provided["breedId"]
                if breed_id is not None:
                    await self._require_breed(breed_id, new_type)
                values["breed_id"] = breed_id
            elif "type" in provided and pet.breed_id is not None:
                existing = pet.breed
                if existing is None or existing.type != new_type:
                    values["breed_id"] = None

            if not values:
                return self._to_read_response(pet)

            updated = await self.uow.pet_repo.update(pet.id, values)
            if updated is None:
                raise PetNotFoundError
            return self._to_read_response(updated)

    async def delete_pet(self, user_id: UUID, pet_id: UUID) -> None:
        async with self.uow:
            pet = await self.uow.pet_repo.get_for_user(pet_id, user_id)
            if pet is None:
                raise PetNotFoundError
            photo_url = pet.photo_url
            await self.uow.pet_repo.delete(pet)
        await _delete_photo_file(photo_url)
        logger.info("Pet {} deleted by user {}", pet_id, user_id)
        track("pet", "deleted")

    async def set_photo(self, user_id: UUID, pet_id: UUID, upload: UploadFile) -> PetReadResponse:
        content, extension = await _read_upload(upload)
        new_url: str | None = None
        try:
            async with self.uow:
                pet = await self.uow.pet_repo.get_for_user(pet_id, user_id)
                if pet is None:
                    raise PetNotFoundError
                old_url = pet.photo_url
                new_url = await _write_photo(content, extension)
                updated = await self.uow.pet_repo.update(pet_id, {"photo_url": new_url})
                if updated is None:
                    raise PetNotFoundError
                response = self._to_read_response(updated)
        except Exception:
            if new_url is not None:
                await _delete_photo_file(new_url)
            raise
        if old_url and old_url != new_url:
            await _delete_photo_file(old_url)
        track("pet", "photo_uploaded")
        return response
