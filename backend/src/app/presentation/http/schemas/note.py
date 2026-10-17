from typing import Annotated

from pydantic import Field, field_validator

from app.domain.notes.ids import NoteId
from app.domain.pets.ids import PetId
from app.presentation.http.schemas.base import PyModel, strip_required_text


class _NoteContentValidation(PyModel):
    @field_validator("content", mode="before", check_fields=False)
    @classmethod
    def strip_content(cls, value: object) -> object:
        return strip_required_text(value)


class NoteCreateBody(_NoteContentValidation):
    petId: PetId
    content: Annotated[str, Field(min_length=1, max_length=2000)]


class NoteUpdateBody(_NoteContentValidation):
    content: Annotated[str | None, Field(min_length=1, max_length=2000)] = None


class NoteReadResponse(PyModel):
    id: NoteId
    petId: PetId
    content: str
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
    updatedAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
