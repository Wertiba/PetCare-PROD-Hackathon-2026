from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.ports.note_gateway import NoteGateway
from app.domain.notes.entity import Note
from app.domain.notes.ids import NoteId
from app.domain.pets.entity import Pet
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


class SqlAlchemyNoteGateway(NoteGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: NoteId, *, user_id: UserId | None = None) -> Note | None:
        stmt = select(Note).where(Note.id == id_)
        if user_id is not None:
            stmt = self._owned(stmt, user_id)
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError("Database error") from exc

    async def get_by_user_id(
        self, user_id: UserId, offset: int, limit: int, *, pet_id: PetId | None = None, query: str | None = None
    ) -> list[Note]:
        stmt = self._apply_criteria(self._owned(select(Note), user_id), pet_id=pet_id, query=query)
        stmt = stmt.order_by(Note.created_at.desc()).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    async def count_by_user_id(self, user_id: UserId, *, pet_id: PetId | None = None, query: str | None = None) -> int:
        stmt = self._apply_criteria(
            self._owned(select(func.count()).select_from(Note), user_id), pet_id=pet_id, query=query
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise ApplicationError("Database error") from e

    @staticmethod
    def _owned(stmt: Select, user_id: UserId) -> Select:
        return stmt.join(Pet, Pet.id == Note.pet_id).where(Pet.user_id == user_id)

    @staticmethod
    def _apply_criteria(stmt: Select, *, pet_id: PetId | None = None, query: str | None = None) -> Select:
        if pet_id is not None:
            stmt = stmt.where(Note.pet_id == pet_id)
        if query:
            stmt = stmt.where(Note.content.ilike(f"%{query}%"))
        return stmt
