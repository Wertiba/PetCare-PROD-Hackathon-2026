from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, kw_only=True)
class GeneratedImage:
    content: bytes
    content_type: str
    extension: str


class AvatarGenerator(Protocol):
    async def generate(self, image: bytes, content_type: str, *, style: str | None = None) -> GeneratedImage: ...
