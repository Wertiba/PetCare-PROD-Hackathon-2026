from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from app.infra.photos.di import build_photo_storage
from app.infra.photos.storage import LocalPhotoStorage, S3PhotoStorage


@pytest.mark.parametrize(
    "key",
    ["../secret", "pets/../../etc/passwd", "pets\\file.png", "/etc/passwd", "pets/foo..bar.png", ""],
)
async def test_local_storage_rejects_unsafe_keys(tmp_path, key):
    storage = LocalPhotoStorage(tmp_path)
    with pytest.raises(ValueError):
        await storage.save(key, b"x", "image/png")
    with pytest.raises(ValueError):
        await storage.load(key)
    with pytest.raises(ValueError):
        storage.url(key)
    with pytest.raises(ValueError):
        await storage.delete(key)


async def test_local_storage_roundtrip_and_ignores_missing(tmp_path):
    storage = LocalPhotoStorage(tmp_path)
    key = "pets/abc/photo/file.png"
    await storage.save(key, b"xyz", "image/png")
    assert (tmp_path / key).read_bytes() == b"xyz"
    assert await storage.load(key) == b"xyz"
    assert storage.url(key) == f"/media/{key}"
    assert storage.url(None) is None
    await storage.delete(None)
    await storage.delete("pets/missing/file.png")
    await storage.delete(key)
    assert not (tmp_path / key).exists()


def test_storage_backend_defaults_to_local(monkeypatch, tmp_path):
    monkeypatch.setattr("app.infra.config.settings.get", lambda _name, default="": default)
    monkeypatch.setattr("app.infra.photos.di.get_media_dir", lambda: tmp_path)
    storage = build_photo_storage()
    assert isinstance(storage, LocalPhotoStorage)
    assert storage.directory == tmp_path


def _s3_settings(public: str) -> dict[str, str]:
    return {
        "APP_STORAGE_BACKEND": "s3",
        "S3_ENDPOINT_URL": "http://minio:9000",
        "S3_PUBLIC_ENDPOINT_URL": public,
        "S3_REGION": "us-east-1",
        "S3_BUCKET": "petcare",
        "S3_ACCESS_KEY_ID": "key",
        "S3_SECRET_ACCESS_KEY": "secret",
        "S3_PRESIGN_EXPIRES": "900",
    }


def test_s3_backend_presigns_with_the_public_endpoint(monkeypatch):
    values = _s3_settings("http://localhost:9000")
    monkeypatch.setattr("app.infra.config.settings.get", lambda name, default="": values.get(name, default))
    storage = build_photo_storage()
    assert isinstance(storage, S3PhotoStorage)
    assert storage._client.meta.endpoint_url.rstrip("/") == "http://minio:9000"
    assert storage._public_client.meta.endpoint_url.rstrip("/") == "http://localhost:9000"
    url = storage.url("pets/a.png")
    assert url is not None
    assert url.startswith("http://localhost:9000/")
    assert "minio:9000" not in url
    assert "petcare/pets/a.png" in url
    assert "X-Amz-Expires=900" in url
    assert storage.url(None) is None


def test_s3_public_endpoint_falls_back_to_the_internal_one(monkeypatch):
    values = _s3_settings("")
    monkeypatch.setattr("app.infra.config.settings.get", lambda name, default="": values.get(name, default))
    storage = build_photo_storage()
    assert storage._public_client is storage._client
    url = storage.url("pets/a.png")
    assert url is not None
    assert url.startswith("http://minio:9000/")


async def test_s3_save_and_delete_use_the_client_and_ignore_missing():
    client = MagicMock()
    public = MagicMock()
    missing = ClientError({"Error": {"Code": "NoSuchKey", "Message": "missing"}}, "delete_object")
    client.delete_object.side_effect = [None, missing]
    storage = S3PhotoStorage(bucket="petcare", presign_expires=3600, client=client, public_client=public)
    await storage.save("pets/a.png", b"data", "image/png")
    client.put_object.assert_called_once_with(Bucket="petcare", Key="pets/a.png", Body=b"data", ContentType="image/png")
    await storage.delete(None)
    client.delete_object.assert_not_called()
    await storage.delete("pets/a.png")
    await storage.delete("missing")
    denied = ClientError({"Error": {"Code": "AccessDenied", "Message": "no"}}, "delete_object")
    client.delete_object.side_effect = denied
    with pytest.raises(ClientError):
        await storage.delete("secret")
