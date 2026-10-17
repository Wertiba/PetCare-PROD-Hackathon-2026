from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.events.enums import EventPeriod, EventStatus, EventType
from app.domain.events.ids import EventId
from app.domain.pets.ids import PetId


@dataclass(eq=False, kw_only=True)
class Event:
    id: EventId = field(default_factory=uuid4)
    pet_id: PetId
    name: str
    type: EventType
    status: EventStatus
    schedule: float
    period: EventPeriod
    description: str | None = None
    done_at: float | None = None
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)
