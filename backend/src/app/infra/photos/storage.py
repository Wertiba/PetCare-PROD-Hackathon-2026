from pathlib import Path
from uuid import uuid4

import anyio

from app.application.ports.photos import PhotoStorage

_PHOTO_URL_PREFIX = "/media/pets/"


class LocalPhotoStorage(PhotoStorage):
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    async def save(self, content: bytes, extension: str) -> str:
        filename = f"{uuid4()}{extension}"
        directory = anyio.Path(self.directory / "pets")
        await directory.mkdir(parents=True, exist_ok=True)
        await (directory / filename).write_bytes(content)
        return f"{_PHOTO_URL_PREFIX}{filename}"

    async def delete(self, photo_url: str | None) -> None:
        if not photo_url or not photo_url.startswith(_PHOTO_URL_PREFIX):
            return
        name = photo_url.removeprefix(_PHOTO_URL_PREFIX)
        if not name or "/" in name or "\\" in name or ".." in name:
            return
        path = anyio.Path(self.directory / "pets" / name)
        await path.unlink(missing_ok=True)
