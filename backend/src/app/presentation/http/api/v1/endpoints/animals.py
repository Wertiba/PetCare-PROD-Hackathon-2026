from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from app.application.animals.dto import AnimalCreateData, AnimalUpdateData
from app.application.animals.interactors import CreateAnimal, DeleteAnimal, GetAnimal, ListAnimals, UpdateAnimal
from app.application.pagination import Pagination
from app.domain.animals.ids import AnimalId
from app.infra.metrics import track
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.animal import AnimalCreateBody, AnimalReadResponse, AnimalUpdateBody
from app.presentation.http.schemas.responses import ErrorResponse

router = APIRouter(prefix="/animals", tags=["Animals"], route_class=DishkaRoute)
_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Animal not found"}}
_ADMIN_ONLY = {status.HTTP_403_FORBIDDEN: {"model": ErrorResponse, "description": "Only an admin can do this"}}
_DUPLICATE = {status.HTTP_409_CONFLICT: {"model": ErrorResponse, "description": "Animal with this name exists"}}


@router.get("", response_model=Page[AnimalReadResponse], status_code=status.HTTP_200_OK)
async def list_animals(
    _: CurrentUserDep,
    interactor: FromDishka[ListAnimals],
    pagination: PaginationDep,
    q: str | None = Query(None, description="Substring of the animal name"),
) -> Page[AnimalReadResponse]:
    """Seeded animals first, then the ones admins added."""
    return Page[AnimalReadResponse].model_validate(
        await interactor(Pagination(page=pagination.page, size=pagination.size), name=q), from_attributes=True
    )


@router.post(
    "",
    response_model=AnimalReadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**_ADMIN_ONLY, **_DUPLICATE},
)
async def create_animal(
    user: CurrentUserDep, interactor: FromDishka[CreateAnimal], body: AnimalCreateBody, response: Response
) -> AnimalReadResponse:
    created = await interactor(user.id, AnimalCreateData(**body.model_dump()))
    track("animal", "created")
    response.headers["Location"] = f"/api/v1/animals/{created.id}"
    return AnimalReadResponse.model_validate(created, from_attributes=True)


@router.get("/{animal_id}", response_model=AnimalReadResponse, status_code=status.HTTP_200_OK, responses=_NOT_FOUND)
async def get_animal(_: CurrentUserDep, animal_id: AnimalId, interactor: FromDishka[GetAnimal]) -> AnimalReadResponse:
    return AnimalReadResponse.model_validate(await interactor(animal_id), from_attributes=True)


@router.patch(
    "/{animal_id}",
    response_model=AnimalReadResponse,
    status_code=status.HTTP_200_OK,
    responses={**_NOT_FOUND, **_ADMIN_ONLY, **_DUPLICATE},
)
async def update_animal(
    user: CurrentUserDep, animal_id: AnimalId, interactor: FromDishka[UpdateAnimal], body: AnimalUpdateBody
) -> AnimalReadResponse:
    return AnimalReadResponse.model_validate(
        await interactor(user.id, animal_id, AnimalUpdateData(changes=body.model_dump(exclude_unset=True))),
        from_attributes=True,
    )


@router.delete(
    "/{animal_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**_NOT_FOUND, **_ADMIN_ONLY},
)
async def delete_animal(user: CurrentUserDep, animal_id: AnimalId, interactor: FromDishka[DeleteAnimal]) -> None:
    """Deletes the animal's breeds too; pets of those breeds stay, without a breed."""
    await interactor(user.id, animal_id)
    track("animal", "deleted")
