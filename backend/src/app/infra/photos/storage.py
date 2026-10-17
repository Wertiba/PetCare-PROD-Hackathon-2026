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

    def _path(self, photo_url: str | None) -> anyio.Path | None:
        """The file behind one of our own photo URLs; None for anything that could escape the directory."""
        if not photo_url or not photo_url.startswith(_PHOTO_URL_PREFIX):
            return None
        name = photo_url.removeprefix(_PHOTO_URL_PREFIX)
        if not name or "/" in name or "\\" in name or ".." in name:
            return None
        return anyio.Path(self.directory / "pets" / name)

    async def delete(self, photo_url: str | None) -> None:
        path = self._path(photo_url)
        if path is not None:
            await path.unlink(missing_ok=True)

    async def read(self, photo_url: str | None) -> bytes | None:
        path = self._path(photo_url)
        if path is None or not await path.is_file():
            return None
        return await path.read_bytes()
