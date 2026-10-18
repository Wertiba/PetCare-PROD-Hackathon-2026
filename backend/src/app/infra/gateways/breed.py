from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.breed_gateway import BreedGateway
from app.domain.animals.ids import AnimalId
from app.domain.breeds.entity import Breed
from app.domain.breeds.ids import BreedId


class SqlAlchemyBreedGateway(BreedGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: BreedId) -> Breed | None:
        stmt = select(Breed).where(Breed.id == id_)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_all(
        self, offset: int, limit: int, *, animal_id: AnimalId | None = None, name: str | None = None
    ) -> list[Breed]:
        # Seeded breeds go first (the oldest rows): they are the defaults offered on pet registration.
        stmt = self._apply_criteria(select(Breed), animal_id=animal_id, name=name)
        stmt = stmt.order_by(Breed.created_at, Breed.name).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count(self, *, animal_id: AnimalId | None = None, name: str | None = None) -> int:
        stmt = self._apply_criteria(select(func.count()).select_from(Breed), animal_id=animal_id, name=name)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _apply_criteria(stmt: Select, *, animal_id: AnimalId | None = None, name: str | None = None) -> Select:
        if animal_id is not None:
            stmt = stmt.where(Breed.animal_id == animal_id)
        if name:
            stmt = stmt.where(Breed.name.ilike(f"%{name}%"))
        return stmt
