from typing import Annotated

from pydantic import Field, field_validator

from app.domain.foods.ids import FoodId
from app.domain.pets.ids import PetId
from app.presentation.http.schemas.base import PyModel, strip_optional_text, strip_required_text

_INGREDIENTS = Field(
    description="Composition; trimmed, blanks and case-insensitive duplicates are dropped",
    max_length=100,
)
_IS_APPROACH = Field(description="Liked by the pet; null when not assessed yet")
_IS_TOLERABILITY = Field(description="Tolerated well, no bad reaction; null when not assessed yet")
_CONSEQUENCES = Field(description="Reaction after feeding, e.g. GI upset or allergy", max_length=1000)


class _FoodValidation(PyModel):
    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def strip_name(cls, value: object) -> object:
        return strip_required_text(value)

    @field_validator("consequences", mode="before", check_fields=False)
    @classmethod
    def strip_consequences(cls, value: object) -> object:
        return strip_optional_text(value)

    @field_validator("ingredients", mode="before", check_fields=False)
    @classmethod
    def ingredients_not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("ingredients cannot be null, send [] instead")
        return value


class FoodCreateBody(_FoodValidation):
    petId: PetId
    name: Annotated[str, Field(min_length=1, max_length=255)]
    weight: Annotated[int | None, Field(ge=0, description="Portion in grams")] = None
    ingredients: Annotated[list[Annotated[str, Field(max_length=100)]], _INGREDIENTS] = []
    isApproach: Annotated[bool | None, _IS_APPROACH] = None
    isTolerability: Annotated[bool | None, _IS_TOLERABILITY] = None
    consequences: Annotated[str | None, _CONSEQUENCES] = None


class FoodUpdateBody(_FoodValidation):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    weight: Annotated[int | None, Field(ge=0, description="Portion in grams")] = None
    ingredients: Annotated[list[Annotated[str, Field(max_length=100)]] | None, _INGREDIENTS] = None
    isApproach: Annotated[bool | None, _IS_APPROACH] = None
    isTolerability: Annotated[bool | None, _IS_TOLERABILITY] = None
    consequences: Annotated[str | None, _CONSEQUENCES] = None


class FoodReadResponse(PyModel):
    id: FoodId
    petId: PetId
    name: str
    weight: int | None
    ingredients: list[str]
    isApproach: bool | None = _IS_APPROACH
    isTolerability: bool | None = _IS_TOLERABILITY
    consequences: str | None
    createdAt: float = Field(description="Feeding time. Unix seconds in UTC; fractional seconds are supported.")
    updatedAt: float = Field(description="Unix seconds in UTC; fractional seconds are supported.")


class FoodSuspectsResponse(PyModel):
    foodId: FoodId
    petId: PetId
    suspects: list[str] = Field(
        description="Ingredients of this food that none of the pet's earlier tolerated foods contained"
    )
    comparedFoods: int = Field(description="How many earlier tolerated foods were compared against")
