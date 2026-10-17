from dataclasses import dataclass
from time import time
from typing import Any

from app.application.changes import apply_changes
from app.application.events.dto import (
    EventCalendarExport,
    EventCalendarItem,
    EventCompleteResult,
    EventCreateData,
    EventResult,
    EventUpdateData,
)
from app.application.pagination import Page, Pagination
from app.application.ports.event_gateway import EventGateway
from app.application.ports.pet_gateway import PetGateway
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.events.entity import Event
from app.domain.events.enums import EventStatus, EventType
from app.domain.events.errors import EventNotFoundError, EventNotPlannedError
from app.domain.events.ids import EventId
from app.domain.events.rules import next_schedule_for
from app.domain.pets.errors import PetNotFoundError, RelatedPetNotFoundError
from app.domain.pets.ids import PetId
from app.domain.users.ids import UserId

CALENDAR_EVENT_LIMIT = 1000

_FIELD_TO_COLUMN = {
    "name": "name",
    "type": "type",
    "status": "status",
    "schedule": "schedule",
    "period": "period",
    "description": "description",
}


@dataclass
class _EventContext:
    uow: UnitOfWork
    event_gateway: EventGateway
    pet_gateway: PetGateway

    @staticmethod
    def _to_read_response(event: Event, now: float | None = None) -> EventResult:
        now = time() if now is None else now
        schedule = event.schedule
        return EventResult(
            id=event.id,
            petId=event.pet_id,
            name=event.name,
            type=event.type,
            status=event.status,
            schedule=schedule,
            period=event.period,
            description=event.description,
            doneAt=event.done_at,
            isOverdue=event.status == EventStatus.PLANNED and schedule < now,
            nextSchedule=next_schedule_for(event),
            createdAt=event.created_at,
            updatedAt=event.updated_at,
        )

    async def _require_event(self, user_id: UserId, event_id: EventId) -> Event:
        event = await self.event_gateway.get_by_id(event_id, user_id=user_id)
        if event is None:
            raise EventNotFoundError
        return event

    async def _complete(self, user_id: UserId, event: Event, done_at: float) -> tuple[Event, Event | None]:
        """Mark a planned event done and, if it repeats, plan the next occurrence."""
        apply_changes(event, {"status": EventStatus.DONE, "done_at": done_at})
        completed = event
        next_at = next_schedule_for(completed)
        if next_at is None:
            return (completed, None)
        next_event = Event(
            pet_id=completed.pet_id,
            name=completed.name,
            type=completed.type,
            status=EventStatus.PLANNED,
            schedule=next_at,
            period=completed.period,
            description=completed.description,
        )
        await self.uow.add(next_event)
        return (completed, next_event)


class ListEvents(_EventContext):
    async def __call__(
        self,
        user_id: UserId,
        pagination: Pagination,
        *,
        pet_id: PetId | None = None,
        status: EventStatus | None = None,
        type_: EventType | None = None,
        from_: float | None = None,
        to: float | None = None,
    ) -> Page[EventResult]:
        events = await self.event_gateway.get_by_user_id(
            user_id,
            offset=pagination.offset,
            limit=pagination.limit,
            pet_id=pet_id,
            status=status,
            type_=type_,
            from_=from_,
            to=to,
        )
        total = await self.event_gateway.count_by_user_id(
            user_id, pet_id=pet_id, status=status, type_=type_, from_=from_, to=to
        )
        now = time()
        items = [self._to_read_response(event, now) for event in events]
        return Page.build(items=items, total=total, pagination=pagination)


class ListUpcomingEvents(_EventContext):
    async def __call__(
        self, user_id: UserId, pagination: Pagination, days: int, pet_id: PetId | None
    ) -> Page[EventResult]:
        now = time()
        until = now + days * 86400
        events = await self.event_gateway.get_upcoming(
            user_id, until, pet_id, offset=pagination.offset, limit=pagination.limit
        )
        total = await self.event_gateway.count_upcoming(user_id, until, pet_id)
        items = [self._to_read_response(event, now) for event in events]
        return Page.build(items=items, total=total, pagination=pagination)


class ExportEventsCalendar(_EventContext):
    async def __call__(self, user_id: UserId, pet_id: PetId | None = None) -> EventCalendarExport:
        if pet_id is not None and await self.pet_gateway.get_by_id(pet_id, user_id=user_id) is None:
            raise PetNotFoundError
        events = await self.event_gateway.get_by_user_id(
            user_id,
            offset=0,
            limit=CALENDAR_EVENT_LIMIT,
            pet_id=pet_id,
            status=EventStatus.PLANNED,
        )
        events.sort(key=lambda event: event.schedule)
        pet_ids = list({event.pet_id for event in events})
        pets = await self.pet_gateway.get_by_ids(user_id, pet_ids) if pet_ids else []
        names = {pet.id: pet.name for pet in pets}
        return EventCalendarExport(
            items=[
                EventCalendarItem(
                    id=event.id,
                    petId=event.pet_id,
                    petName=names[event.pet_id],
                    name=event.name,
                    type=event.type,
                    schedule=event.schedule,
                    period=event.period,
                    description=event.description,
                )
                for event in events
            ]
        )


class GetEvent(_EventContext):
    async def __call__(self, user_id: UserId, event_id: EventId) -> EventResult:
        return self._to_read_response(await self._require_event(user_id, event_id))


class CreateEvent(_EventContext):
    async def __call__(self, user_id: UserId, data: EventCreateData) -> EventResult:
        if await self.pet_gateway.get_by_id(data.petId, user_id=user_id) is None:
            raise RelatedPetNotFoundError
        now = time()
        event = Event(
            pet_id=data.petId,
            name=data.name,
            type=data.type,
            status=data.status,
            schedule=data.schedule,
            period=data.period,
            description=data.description,
            done_at=now if data.status == EventStatus.DONE else None,
        )
        await self.uow.add(event)
        result = self._to_read_response(event, now)
        await self.uow.commit()
        return result


class UpdateEvent(_EventContext):
    async def __call__(self, user_id: UserId, event_id: EventId, data: EventUpdateData) -> EventResult:
        """Plain field update. Moving a planned event to done goes through completion, so the
        next occurrence of a repeating event gets planned the same way as with /complete."""
        event = await self._require_event(user_id, event_id)
        provided = data.changes
        values: dict[str, Any] = {_FIELD_TO_COLUMN[field]: value for field, value in provided.items()}
        new_status = values.pop("status", event.status)
        completing = new_status == EventStatus.DONE and event.status == EventStatus.PLANNED
        if new_status != event.status and (not completing):
            values["status"] = new_status
            values["done_at"] = time() if new_status == EventStatus.DONE else None
        if values:
            apply_changes(event, values)
        if completing:
            event, _ = await self._complete(user_id, event, time())
        result = self._to_read_response(event)
        await self.uow.commit()
        return result


class CompleteEvent(_EventContext):
    async def __call__(self, user_id: UserId, event_id: EventId, done_at: float | None) -> EventCompleteResult:
        event = await self._require_event(user_id, event_id)
        if event.status != EventStatus.PLANNED:
            raise EventNotPlannedError
        completed, next_event = await self._complete(user_id, event, done_at if done_at is not None else time())
        now = time()
        result = EventCompleteResult(
            event=self._to_read_response(completed, now),
            nextEvent=self._to_read_response(next_event, now) if next_event else None,
        )
        await self.uow.commit()
        return result


class DeleteEvent(_EventContext):
    async def __call__(self, user_id: UserId, event_id: EventId) -> None:
        event = await self._require_event(user_id, event_id)
        await self.uow.delete(event)
        await self.uow.commit()
