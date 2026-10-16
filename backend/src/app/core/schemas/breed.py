from uuid import UUID

from app.core.enums import PetType
from app.core.schemas.base import PyModel


class BreedReadResponse(PyModel):
    id: UUID
    type: PetType
    name: str


class BreedFilterQuery(PyModel):
    type: PetType | None = None
    q: str | None = None
