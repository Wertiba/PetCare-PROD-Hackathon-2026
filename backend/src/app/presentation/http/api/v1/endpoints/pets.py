from typing import Annotated
from urllib.parse import quote

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, File, Response, UploadFile, status

from app.application.pagination import Pagination
from app.application.pets.dto import PetCreateData, PetUpdateData
from app.application.pets.interactors import CreatePet, DeletePet, GetPet, ListPets, SetPetPhoto, UpdatePet
from app.application.reports.interactors import ExportPetReport
from app.domain.pets.ids import PetId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.pet import PetCreateBody, PetReadResponse, PetUpdateBody
from app.presentation.http.schemas.responses import ErrorResponse
from app.presentation.http.uploads import read_photo

router = APIRouter(prefix="/pets", tags=["Pets"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Pet not found"}}
_UNPROCESSABLE = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Breed not found"}}


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
    user: CurrentUserDep, pet_id: PetId, interactor: FromDishka[SetPetPhoto], file: Annotated[UploadFile, File()]
) -> PetReadResponse:
    result = await interactor(user.id, pet_id, await read_photo(file))
    track("pet", "photo_uploaded")
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
