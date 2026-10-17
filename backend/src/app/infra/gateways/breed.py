from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.breed_gateway import BreedGateway
from app.domain.breeds.entity import Breed
from app.domain.breeds.ids import BreedId
from app.domain.pets.enums import PetType


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
        self, offset: int, limit: int, *, type_: PetType | None = None, name: str | None = None
    ) -> list[Breed]:
        stmt = self._apply_criteria(select(Breed), type_=type_, name=name)
        stmt = stmt.order_by(Breed.name).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count(self, *, type_: PetType | None = None, name: str | None = None) -> int:
        stmt = self._apply_criteria(select(func.count()).select_from(Breed), type_=type_, name=name)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _apply_criteria(stmt: Select, *, type_: PetType | None = None, name: str | None = None) -> Select:
        if type_ is not None:
            stmt = stmt.where(Breed.type == type_)
        if name:
            stmt = stmt.where(Breed.name.ilike(f"%{name}%"))
        return stmt
