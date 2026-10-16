from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Response, UploadFile, status

from app.api.v1.dependencies import CurrentUserDep, PaginationDep, PetServiceDep
from app.core.schemas.pet import PetCreateBody, PetReadResponse, PetUpdateBody
from app.core.schemas.responses import ErrorResponse
from app.core.utils import Page

router = APIRouter(prefix="/pets", tags=["Pets"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Pet not found"}}
_UNPROCESSABLE = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "model": ErrorResponse,
        "description": "Breed is missing or does not match",
    },
}


@router.get("", response_model=Page[PetReadResponse], status_code=status.HTTP_200_OK)
async def list_pets(
    user: CurrentUserDep,
    pet_service: PetServiceDep,
    pagination: PaginationDep,
) -> Page[PetReadResponse]:
    return await pet_service.list_pets(user.id, pagination)


@router.post(
    "",
    response_model=PetReadResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_UNPROCESSABLE,
)
async def create_pet(
    user: CurrentUserDep,
    pet_service: PetServiceDep,
    body: PetCreateBody,
    response: Response,
) -> PetReadResponse:
    created = await pet_service.create_pet(user.id, body)
    response.headers["Location"] = f"/api/v1/pets/{created.id}"
    return created


@router.get(
    "/{pet_id}",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def get_pet(user: CurrentUserDep, pet_id: UUID, pet_service: PetServiceDep) -> PetReadResponse:
    return await pet_service.get_pet(user.id, pet_id)


@router.patch(
    "/{pet_id}",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_UNPROCESSABLE},
)
async def update_pet(
    user: CurrentUserDep,
    pet_id: UUID,
    pet_service: PetServiceDep,
    body: PetUpdateBody,
) -> PetReadResponse:
    return await pet_service.update_pet(user.id, pet_id, body)


@router.delete(
    "/{pet_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_NOT_FOUND,
)
async def delete_pet(user: CurrentUserDep, pet_id: UUID, pet_service: PetServiceDep) -> None:
    await pet_service.delete_pet(user.id, pet_id)


@router.put(
    "/{pet_id}/photo",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses={
        **_NOT_FOUND,
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse, "description": "File is too large"},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ErrorResponse, "description": "Unsupported file type"},
    },
)
async def upload_photo(
    user: CurrentUserDep,
    pet_id: UUID,
    pet_service: PetServiceDep,
    file: Annotated[UploadFile, File()],
) -> PetReadResponse:
    return await pet_service.set_photo(user.id, pet_id, file)
