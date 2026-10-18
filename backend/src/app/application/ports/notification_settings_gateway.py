from typing import Protocol

from app.domain.notifications.settings import NotificationSettings
from app.domain.users.ids import UserId


class NotificationSettingsGateway(Protocol):
    async def get_by_user_id(self, user_id: UserId) -> NotificationSettings | None: ...
