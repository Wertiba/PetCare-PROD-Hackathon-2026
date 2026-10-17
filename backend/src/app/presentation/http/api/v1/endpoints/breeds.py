from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from app.application.breeds.interactors import ListBreeds
from app.application.pagination import Pagination
from app.domain.pets.enums import PetType
from app.presentation.http.api.v1.dependencies import CurrentUserDep, PaginationDep
from app.presentation.http.paginated import Page
from app.presentation.http.schemas.breed import BreedReadResponse

router = APIRouter(prefix="/breeds", tags=["Breeds"], route_class=DishkaRoute)


@router.get("", response_model=Page[BreedReadResponse], status_code=status.HTTP_200_OK)
async def get_breeds(
    _: CurrentUserDep,
    interactor: FromDishka[ListBreeds],
    pagination: PaginationDep,
    type: PetType | None = Query(None),
    q: str | None = Query(None),
) -> Page[BreedReadResponse]:
    return Page[BreedReadResponse].model_validate(
        await interactor(Pagination(page=pagination.page, size=pagination.size), type_=type, name=q),
        from_attributes=True,
    )
