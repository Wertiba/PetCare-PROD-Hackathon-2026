from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.notes.ids import NoteId
from app.domain.pets.ids import PetId


@dataclass(eq=False, kw_only=True)
class Note:
    id: NoteId = field(default_factory=uuid4)
    pet_id: PetId
    content: str
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)
