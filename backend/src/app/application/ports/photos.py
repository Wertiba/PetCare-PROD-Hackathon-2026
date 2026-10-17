from dataclasses import dataclass
from typing import Protocol

MAX_PHOTO_BYTES = 5 * 1024 * 1024


@dataclass
class PhotoUpload:
    content: bytes
    content_type: str | None


class PhotoStorage(Protocol):
    async def save(self, key: str, content: bytes, content_type: str) -> None: ...
    async def load(self, key: str) -> bytes: ...
    async def delete(self, key: str | None) -> None: ...
    def url(self, key: str | None) -> str | None: ...
