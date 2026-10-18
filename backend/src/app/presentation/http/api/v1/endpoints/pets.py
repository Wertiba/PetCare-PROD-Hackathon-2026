from typing import Annotated
from urllib.parse import quote

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Body, File, Response, UploadFile, status

from app.application.pagination import Pagination
from app.application.pets.dto import PetCreateData, PetUpdateData
from app.application.pets.interactors import (
    ConfirmPetPhoto,
    CreatePet,
    DeleteGeneratedAvatar,
    DeletePet,
    DeletePetPhoto,
    GeneratePetAvatar,
    GetPet,
    IssuePetPhotoUploadUrl,
    ListPets,
    SelectPetAvatar,
    SetPetPhoto,
    UpdatePet,
)
from app.application.reports.interactors import ExportPetReport
from app.domain.pets.ids import PetId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.pet import (
    AvatarGenerateBody,
    PetAvatarBody,
    PetCreateBody,
    PetPhotoConfirmBody,
    PetPhotoUploadUrlBody,
    PetPhotoUploadUrlResponse,
    PetReadResponse,
    PetUpdateBody,
)
from app.presentation.http.schemas.responses import ErrorResponse
from app.presentation.http.uploads import read_photo

router = APIRouter(prefix="/pets", tags=["Pets"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Pet not found"}}
_UNPROCESSABLE = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Breed not found"}}
_PHOTO_FILE = {
    status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse, "description": "File is too large"},
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ErrorResponse, "description": "Unsupported file type"},
}
_PHOTO_UPLOAD = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "PHOTO_UPLOAD_NOT_FOUND"},
}


@router.get("", response_model=Page[PetReadResponse], status_code=status.HTTP_200_OK)
async def list_pets(
    user: CurrentUserDep, interactor: FromDishka[ListPets], pagination: PaginationDep
) -> Page[PetReadResponse]:
    return Page[PetReadResponse].model_validate(
        await interactor(user.id, Pagination(page=pagination.page, size=pagination.size)), from_attributes=True
    )


@router.post("", response_model=PetReadResponse, status_code=status.HTTP_201_CREATED, responses=_UNPROCESSABLE)
async def create_pet(
    user: CurrentUserDep, interactor: FromDishka[CreatePet], body: PetCreateBody, response: Response
) -> PetReadResponse:
    created = await interactor(user.id, PetCreateData(**body.model_dump()))
    track("pet", "created")
    response.headers["Location"] = f"/api/v1/pets/{created.id}"
    return PetReadResponse.model_validate(created, from_attributes=True)


@router.get("/{pet_id}", response_model=PetReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_pet(user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[GetPet]) -> PetReadResponse:
    return PetReadResponse.model_validate(await interactor(user.id, pet_id), from_attributes=True)


@router.patch(
    "/{pet_id}",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_UNPROCESSABLE},
)
async def update_pet(
    user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[UpdatePet], body: PetUpdateBody
) -> PetReadResponse:
    return PetReadResponse.model_validate(
        await interactor(user.id, pet_id, PetUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete("/{pet_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
async def delete_pet(user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[DeletePet]) -> None:
    await interactor(user.id, pet_id)
    track("pet", "deleted")


@router.post(
    "/{pet_id}/photo/upload-url",
    response_model=PetPhotoUploadUrlResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_PHOTO_FILE},
)
async def issue_photo_upload_url(
    user: CurrentUserDep,
    pet_id: PetId,
    interactor: FromDishka[IssuePetPhotoUploadUrl],
    body: PetPhotoUploadUrlBody,
) -> PetPhotoUploadUrlResponse:
    """Presigned PUT for a direct upload. The pet changes only after confirm."""
    result = await interactor(user.id, pet_id, body.contentType, body.size)
    track("pet", "photo_upload_url_issued")
    return PetPhotoUploadUrlResponse.model_validate(result, from_attributes=True)


@router.post(
    "/{pet_id}/photo/confirm",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_PHOTO_FILE, **_PHOTO_UPLOAD},
)
async def confirm_photo(
    user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[ConfirmPetPhoto], body: PetPhotoConfirmBody
) -> PetReadResponse:
    """Store an object uploaded with the presigned URL as the pet's photo."""
    result = await interactor(user.id, pet_id, body.key)
    track("pet", "photo_uploaded")
    return PetReadResponse.model_validate(result, from_attributes=True)


@router.put(
    "/{pet_id}/photo",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_PHOTO_FILE},
)
async def upload_photo(
    user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[SetPetPhoto], file: Annotated[UploadFile, File()]
) -> PetReadResponse:
    result = await interactor(user.id, pet_id, await read_photo(file))
    track("pet", "photo_uploaded")
    return PetReadResponse.model_validate(result, from_attributes=True)


@router.delete(
    "/{pet_id}/photo",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def delete_photo(user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[DeletePetPhoto]) -> PetReadResponse:
    """Remove the photo and the avatar generated from it."""
    result = await interactor(user.id, pet_id)
    track("pet", "photo_deleted")
    return PetReadResponse.model_validate(result, from_attributes=True)


@router.post(
    "/{pet_id}/avatar/generate",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses={
        **_NOT_FOUND,
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "PET_PHOTO_REQUIRED or AVATAR_PROMPT_REJECTED",
        },
        status.HTTP_502_BAD_GATEWAY: {"model": ErrorResponse, "description": "AVATAR_GENERATION_FAILED"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "AVATAR_GENERATION_UNAVAILABLE",
        },
    },
)
async def generate_avatar(
    user: CurrentUserDep,
    pet_id: PetId,
    interactor: FromDishka[GeneratePetAvatar],
    body: Annotated[AvatarGenerateBody | None, Body()] = None,
) -> PetReadResponse:
    """Build a stylized avatar from the pet's photo. Does not change avatarSource.

    Optional `prompt` is a short look wish. Requests to do anything else are rejected.
    """
    result = await interactor(user.id, pet_id, None if body is None else body.prompt)
    track("pet", "avatar_generated")
    return PetReadResponse.model_validate(result, from_attributes=True)


@router.delete(
    "/{pet_id}/avatar/generated",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses=_NOT_FOUND,
)
async def delete_generated_avatar(
    user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[DeleteGeneratedAvatar]
) -> PetReadResponse:
    """Remove the generated avatar. If it was selected, show the photo again."""
    result = await interactor(user.id, pet_id)
    track("pet", "generated_avatar_deleted")
    return PetReadResponse.model_validate(result, from_attributes=True)


@router.put(
    "/{pet_id}/avatar",
    response_model=PetReadResponse,
    status_code=status.HTTP_200_OK,
    responses={
        **_NOT_FOUND,
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "PET_PHOTO_REQUIRED or GENERATED_AVATAR_MISSING",
        },
    },
)
async def select_avatar(
    user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[SelectPetAvatar], body: PetAvatarBody
) -> PetReadResponse:
    """Choose which image to show: the original photo or the generated avatar."""
    result = await interactor(user.id, pet_id, body.source)
    track("pet", "avatar_selected")
    return PetReadResponse.model_validate(result, from_attributes=True)


@router.get(
    "/{pet_id}/report",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
            "description": "Pet health and care report: upcoming procedures, vaccination and treatment summary, "
            "monthly care activity, weight chart, food tolerance and vet conclusions",
        },
        **_NOT_FOUND,
    },
)
async def export_report(user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[ExportPetReport]) -> Response:
    report = await interactor(user.id, pet_id)
    track("pet", "report_exported")
    # RFC 6266: an ASCII fallback plus the real (Cyrillic) name for browsers that read filename*.
    disposition = f"attachment; filename=\"petcare-report.pdf\"; filename*=UTF-8''{quote(report.filename)}"
    return Response(report.content, media_type="application/pdf", headers={"Content-Disposition": disposition})
