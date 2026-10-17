from functools import partial
from pathlib import Path
from typing import Any

import anyio
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.application.ports.photos import PhotoStorage

_MISSING_CODES = {"404", "NoSuchKey", "NotFound"}


def build_s3_client(*, endpoint_url: str, region: str, access_key_id: str, secret_access_key: str) -> Any:
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url or None,
        region_name=region,
        aws_access_key_id=access_key_id or None,
        aws_secret_access_key=secret_access_key or None,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def _is_missing(exc: ClientError) -> bool:
    error = exc.response.get("Error", {})
    status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    return str(error.get("Code", "")) in _MISSING_CODES or status == 404


class LocalPhotoStorage(PhotoStorage):
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def _path(self, key: str) -> Path:
        if not key or ".." in key or "\\" in key or key.startswith("/") or Path(key).is_absolute():
            raise ValueError("invalid object key")
        root = self.directory.resolve()
        path = (self.directory / key).resolve()
        if path != root and root not in path.parents:
            raise ValueError("invalid object key")
        return path

    async def save(self, key: str, content: bytes, content_type: str) -> None:
        path = anyio.Path(self._path(key))
        await path.parent.mkdir(parents=True, exist_ok=True)
        await path.write_bytes(content)

    async def load(self, key: str) -> bytes:
        return await anyio.Path(self._path(key)).read_bytes()

    async def delete(self, key: str | None) -> None:
        if key is None:
            return
        await anyio.Path(self._path(key)).unlink(missing_ok=True)

    def url(self, key: str | None) -> str | None:
        if key is None:
            return None
        self._path(key)
        return f"/media/{key}"


class S3PhotoStorage(PhotoStorage):
    def __init__(self, *, bucket: str, presign_expires: int, client: Any, public_client: Any) -> None:
        self.bucket = bucket
        self.presign_expires = presign_expires
        self._client = client
        self._public_client = public_client

    async def save(self, key: str, content: bytes, content_type: str) -> None:
        await anyio.to_thread.run_sync(
            partial(self._client.put_object, Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)
        )

    async def load(self, key: str) -> bytes:
        def _load() -> bytes:
            response = self._client.get_object(Bucket=self.bucket, Key=key)
            body = response["Body"]
            try:
                return body.read()
            finally:
                body.close()

        return await anyio.to_thread.run_sync(_load)

    async def delete(self, key: str | None) -> None:
        if key is None:
            return

        def _delete() -> None:
            try:
                self._client.delete_object(Bucket=self.bucket, Key=key)
            except ClientError as exc:
                if _is_missing(exc):
                    return
                raise

        await anyio.to_thread.run_sync(_delete)

    def url(self, key: str | None) -> str | None:
        if key is None:
            return None
        return self._public_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=self.presign_expires,
        )
