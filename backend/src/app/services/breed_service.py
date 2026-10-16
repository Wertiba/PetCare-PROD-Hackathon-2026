from app.core.schemas.breed import BreedFilterQuery, BreedReadResponse
from app.core.utils.paginated import Page, PaginationParams
from app.infrastructure.models import Breed
from app.infrastructure.unit_of_work import UnitOfWork


class BreedService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _to_read_response(breed: Breed) -> BreedReadResponse:
        return BreedReadResponse(id=breed.id, type=breed.type, name=breed.name)

    async def list_breeds(self, pagination: PaginationParams, filters: BreedFilterQuery) -> Page[BreedReadResponse]:
        async with self.uow:
            breeds = await self.uow.breed_repo.get_filtered(filters, offset=pagination.offset, limit=pagination.limit)
            total = await self.uow.breed_repo.count_filtered(filters)
            items = [self._to_read_response(breed) for breed in breeds]
            return Page.build(items=items, total=total, pagination=pagination)
