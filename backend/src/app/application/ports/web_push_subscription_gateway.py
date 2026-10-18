from typing import Protocol

from app.domain.notifications.settings import WebPushSubscription
from app.domain.users.ids import UserId


class WebPushSubscriptionGateway(Protocol):
    async def list_by_user_id(self, user_id: UserId) -> list[WebPushSubscription]: ...

    async def get_by_endpoint(self, endpoint: str) -> WebPushSubscription | None: ...
