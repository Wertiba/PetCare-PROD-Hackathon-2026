from datetime import UTC, datetime
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlsplit

import pytest
from aiobotocore.stub import AioStubber
from botocore.exceptions import ClientError
from botocore.stub import ANY

from app.application.ports.photos import PhotoObject
from app.infra.config import S3Config
from app.infra.photos.s3 import S3PhotosGateway, create_s3_client


@pytest.fixture
def s3_config():
    return S3Config(
        S3_ENDPOINT_URL="http://rustfs:9000",
        S3_PUBLIC_ENDPOINT_URL="https://petcare.example.com",
        S3_ACCESS_KEY="test-photos",
        S3_SECRET_KEY="test-photos-secret",
    )


@pytest.fixture
async def gateway(s3_config):
    async with create_s3_client(s3_config) as client, create_s3_client(s3_config, public=True) as signer:
        yield S3PhotosGateway(client, signer, s3_config)


async def test_upload_stores_an_object_key_and_signs_the_public_same_domain_url(gateway):
    with AioStubber(gateway.client) as stub:
        stub.add_response(
            "put_object",
            {},
            {
                "Bucket": "media",
                "Key": ANY,
                "Body": b"photo",
                "ContentType": "image/png",
                "CacheControl": "private, no-store",
            },
        )
        key = await gateway.save(b"photo", ".png")
        assert key.startswith("pets/") and key.endswith(".png")
        signed = urlsplit(await gateway.get_presigned_url(key))
        assert signed.scheme == "https"
        assert signed.netloc == "petcare.example.com"
        assert signed.path == f"/media/{key}"
        query = parse_qs(signed.query)
        assert query["X-Amz-Expires"] == ["604800"]
        assert query["X-Amz-SignedHeaders"] == ["host"]
        assert query["X-Amz-Credential"][0].startswith("test-photos/")
        assert "test-photos-secret" not in signed.query
        stub.assert_no_pending_responses()


async def test_urls_are_generated_fresh_instead_of_persisting_expiring_signatures(gateway, monkeypatch):
    key = "pets/00000000-0000-0000-0000-000000000001.jpg"
    monkeypatch.setattr("botocore.auth.get_current_datetime", lambda: datetime(2026, 10, 17, tzinfo=UTC))
    first = await gateway.get_presigned_url(key)
    monkeypatch.setattr("botocore.auth.get_current_datetime", lambda: datetime(2026, 10, 18, tzinfo=UTC))
    second = await gateway.get_presigned_url(key)
    assert first != second


async def test_delete_uses_the_key(gateway):
    key = "pets/00000000-0000-0000-0000-000000000001.jpg"
    with AioStubber(gateway.client) as stub:
        stub.add_response("delete_object", {}, {"Bucket": "media", "Key": key})
        await gateway.delete(key)
        await gateway.delete(None)
        stub.assert_no_pending_responses()


async def test_load_reads_the_original_photo_and_closes_the_body(gateway, monkeypatch):
    key = "pets/00000000-0000-0000-0000-000000000001.png"
    body = AsyncMock()
    body.__aenter__.return_value = body
    body.read.return_value = b"original-photo"
    get_object = AsyncMock(return_value={"Body": body})
    monkeypatch.setattr(gateway.client, "get_object", get_object)

    assert await gateway.load(key) == b"original-photo"
    get_object.assert_awaited_once_with(Bucket="media", Key=key)
    body.__aexit__.assert_awaited_once()


async def test_load_closes_the_body_when_reading_fails(gateway, monkeypatch):
    body = AsyncMock()
    body.__aenter__.return_value = body
    body.read.side_effect = RuntimeError("stream interrupted")
    monkeypatch.setattr(gateway.client, "get_object", AsyncMock(return_value={"Body": body}))

    with pytest.raises(RuntimeError, match="stream interrupted"):
        await gateway.load("pets/00000000-0000-0000-0000-000000000001.png")
    body.__aexit__.assert_awaited_once()


@pytest.mark.parametrize(
    "key",
    [
        "../secret",
        "pets/../../secret",
        "https://other.test/pet.png",
        "/other-bucket/pet.png",
        "/media/pets/old.png",
        "pets/00000000-0000-0000-0000-000000000001/photo/../../secret.png",
        "pets/00000000-0000-0000-0000-000000000001/other/00000000-0000-0000-0000-000000000002.png",
        "pets/00000000-0000-0000-0000-000000000001/avatar/00000000-0000-0000-0000-000000000002.svg",
    ],
)
async def test_invalid_keys_cannot_be_signed_or_deleted(gateway, key):
    with pytest.raises(ValueError, match="Invalid photo object key"):
        await gateway.get_presigned_url(key)
    with pytest.raises(ValueError, match="Invalid photo object key"):
        await gateway.get_presigned_upload_url(key, "image/png")
    with pytest.raises(ValueError, match="Invalid photo object key"):
        await gateway.delete(key)
    with pytest.raises(ValueError, match="Invalid photo object key"):
        await gateway.load(key)
    with pytest.raises(ValueError, match="Invalid photo object key"):
        await gateway.stat(key)
    with pytest.raises(ValueError, match="Invalid photo object key"):
        await gateway.read_head(key, 16)


async def test_presigned_upload_url_signs_content_type_on_the_public_host(gateway):
    key = "pets/00000000-0000-0000-0000-000000000001/photo/00000000-0000-0000-0000-000000000002.png"
    signed = urlsplit(await gateway.get_presigned_upload_url(key, "image/png"))
    assert signed.scheme == "https"
    assert signed.netloc == "petcare.example.com"
    assert signed.path == f"/media/{key}"
    query = parse_qs(signed.query)
    assert query["X-Amz-Expires"] == ["900"]
    assert set(query["X-Amz-SignedHeaders"][0].split(";")) == {"content-type", "host"}
    assert "test-photos-secret" not in signed.geturl()


async def test_stat_returns_size_and_content_type(gateway):
    key = "pets/00000000-0000-0000-0000-000000000001.png"
    with AioStubber(gateway.client) as stub:
        stub.add_response(
            "head_object",
            {"ContentLength": 42, "ContentType": "image/png"},
            {"Bucket": "media", "Key": key},
        )
        assert await gateway.stat(key) == PhotoObject(size=42, content_type="image/png")
        stub.assert_no_pending_responses()


@pytest.mark.parametrize("code", ["404", "NoSuchKey", "NotFound"])
async def test_stat_returns_none_when_the_object_is_missing(gateway, code):
    key = "pets/00000000-0000-0000-0000-000000000001.png"
    with AioStubber(gateway.client) as stub:
        stub.add_client_error(
            "head_object",
            service_error_code=code,
            service_message="Not Found",
            http_status_code=404,
            expected_params={"Bucket": "media", "Key": key},
        )
        assert await gateway.stat(key) is None
        stub.assert_no_pending_responses()


async def test_stat_reraises_other_client_errors(gateway):
    key = "pets/00000000-0000-0000-0000-000000000001.png"
    with AioStubber(gateway.client) as stub:
        stub.add_client_error(
            "head_object",
            service_error_code="AccessDenied",
            service_message="Access Denied",
            http_status_code=403,
            expected_params={"Bucket": "media", "Key": key},
        )
        with pytest.raises(ClientError):
            await gateway.stat(key)


async def test_read_head_requests_a_byte_range(gateway, monkeypatch):
    key = "pets/00000000-0000-0000-0000-000000000001.png"
    body = AsyncMock()
    body.__aenter__.return_value = body
    body.read.return_value = b"\x89PNG\r\n\x1a\nrest"
    get_object = AsyncMock(return_value={"Body": body})
    monkeypatch.setattr(gateway.client, "get_object", get_object)

    assert await gateway.read_head(key, 16) == b"\x89PNG\r\n\x1a\nrest"
    get_object.assert_awaited_once_with(Bucket="media", Key=key, Range="bytes=0-15")
    body.__aexit__.assert_awaited_once()


async def test_signing_failure_after_upload_cleans_up_the_new_object(client, auth, pet_id, monkeypatch):
    save = AsyncMock(return_value="pets/new-object.png")
    delete = AsyncMock()
    monkeypatch.setattr(S3PhotosGateway, "save", save)
    monkeypatch.setattr(S3PhotosGateway, "delete", delete)
    monkeypatch.setattr(S3PhotosGateway, "get_presigned_url", AsyncMock(side_effect=RuntimeError("signing failed")))
    with pytest.raises(RuntimeError, match="signing failed"):
        client.put(f"/api/v1/pets/{pet_id}/photo", headers=auth, files={"file": ("pet.png", b"photo", "image/png")})
    delete.assert_awaited_once_with("pets/new-object.png")
    assert client.get(f"/api/v1/pets/{pet_id}", headers=auth).json()["photoUrl"] is None
