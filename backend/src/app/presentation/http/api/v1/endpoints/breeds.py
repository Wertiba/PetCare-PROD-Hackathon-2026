from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.breeds.dto import BreedCreateData, BreedUpdateData
from app.application.breeds.interactors import CreateBreed, DeleteBreed, GetBreed, ListBreeds, UpdateBreed
from app.application.pagination import Pagination
from app.domain.animals.ids import AnimalId
from app.domain.breeds.ids import BreedId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.base import NO_NUL_PATTERN
from app.presentation.http.schemas.breed import BreedCreateBody, BreedReadResponse, BreedUpdateBody
from app.presentation.http.schemas.responses import ErrorResponse

router = APIRouter(prefix="/breeds", tags=["Breeds"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Breed not found"}}
_ADMIN_ONLY = {status.HTTP_403_FORBIDDEN: {"model": ErrorResponse, "description": "Only an admin can do this"}}
_DUPLICATE = {
    status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "The animal has a breed with this name"}
}
_UNPROCESSABLE = {status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse, "description": "Animal not found"}}


@router.get("", response_model=Page[BreedReadResponse], status_code=status.HTTP_200_OK)
async def get_breeds(
    _: CurrentUserDep,
    interactor: FromDishka[ListBreeds],
    pagination: PaginationDep,
    animalId: AnimalId | None = Query(None),
    q: str | None = Query(None, pattern=NO_NUL_PATTERN, description="Substring of the breed name"),
) -> Page[BreedReadResponse]:
    """Seeded breeds first, then the ones admins added."""
    return Page[BreedReadResponse].model_validate(
        await interactor(Pagination(page=pagination.page, size=pagination.size), animal_id=animalId, name=q),
        from_attributes=True,
    )


@router.post(
    "",
    response_model=BreedReadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**_ADMIN_ONLY, **_DUPLICATE, **_UNPROCESSABLE},
)
async def create_breed(
    user: CurrentUserDep, interactor: FromDishka[CreateBreed], body: BreedCreateBody, response: Response
) -> BreedReadResponse:
    created = await interactor(user.id, BreedCreateData(**body.model_dump()))
    track("breed", "created")
    response.headers["Location"] = f"/api/v1/breeds/{created.id}"
    return BreedReadResponse.model_validate(created, from_attributes=True)


@router.get("/{breed_id}", response_model=BreedReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_breed(_: CurrentUserDep, breed_id: BreedId, interactor: FromDishka[GetBreed]) -> BreedReadResponse:
    return BreedReadResponse.model_validate(await interactor(breed_id), from_attributes=True)


@router.patch(
    "/{breed_id}",
    response_model=BreedReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_ADMIN_ONLY, **_DUPLICATE, **_UNPROCESSABLE},
)
async def update_breed(
    user: CurrentUserDep, breed_id: BreedId, interactor: FromDishka[UpdateBreed], body: BreedUpdateBody
) -> BreedReadResponse:
    return BreedReadResponse.model_validate(
        await interactor(user.id, breed_id, BreedUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete(
    "/{breed_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**_NOT_FOUND, **_ADMIN_ONLY},
)
async def delete_breed(user: CurrentUserDep, breed_id: BreedId, interactor: FromDishka[DeleteBreed]) -> None:
    """Pets of the breed stay, without a breed."""
    await interactor(user.id, breed_id)
    track("breed", "deleted")
