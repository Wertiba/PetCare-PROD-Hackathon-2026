from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, field_validator

from app.core.enums import CategoryKind, CategoryType, CategoryUnit
from app.core.schemas.base import DatetimeResponse, PyModel, strip_required_text


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


class CategoryReadResponse(DatetimeResponse):
    id: UUID
    name: str
    kind: CategoryKind
    type: CategoryType
    unit: CategoryUnit
    createdBy: UUID | None
    isSystem: bool
    createdAt: datetime


class CategoryFilterQuery(PyModel):
    type: CategoryType | None = None
    q: str | None = None
