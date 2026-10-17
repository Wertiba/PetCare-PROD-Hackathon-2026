from app.domain.breeds.ids import BreedId
from app.domain.pets.enums import PetType
from app.presentation.http.schemas.base import PyModel


class BreedReadResponse(PyModel):
    id: BreedId
    type: PetType
    name: str
