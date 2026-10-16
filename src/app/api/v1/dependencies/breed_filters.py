from typing import Annotated

from fastapi import Depends, Query

from app.core.enums import PetType
from app.core.schemas.breed import BreedFilterQuery


def get_breed_filters(
    type: PetType | None = Query(None),
    q: str | None = Query(None),
) -> BreedFilterQuery:
    return BreedFilterQuery(type=type, q=q)


BreedFilterDep = Annotated[BreedFilterQuery, Depends(get_breed_filters)]
