import re
from uuid import uuid4

import aioboto3
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError

from app.application.ports.photos import PhotoObject, PhotosGateway
from app.infra.config import S3Config

_CONTENT_TYPES = {".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


def create_s3_client(config: S3Config, *, public: bool = False):
    return aioboto3.Session().client(
        "s3",
        endpoint_url=config.public_endpoint_url if public else config.endpoint_url,
        region_name=config.region,
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
        config=AioConfig(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            connect_timeout=3,
            read_timeout=15,
            retries={"mode": "standard", "total_max_attempts": 3},
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )


class S3PhotosGateway(PhotosGateway):
    def __init__(self, client, signer, config: S3Config) -> None:
        self.client = client
        self.signer = signer
        self.config = config
        self.upload_ttl = config.upload_ttl

    @staticmethod
    def _validate_key(key: str) -> None:
        if not re.fullmatch(r"pets/(?:[0-9a-f-]{36}/(?:photo|avatar)/)?[0-9a-f-]{36}\.(jpe?g|png|webp)", key):
            raise ValueError("Invalid photo object key")

    async def save(self, content: bytes, extension: str) -> str:
        content_type = _CONTENT_TYPES[extension]
        key = f"pets/{uuid4()}{extension}"
        await self.client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
            CacheControl="private, no-store",
        )
        return key

    async def load(self, key: str) -> bytes:
        self._validate_key(key)
        response = await self.client.get_object(Bucket=self.config.bucket, Key=key)
        async with response["Body"] as body:
            return await body.read()

    async def delete(self, photo_url: str | None) -> None:
        if not photo_url:
            return
        self._validate_key(photo_url)
        await self.client.delete_object(Bucket=self.config.bucket, Key=photo_url)

    async def get_presigned_url(self, key: str) -> str:
        self._validate_key(key)
        return await self.signer.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.config.bucket, "Key": key},
            ExpiresIn=self.config.presigned_ttl,
            HttpMethod="GET",
        )

    async def get_presigned_upload_url(self, key: str, content_type: str) -> str:
        self._validate_key(key)
        return await self.signer.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.config.bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=self.config.upload_ttl,
            HttpMethod="PUT",
        )

    async def stat(self, key: str) -> PhotoObject | None:
        self._validate_key(key)
        try:
            response = await self.client.head_object(Bucket=self.config.bucket, Key=key)
        except ClientError as error:
            code = str(error.response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise
        return PhotoObject(size=int(response["ContentLength"]), content_type=response.get("ContentType"))

    async def read_head(self, key: str, length: int) -> bytes:
        self._validate_key(key)
        response = await self.client.get_object(Bucket=self.config.bucket, Key=key, Range=f"bytes=0-{length - 1}")
        async with response["Body"] as body:
            return await body.read()
