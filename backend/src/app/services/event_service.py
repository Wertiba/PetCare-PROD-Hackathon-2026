from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.enums import EventStatus
from app.core.exceptions.event_exs import EventNotFoundError, EventNotPlannedError
from app.core.exceptions.pet_exs import RelatedPetNotFoundError
from app.core.logger import Logger
from app.core.metrics import track
from app.core.schemas.event import (
    EventCompleteResponse,
    EventCreateBody,
    EventFilterQuery,
    EventReadResponse,
    EventUpdateBody,
)
from app.core.utils import as_aware_utc, next_occurrence
from app.core.utils.paginated import Page, PaginationParams
from app.infrastructure.models import Event
from app.infrastructure.unit_of_work import UnitOfWork

logger = Logger.get_logger()

_FIELD_TO_COLUMN = {
    "name": "name",
    "type": "type",
    "status": "status",
    "schedule": "schedule",
    "period": "period",
    "description": "description",
}


def next_schedule_for(event: Event) -> datetime | None:
    """When a repeating event is due next.

    Counted from the moment it was actually done when that is later than planned: a vaccination
    done two months late is next due a year after it was done, not ten months later.
    """
    base = as_aware_utc(event.schedule)
    if event.done_at is not None:
        base = max(base, as_aware_utc(event.done_at))
    return next_occurrence(base, event.period)


class EventService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def _to_read_response(event: Event, now: datetime | None = None) -> EventReadResponse:
        now = now or datetime.now(UTC)
        schedule = as_aware_utc(event.schedule)
        return EventReadResponse(
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

    async def _require_event(self, user_id: UUID, event_id: UUID) -> Event:
        event = await self.uow.event_repo.get_for_user(event_id, user_id)
        if event is None:
            raise EventNotFoundError
        return event

    async def _complete(self, user_id: UUID, event: Event, done_at: datetime) -> tuple[Event, Event | None]:
        """Mark a planned event done and, if it repeats, plan the next occurrence."""
        await self.uow.event_repo.update(event.id, {"status": EventStatus.DONE, "done_at": done_at})
        completed = await self._require_event(user_id, event.id)
        track("event", "completed")

        next_at = next_schedule_for(completed)
        if next_at is None:
            return completed, None
        next_event = await self.uow.event_repo.add(
            Event(
                pet_id=completed.pet_id,
                name=completed.name,
                type=completed.type,
                status=EventStatus.PLANNED,
                schedule=next_at,
                period=completed.period,
                description=completed.description,
            )
        )
        logger.info("Event {} done, next occurrence {} planned at {}", event.id, next_event.id, next_at)
        track("event", "auto_planned")
        return completed, next_event

    async def list_events(
        self, user_id: UUID, pagination: PaginationParams, filters: EventFilterQuery
    ) -> Page[EventReadResponse]:
        async with self.uow:
            events = await self.uow.event_repo.list_for_user(
                user_id, filters, offset=pagination.offset, limit=pagination.limit
            )
            total = await self.uow.event_repo.count_for_user(user_id, filters)
            now = datetime.now(UTC)
            items = [self._to_read_response(event, now) for event in events]
            return Page.build(items=items, total=total, pagination=pagination)

    async def list_upcoming(
        self, user_id: UUID, pagination: PaginationParams, days: int, pet_id: UUID | None
    ) -> Page[EventReadResponse]:
        async with self.uow:
            now = datetime.now(UTC)
            until = now + timedelta(days=days)
            events = await self.uow.event_repo.list_upcoming(
                user_id, until, pet_id, offset=pagination.offset, limit=pagination.limit
            )
            total = await self.uow.event_repo.count_upcoming(user_id, until, pet_id)
            items = [self._to_read_response(event, now) for event in events]
            return Page.build(items=items, total=total, pagination=pagination)

    async def get_event(self, user_id: UUID, event_id: UUID) -> EventReadResponse:
        async with self.uow:
            return self._to_read_response(await self._require_event(user_id, event_id))

    async def create_event(self, user_id: UUID, data: EventCreateBody) -> EventReadResponse:
        async with self.uow:
            if await self.uow.pet_repo.get_for_user(data.petId, user_id) is None:
                raise RelatedPetNotFoundError
            now = datetime.now(UTC)
            event = await self.uow.event_repo.add(
                Event(
                    pet_id=data.petId,
                    name=data.name,
                    type=data.type,
                    status=data.status,
                    schedule=data.schedule,
                    period=data.period,
                    description=data.description,
                    done_at=now if data.status == EventStatus.DONE else None,
                )
            )
            logger.info("Event {} ({}) created for pet {}", event.id, data.type.value, data.petId)
            track("event", "created")
            return self._to_read_response(event, now)

    async def update_event(self, user_id: UUID, event_id: UUID, data: EventUpdateBody) -> EventReadResponse:
        """Plain field update. Moving a planned event to done goes through completion, so the
        next occurrence of a repeating event gets planned the same way as with /complete."""
        async with self.uow:
            event = await self._require_event(user_id, event_id)
            provided = data.model_dump(exclude_unset=True)
            values: dict[str, Any] = {_FIELD_TO_COLUMN[field]: value for field, value in provided.items()}
            new_status = values.pop("status", event.status)
            completing = new_status == EventStatus.DONE and event.status == EventStatus.PLANNED

            if new_status != event.status and not completing:
                values["status"] = new_status
                values["done_at"] = datetime.now(UTC) if new_status == EventStatus.DONE else None

            if values:
                await self.uow.event_repo.update(event.id, values)
                event = await self._require_event(user_id, event_id)
            if completing:
                event, _ = await self._complete(user_id, event, datetime.now(UTC))
            return self._to_read_response(event)

    async def complete_event(
        self, user_id: UUID, event_id: UUID, done_at: datetime | None
    ) -> EventCompleteResponse:
        async with self.uow:
            event = await self._require_event(user_id, event_id)
            if event.status != EventStatus.PLANNED:
                raise EventNotPlannedError
            completed, next_event = await self._complete(user_id, event, done_at or datetime.now(UTC))
            now = datetime.now(UTC)
            return EventCompleteResponse(
                event=self._to_read_response(completed, now),
                nextEvent=self._to_read_response(next_event, now) if next_event else None,
            )

    async def delete_event(self, user_id: UUID, event_id: UUID) -> None:
        async with self.uow:
            event = await self._require_event(user_id, event_id)
            await self.uow.event_repo.delete(event)
            track("event", "deleted")
