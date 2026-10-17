from dataclasses import dataclass
from typing import Any

from app.domain.events.enums import EventPeriod, EventStatus, EventType
from app.domain.events.ids import EventId
from app.domain.pets.ids import PetId


@dataclass(kw_only=True)
class EventCreateData:
    petId: PetId
    name: str
    type: EventType = EventType.OTHER
    status: EventStatus = EventStatus.PLANNED
    schedule: float
    period: EventPeriod = EventPeriod.NONE
    description: str | None = None


@dataclass(kw_only=True)
class EventUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class EventCompleteData:
    doneAt: float | None = None


@dataclass(kw_only=True)
class EventResult:
    id: EventId
    petId: PetId
    name: str
    type: EventType
    status: EventStatus
    schedule: float
    period: EventPeriod
    description: str | None
    doneAt: float | None
    isOverdue: bool
    nextSchedule: float | None
    createdAt: float
    updatedAt: float


@dataclass(kw_only=True)
class EventCompleteResult:
    event: EventResult
    nextEvent: EventResult | None
