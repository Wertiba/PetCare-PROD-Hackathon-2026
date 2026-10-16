from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.base import RepositoryError
from app.infrastructure.models import Pet
from app.infrastructure.repositories.base_repo import BaseRepository


class PetRepository(BaseRepository[Pet]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=Pet)

    async def get_for_user(self, pet_id: UUID, user_id: UUID) -> Pet | None:
        stmt = (
            select(Pet)
            .options(selectinload(Pet.breed))
            .where(Pet.id == pet_id, Pet.user_id == user_id)
            .execution_options(populate_existing=True)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def list_for_user(self, user_id: UUID, offset: int, limit: int) -> list[Pet]:
        stmt = (
            select(Pet)
            .options(selectinload(Pet.breed))
            .where(Pet.user_id == user_id)
            .order_by(Pet.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def count_for_user(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(Pet).where(Pet.user_id == user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e

    async def update(self, pet_id: UUID, data: dict[str, Any]) -> Pet | None:
        data["updated_at"] = datetime.now(UTC)
        updated = await super().update(pet_id, data)
        if updated is None:
            return None
        return await self.get_for_user(pet_id, updated.user_id)

    async def delete(self, pet: Pet) -> None:
        try:
            await self.session.delete(pet)
            await self.session.flush()
        except SQLAlchemyError as e:
            raise RepositoryError("Database error") from e
