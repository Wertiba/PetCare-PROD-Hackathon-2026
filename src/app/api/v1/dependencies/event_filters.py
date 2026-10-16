from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query

from app.core.enums import EventStatus, EventType
from app.core.schemas.event import EventFilterQuery
from app.core.utils import as_aware_utc


def get_event_filters(
    petId: UUID | None = Query(None),
    status: EventStatus | None = Query(None),
    type: EventType | None = Query(None),
    from_: datetime | None = Query(None, alias="from", description="Inclusive lower bound of `schedule`"),
    to: datetime | None = Query(None, description="Inclusive upper bound of `schedule`"),
) -> EventFilterQuery:
    return EventFilterQuery(
        petId=petId,
        status=status,
        type=type,
        from_=as_aware_utc(from_) if from_ else None,
        to=as_aware_utc(to) if to else None,
    )


EventFilterDep = Annotated[EventFilterQuery, Depends(get_event_filters)]
