from dataclasses import dataclass
from typing import Any

from app.domain.notes.ids import NoteId
from app.domain.pets.ids import PetId


@dataclass(kw_only=True)
class NoteCreateData:
    petId: PetId
    content: str


@dataclass(kw_only=True)
class NoteUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class NoteResult:
    id: NoteId
    petId: PetId
    content: str
    createdAt: float
    updatedAt: float
