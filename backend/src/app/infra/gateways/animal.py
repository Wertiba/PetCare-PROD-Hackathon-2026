from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.animal_gateway import AnimalGateway
from app.domain.animals.entity import Animal
from app.domain.animals.ids import AnimalId


class SqlAlchemyAnimalGateway(AnimalGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: AnimalId) -> Animal | None:
        stmt = select(Animal).where(Animal.id == id_)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_all(self, offset: int, limit: int, *, name: str | None = None) -> list[Animal]:
        # Seeded animals go first (the oldest rows): they are the defaults offered on pet registration.
        stmt = self._apply_criteria(select(Animal), name=name)
        stmt = stmt.order_by(Animal.created_at, Animal.name).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count(self, *, name: str | None = None) -> int:
        stmt = self._apply_criteria(select(func.count()).select_from(Animal), name=name)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _apply_criteria(stmt: Select, *, name: str | None = None) -> Select:
        if name:
            stmt = stmt.where(Animal.name.ilike(f"%{name}%"))
        return stmt
