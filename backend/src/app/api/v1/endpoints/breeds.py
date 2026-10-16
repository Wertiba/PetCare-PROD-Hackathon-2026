from fastapi import APIRouter, status

from app.api.v1.dependencies import BreedFilterDep, BreedServiceDep, CurrentUserDep, PaginationDep
from app.core.schemas.breed import BreedReadResponse
from app.core.utils import Page

router = APIRouter(prefix="/breeds", tags=["Breeds"])


@router.get("", response_model=Page[BreedReadResponse], status_code=status.HTTP_200_OK)
async def get_breeds(
    _: CurrentUserDep,
    breed_service: BreedServiceDep,
    pagination: PaginationDep,
    filters: BreedFilterDep,
) -> Page[BreedReadResponse]:
    return await breed_service.list_breeds(pagination, filters)
