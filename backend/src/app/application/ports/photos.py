from dataclasses import dataclass
from typing import Protocol

MAX_PHOTO_BYTES = 5 * 1024 * 1024


@dataclass
class PhotoUpload:
    content: bytes
    content_type: str | None


class PhotosGateway(Protocol):
    async def save(self, content: bytes, extension: str) -> str: ...
    async def load(self, key: str) -> bytes: ...
    async def delete(self, photo_url: str | None) -> None: ...
    async def get_presigned_url(self, key: str) -> str: ...
