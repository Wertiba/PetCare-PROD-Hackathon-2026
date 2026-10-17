from fastapi import UploadFile

from app.application.pets.interactors import photo_extension
from app.application.ports.photos import MAX_PHOTO_BYTES, PhotoUpload
from app.domain.pets.errors import FileTooLargeError, UnsupportedFileTypeError


async def read_photo(upload: UploadFile) -> PhotoUpload:
    photo_extension(upload.content_type)
    chunks: list[bytes] = []
    total = 0
    while chunk := await upload.read(64 * 1024):
        total += len(chunk)
        if total > MAX_PHOTO_BYTES:
            raise FileTooLargeError
        chunks.append(chunk)
    if total == 0:
        # An empty file is no image: storing it would leave the pet with a broken photo.
        raise UnsupportedFileTypeError
    return PhotoUpload(content=b"".join(chunks), content_type=upload.content_type)
