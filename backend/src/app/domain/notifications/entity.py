from dataclasses import dataclass, field
from time import time
from uuid import uuid4

from app.domain.events.entity import Event
from app.domain.events.ids import EventId
from app.domain.notifications.enums import NotificationStatus, NotificationType
from app.domain.notifications.ids import NotificationId


@dataclass(eq=False, kw_only=True)
class Notification:
    id: NotificationId = field(default_factory=uuid4)
    event_id: EventId
    type: NotificationType
    status: NotificationStatus
    time: float
    created_at: float = field(default_factory=time)
    event: Event
