from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query

from app.core.enums import NotificationStatus
from app.core.schemas.notification import NotificationFilterQuery


def get_notification_filters(
    eventId: UUID | None = Query(None),
    petId: UUID | None = Query(None),
    status: NotificationStatus | None = Query(None),
    due: bool = Query(False, description="Only pending notifications whose time has come"),
) -> NotificationFilterQuery:
    return NotificationFilterQuery(eventId=eventId, petId=petId, status=status, due=due)


NotificationFilterDep = Annotated[NotificationFilterQuery, Depends(get_notification_filters)]
