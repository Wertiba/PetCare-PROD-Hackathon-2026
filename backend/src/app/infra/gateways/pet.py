from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.exceptions import ApplicationError
from app.application.ports.pet_gateway import PetGateway
from app.domain.pets.entity import Pet
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class SqlAlchemyPetGateway(PetGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: PetId, *, user_id: UserId | None = None) -> Pet | None:
        stmt = select(Pet).where(Pet.id == id_).options(selectinload(Pet.breed))
        if user_id is not None:
            stmt = stmt.where(Pet.user_id == user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_ids(self, user_id: UserId, ids: Sequence[PetId]) -> list[Pet]:
        if not ids:
            return []
        stmt = select(Pet).where(Pet.user_id == user_id, Pet.id.in_(ids)).options(selectinload(Pet.breed))
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_user_id(self, user_id: UserId, offset: int, limit: int) -> list[Pet]:
        stmt = (
            select(Pet)
            .options(selectinload(Pet.breed))
            .where(Pet.user_id == user_id)
            .order_by(Pet.created_at.desc(), Pet.id)
            .offset(offset)
            .limit(limit)
        )
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count_by_user_id(self, user_id: UserId) -> int:
        stmt = select(func.count()).select_from(Pet).where(Pet.user_id == user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e
