from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.food_gateway import FoodGateway
from app.domain.foods.entity import Food
from app.domain.foods.ids import FoodId
from app.domain.pets.entity import Pet
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class SqlAlchemyFoodGateway(FoodGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: FoodId, *, user_id: UserId | None = None) -> Food | None:
        stmt = select(Food).where(Food.id == id_)
        if user_id is not None:
            stmt = self._owned(stmt, user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_user_id(
        self,
        user_id: UserId,
        offset: int,
        limit: int,
        *,
        pet_id: PetId | None = None,
        is_approach: bool | None = None,
        is_tolerability: bool | None = None,
    ) -> list[Food]:
        stmt = self._apply_criteria(
            self._owned(select(Food), user_id),
            pet_id=pet_id,
            is_approach=is_approach,
            is_tolerability=is_tolerability,
        )
        stmt = stmt.order_by(Food.created_at.desc(), Food.id).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count_by_user_id(
        self,
        user_id: UserId,
        *,
        pet_id: PetId | None = None,
        is_approach: bool | None = None,
        is_tolerability: bool | None = None,
    ) -> int:
        stmt = self._apply_criteria(
            self._owned(select(func.count()).select_from(Food), user_id),
            pet_id=pet_id,
            is_approach=is_approach,
            is_tolerability=is_tolerability,
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def get_tolerated_before(self, pet_id: PetId, before: float, *, exclude_id: FoodId) -> list[Food]:
        stmt = select(Food).where(
            Food.pet_id == pet_id,
            Food.is_tolerability.is_(True),
            Food.created_at < before,
            Food.id != exclude_id,
        )
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _owned(stmt: Select, user_id: UserId) -> Select:
        return stmt.join(Pet, Pet.id == Food.pet_id).where(Pet.user_id == user_id)

    @staticmethod
    def _apply_criteria(
        stmt: Select,
        *,
        pet_id: PetId | None = None,
        is_approach: bool | None = None,
        is_tolerability: bool | None = None,
    ) -> Select:
        if pet_id is not None:
            stmt = stmt.where(Food.pet_id == pet_id)
        if is_approach is not None:
            stmt = stmt.where(Food.is_approach.is_(is_approach))
        if is_tolerability is not None:
            stmt = stmt.where(Food.is_tolerability.is_(is_tolerability))
        return stmt
