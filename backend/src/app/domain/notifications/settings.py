from dataclasses import dataclass, field
from time import time
from uuid import UUID, uuid4

from app.domain.users.ids import UserId


@dataclass(eq=False, kw_only=True)
class NotificationSettings:
    user_id: UserId
    web_push_enabled: bool = False


@dataclass(eq=False, kw_only=True)
class WebPushSubscription:
    id: UUID = field(default_factory=uuid4)
    user_id: UserId
    endpoint: str
    p256dh: str
    auth: str
    created_at: float = field(default_factory=time)
