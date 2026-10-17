from dataclasses import dataclass
from typing import Any

from app.domain.events.ids import EventId
from app.domain.notifications.enums import NotificationStatus, NotificationType
from app.domain.notifications.ids import NotificationId
from app.domain.pets.ids import PetId


@dataclass(kw_only=True)
class NotificationCreateData:
    eventId: EventId
    type: NotificationType = NotificationType.APP
    status: NotificationStatus = NotificationStatus.PENDING
    time: float | None = None


@dataclass(kw_only=True)
class NotificationUpdateData:
    changes: dict[str, Any]


@dataclass(kw_only=True)
class NotificationResult:
    id: NotificationId
    eventId: EventId
    petId: PetId
    eventName: str
    type: NotificationType
    status: NotificationStatus
    time: float
    createdAt: float
