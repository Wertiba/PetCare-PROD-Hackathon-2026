from dataclasses import dataclass

from app.application.changes import apply_changes
from app.application.notes.dto import NoteCreateData, NoteResult, NoteUpdateData
from app.application.pagination import Page, Pagination
from app.application.ports.note_gateway import NoteGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.notes.entity import Note
from app.domain.notes.errors import NoteNotFoundError
from app.domain.notes.ids import NoteId
from app.domain.pets.errors import RelatedPetNotFoundError
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId


@dataclass
class _NoteContext:
    uow: UnitOfWork
    note_gateway: NoteGateway
    pet_gateway: PetGateway

    @staticmethod
    def _to_read_response(note: Note) -> NoteResult:
        return NoteResult(
            id=note.id,
            petId=note.pet_id,
            content=note.content,
            createdAt=note.created_at,
            updatedAt=note.updated_at,
        )

    async def _require_note(self, user_id: UserId, note_id: NoteId) -> Note:
        note = await self.note_gateway.get_by_id(note_id, user_id=user_id)
        if note is None:
            raise NoteNotFoundError
        return note


class ListNotes(_NoteContext):
    async def __call__(
        self, user_id: UserId, pagination: Pagination, *, pet_id: PetId | None = None, query: str | None = None
    ) -> Page[NoteResult]:
        notes = await self.note_gateway.get_by_user_id(
            user_id, offset=pagination.offset, limit=pagination.limit, pet_id=pet_id, query=query
        )
        total = await self.note_gateway.count_by_user_id(user_id, pet_id=pet_id, query=query)
        items = [self._to_read_response(note) for note in notes]
        return Page.build(items=items, total=total, pagination=pagination)


class GetNote(_NoteContext):
    async def __call__(self, user_id: UserId, note_id: NoteId) -> NoteResult:
        return self._to_read_response(await self._require_note(user_id, note_id))


class CreateNote(_NoteContext):
    async def __call__(self, user_id: UserId, data: NoteCreateData) -> NoteResult:
        if await self.pet_gateway.get_by_id(data.petId, user_id=user_id) is None:
            raise RelatedPetNotFoundError
        note = Note(pet_id=data.petId, content=data.content)
        await self.uow.add(note)
        result = self._to_read_response(note)
        await self.uow.commit()
        return result


class UpdateNote(_NoteContext):
    async def __call__(self, user_id: UserId, note_id: NoteId, data: NoteUpdateData) -> NoteResult:
        note = await self._require_note(user_id, note_id)
        if "content" in data.changes:
            apply_changes(note, {"content": data.changes["content"]})
        result = self._to_read_response(note)
        await self.uow.commit()
        return result


class DeleteNote(_NoteContext):
    async def __call__(self, user_id: UserId, note_id: NoteId) -> None:
        note = await self._require_note(user_id, note_id)
        await self.uow.delete(note)
        await self.uow.commit()
