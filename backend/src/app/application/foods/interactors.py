from dataclasses import dataclass
from typing import Any

from app.application.changes import apply_changes
from app.application.foods.dto import FoodCreateData, FoodResult, FoodSuspectsResult, FoodUpdateData
from app.application.pagination import Page, Pagination
from app.application.ports.food_gateway import FoodGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.foods.entity import Food
from app.domain.foods.errors import FoodNotFoundError
from app.domain.foods.ids import FoodId
from app.domain.foods.rules import normalize_ingredients, suspect_ingredients
from app.domain.pets.errors import RelatedPetNotFoundError
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId

_FIELD_TO_COLUMN = {
    "name": "name",
    "weight": "weight",
    "isApproach": "is_approach",
    "isTolerability": "is_tolerability",
    "consequences": "consequences",
}


@dataclass
class _FoodContext:
    uow: UnitOfWork
    food_gateway: FoodGateway
    pet_gateway: PetGateway

    @staticmethod
    def _to_read_response(food: Food) -> FoodResult:
        return FoodResult(
            id=food.id,
            petId=food.pet_id,
            name=food.name,
            weight=food.weight,
            ingredients=list(food.ingredients),
            isApproach=food.is_approach,
            isTolerability=food.is_tolerability,
            consequences=food.consequences,
            createdAt=food.created_at,
            updatedAt=food.updated_at,
        )

    async def _require_food(self, user_id: UserId, food_id: FoodId) -> Food:
        food = await self.food_gateway.get_by_id(food_id, user_id=user_id)
        if food is None:
            raise FoodNotFoundError
        return food


class ListFoods(_FoodContext):
    async def __call__(
        self,
        user_id: UserId,
        pagination: Pagination,
        *,
        pet_id: PetId | None = None,
        is_approach: bool | None = None,
        is_tolerability: bool | None = None,
    ) -> Page[FoodResult]:
        criteria = {"pet_id": pet_id, "is_approach": is_approach, "is_tolerability": is_tolerability}
        foods = await self.food_gateway.get_by_user_id(
            user_id, offset=pagination.offset, limit=pagination.limit, **criteria
        )
        total = await self.food_gateway.count_by_user_id(user_id, **criteria)
        items = [self._to_read_response(food) for food in foods]
        return Page.build(items=items, total=total, pagination=pagination)


class GetFood(_FoodContext):
    async def __call__(self, user_id: UserId, food_id: FoodId) -> FoodResult:
        return self._to_read_response(await self._require_food(user_id, food_id))


class CreateFood(_FoodContext):
    async def __call__(self, user_id: UserId, data: FoodCreateData) -> FoodResult:
        if await self.pet_gateway.get_by_id(data.petId, user_id=user_id) is None:
            raise RelatedPetNotFoundError
        food = Food(
            pet_id=data.petId,
            name=data.name,
            weight=data.weight,
            ingredients=normalize_ingredients(data.ingredients),
            is_approach=data.isApproach,
            is_tolerability=data.isTolerability,
            consequences=data.consequences,
        )
        await self.uow.add(food)
        result = self._to_read_response(food)
        await self.uow.commit()
        return result


class UpdateFood(_FoodContext):
    async def __call__(self, user_id: UserId, food_id: FoodId, data: FoodUpdateData) -> FoodResult:
        food = await self._require_food(user_id, food_id)
        values: dict[str, Any] = {
            _FIELD_TO_COLUMN[field]: value for field, value in data.changes.items() if field in _FIELD_TO_COLUMN
        }
        if "ingredients" in data.changes:
            values["ingredients"] = normalize_ingredients(data.changes["ingredients"])
        if values:
            apply_changes(food, values)
        result = self._to_read_response(food)
        await self.uow.commit()
        return result


class DeleteFood(_FoodContext):
    async def __call__(self, user_id: UserId, food_id: FoodId) -> None:
        food = await self._require_food(user_id, food_id)
        await self.uow.delete(food)
        await self.uow.commit()


class FindSuspectIngredients(_FoodContext):
    async def __call__(self, user_id: UserId, food_id: FoodId) -> FoodSuspectsResult:
        """Ingredients of this food the pet never got in a food it tolerated before."""
        food = await self._require_food(user_id, food_id)
        tolerated = await self.food_gateway.get_tolerated_before(food.pet_id, food.created_at, exclude_id=food.id)
        return FoodSuspectsResult(
            foodId=food.id,
            petId=food.pet_id,
            suspects=suspect_ingredients(food.ingredients, (other.ingredients for other in tolerated)),
            comparedFoods=len(tolerated),
        )
