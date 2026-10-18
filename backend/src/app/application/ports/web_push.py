from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, kw_only=True)
class WebPushMessage:
    title: str
    body: str
    notification_id: str | None = None
    event_id: str | None = None
    pet_id: str | None = None
    url: str = "/"


class WebPushSender(Protocol):
    def configured(self) -> bool: ...

    def public_key(self) -> str: ...

    async def send(self, *, endpoint: str, p256dh: str, auth: str, message: WebPushMessage) -> None: ...
