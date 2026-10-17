from typing import Annotated

from pydantic import Field, field_validator

from app.domain.categories.enums import CategoryKind, CategoryType, CategoryUnit
from app.domain.categories.ids import CategoryId
from app.domain.users.ids import UserId
from app.presentation.http.schemas.base import PyModel, strip_required_text


class _CategoryNameValidation(PyModel):
    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def strip_name(cls, value: object) -> object:
        return strip_required_text(value)


class CategoryCreateBody(_CategoryNameValidation):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    kind: CategoryKind
    type: CategoryType
    unit: CategoryUnit = CategoryUnit.NONE


class CategoryUpdateBody(_CategoryNameValidation):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    kind: CategoryKind | None = None
    type: CategoryType | None = None
    unit: CategoryUnit | None = None


class CategoryReadResponse(PyModel):
    id: CategoryId
    name: str
    kind: CategoryKind
    type: CategoryType
    unit: CategoryUnit
    createdBy: UserId | None
    isSystem: bool
    createdAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")
