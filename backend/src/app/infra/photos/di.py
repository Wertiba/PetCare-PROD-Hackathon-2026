from dishka import Provider, Scope, provide

from app.application.ports.photos import PhotoStorage
from app.infra.config import get_media_dir, setting_text
from app.infra.photos.storage import LocalPhotoStorage, S3PhotoStorage, build_s3_client


def build_photo_storage() -> PhotoStorage:
    backend = (setting_text("APP_STORAGE_BACKEND") or "local").lower()
    if backend != "s3":
        return LocalPhotoStorage(get_media_dir())
    endpoint = setting_text("S3_ENDPOINT_URL")
    public = setting_text("S3_PUBLIC_ENDPOINT_URL") or endpoint
    region = setting_text("S3_REGION") or "us-east-1"
    access_key = setting_text("S3_ACCESS_KEY_ID")
    secret_key = setting_text("S3_SECRET_ACCESS_KEY")
    client = build_s3_client(
        endpoint_url=endpoint, region=region, access_key_id=access_key, secret_access_key=secret_key
    )
    public_client = (
        client
        if public == endpoint
        else build_s3_client(endpoint_url=public, region=region, access_key_id=access_key, secret_access_key=secret_key)
    )
    return S3PhotoStorage(
        bucket=setting_text("S3_BUCKET"),
        presign_expires=int(setting_text("S3_PRESIGN_EXPIRES") or "3600"),
        client=client,
        public_client=public_client,
    )


class PhotoProvider(Provider):
    @provide(scope=Scope.APP)
    def photos(self) -> PhotoStorage:
        return build_photo_storage()
