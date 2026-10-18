import uuid
from time import time
from urllib.parse import parse_qs, urlsplit

import pytest
from test_pets_endpoints import PNG_BYTES, _auth, _create_pet, _object_key, _register, _upload_photo

from app.application.ports.photos import MAX_PHOTO_BYTES
from app.infra.metrics import DOMAIN_EVENTS_TOTAL

JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 16
pytestmark = pytest.mark.req("5.1.3")


def _issue(client, pet_id, token, content_type="image/jpeg", size=len(JPEG_BYTES)):
    return client.post(
        f"/api/v1/pets/{pet_id}/photo/upload-url",
        json={"contentType": content_type, "size": size},
        headers=_auth(token),
    )


@pytest.mark.req("P.ACCESS")
def test_direct_photo_endpoints_require_a_token(client, pet_id):
    client.cookies.clear()
    body = {"contentType": "image/jpeg", "size": 10}
    assert client.post(f"/api/v1/pets/{pet_id}/photo/upload-url", json=body).status_code == 401
    assert client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": "pets/x"}).status_code == 401
    assert client.delete(f"/api/v1/pets/{pet_id}/photo").status_code == 401
    assert client.delete(f"/api/v1/pets/{pet_id}/avatar/generated").status_code == 401


@pytest.mark.req("7.1", "P.ACCESS")
def test_upload_url_rejects_bad_input_and_a_foreign_pet(client):
    _, owner = _register(client, login="owner")
    _, stranger = _register(client, login="stranger")
    pet_id = _create_pet(client, owner).json()["id"]
    bad_type = _issue(client, pet_id, owner, content_type="image/gif")
    assert bad_type.status_code == 415
    assert bad_type.json()["code"] == "UNSUPPORTED_FILE_TYPE"
    too_big = _issue(client, pet_id, owner, size=MAX_PHOTO_BYTES + 1)
    assert too_big.status_code == 413
    assert too_big.json()["code"] == "FILE_TOO_LARGE"
    zero = _issue(client, pet_id, owner, size=0)
    assert zero.status_code == 422
    assert "size" in [err["field"] for err in zero.json()["fieldErrors"]]
    foreign = _issue(client, pet_id, stranger)
    assert foreign.status_code == 404
    assert foreign.json()["code"] == "NOT_FOUND"
    assert foreign.json()["message"] == "Pet not found"


def test_upload_url_returns_a_presigned_put(client, photo_objects):
    _, token = _register(client)
    created = _create_pet(client, token)
    assert created.status_code == 201
    pet = created.json()
    assert pet["photoUrl"] is None
    pet_id = pet["id"]
    issued_counter = DOMAIN_EVENTS_TOTAL.labels(entity="pet", action="photo_upload_url_issued")
    before = issued_counter._value.get()
    started = time()
    issued = _issue(client, pet_id, token, content_type="Image/JPEG; charset=binary", size=len(JPEG_BYTES))
    assert issued.status_code == 200, issued.text
    body = issued.json()
    assert body["key"].startswith(f"pets/{pet_id}/photo/")
    assert body["key"].endswith(".jpg")
    assert body["method"] == "PUT"
    assert body["headers"] == {"Content-Type": "image/jpeg"}
    assert body["maxBytes"] == MAX_PHOTO_BYTES
    assert started + 900 <= body["expiresAt"] <= time() + 900
    signed = urlsplit(body["uploadUrl"])
    assert signed.scheme == "https"
    assert signed.netloc == "testserver"
    assert signed.path == f"/media/{body['key']}"
    query = parse_qs(signed.query)
    assert "X-Amz-Signature" in query
    assert query["X-Amz-Expires"] == ["900"]
    assert "content-type" in query["X-Amz-SignedHeaders"][0].split(";")
    assert "test-photos-secret" not in body["uploadUrl"]
    assert body["key"] not in photo_objects
    assert client.get(f"/api/v1/pets/{pet_id}", headers=_auth(token)).json()["photoUrl"] is None
    assert issued_counter._value.get() == before + 1


def test_confirm_replaces_photo_and_rejects_foreign_or_avatar_keys(client, photo_objects):
    _, owner = _register(client, login="owner")
    _, stranger = _register(client, login="stranger")
    pet_id = _create_pet(client, owner).json()["id"]
    headers = _auth(owner)
    uploaded = _upload_photo(client, pet_id, owner)
    generated = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "generated"}, headers=headers)
    old_photo = _object_key(uploaded.json()["photoUrl"])
    old_avatar = _object_key(generated.json()["generatedAvatarUrl"])
    issued = _issue(client, pet_id, owner, content_type="image/jpeg", size=len(JPEG_BYTES))
    key = issued.json()["key"]
    photo_objects[key] = JPEG_BYTES
    uploaded_counter = DOMAIN_EVENTS_TOTAL.labels(entity="pet", action="photo_uploaded")
    before = uploaded_counter._value.get()
    confirmed = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": key}, headers=headers)
    assert confirmed.status_code == 200, confirmed.text
    body = confirmed.json()
    assert _object_key(body["photoUrl"]) == key
    assert body["generatedAvatarUrl"] is None
    assert body["avatarSource"] == "photo"
    assert body["avatarUrl"] == body["photoUrl"]
    assert old_photo not in photo_objects
    assert old_avatar not in photo_objects
    assert photo_objects[key] == JPEG_BYTES
    assert uploaded_counter._value.get() == before + 1

    foreign_key = f"pets/{uuid.uuid4()}/photo/{uuid.uuid4()}.png"
    photo_objects[foreign_key] = PNG_BYTES
    foreign = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": foreign_key}, headers=headers)
    assert foreign.status_code == 422
    assert foreign.json()["code"] == "PHOTO_UPLOAD_NOT_FOUND"
    assert foreign.json()["message"] == "Uploaded photo not found"
    assert foreign.json()["details"] == {"field": "key"}
    assert foreign_key in photo_objects
    avatar_key = f"pets/{pet_id}/avatar/{uuid.uuid4()}.png"
    photo_objects[avatar_key] = PNG_BYTES
    avatar = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": avatar_key}, headers=headers)
    assert avatar.status_code == 422
    assert avatar.json()["code"] == "PHOTO_UPLOAD_NOT_FOUND"
    assert avatar_key in photo_objects
    assert (
        client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": key}, headers=_auth(stranger)).status_code
        == 404
    )


def test_confirm_rejects_missing_oversized_and_mismatched_objects(client, photo_objects):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    missing_key = f"pets/{pet_id}/photo/{uuid.uuid4()}.png"
    missing = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": missing_key}, headers=headers)
    assert missing.status_code == 422
    assert missing.json()["code"] == "PHOTO_UPLOAD_NOT_FOUND"
    assert client.get(f"/api/v1/pets/{pet_id}", headers=headers).json()["photoUrl"] is None

    oversized = _issue(client, pet_id, token, content_type="image/png", size=len(PNG_BYTES)).json()["key"]
    photo_objects[oversized] = b"x" * (MAX_PHOTO_BYTES + 1)
    too_big = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": oversized}, headers=headers)
    assert too_big.status_code == 413
    assert too_big.json()["code"] == "FILE_TOO_LARGE"
    assert oversized not in photo_objects

    mismatched = _issue(client, pet_id, token, content_type="image/png", size=len(JPEG_BYTES)).json()["key"]
    photo_objects[mismatched] = JPEG_BYTES
    wrong = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": mismatched}, headers=headers)
    assert wrong.status_code == 415
    assert wrong.json()["code"] == "UNSUPPORTED_FILE_TYPE"
    assert mismatched not in photo_objects
    assert client.get(f"/api/v1/pets/{pet_id}", headers=headers).json()["photoUrl"] is None


def test_confirming_the_current_photo_key_is_idempotent(client, photo_objects, generator):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    issued = _issue(client, pet_id, token, content_type="image/png", size=len(PNG_BYTES))
    key = issued.json()["key"]
    photo_objects[key] = PNG_BYTES
    first = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": key}, headers=headers)
    assert first.status_code == 200, first.text
    generated = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    assert generated.status_code == 200, generated.text
    avatar_key = _object_key(generated.json()["generatedAvatarUrl"])
    again = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": key}, headers=headers)
    assert again.status_code == 200, again.text
    body = again.json()
    assert _object_key(body["photoUrl"]) == key
    assert _object_key(body["generatedAvatarUrl"]) == avatar_key
    assert body["avatarSource"] == "photo"
    assert photo_objects[key] == PNG_BYTES
    assert avatar_key in photo_objects
    assert generator.calls == [(PNG_BYTES, "image/png")]


@pytest.mark.req("P.ACCESS")
def test_delete_photo_removes_both_objects_and_is_idempotent(client, photo_objects):
    _, owner = _register(client, login="owner")
    _, stranger = _register(client, login="stranger")
    pet_id = _create_pet(client, owner).json()["id"]
    headers = _auth(owner)
    issued = _issue(client, pet_id, owner, content_type="image/png", size=len(PNG_BYTES))
    key = issued.json()["key"]
    photo_objects[key] = PNG_BYTES
    assert client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": key}, headers=headers).status_code == 200
    generated = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    avatar_key = _object_key(generated.json()["generatedAvatarUrl"])
    deleted_counter = DOMAIN_EVENTS_TOTAL.labels(entity="pet", action="photo_deleted")
    before = deleted_counter._value.get()
    deleted = client.delete(f"/api/v1/pets/{pet_id}/photo", headers=headers)
    assert deleted.status_code == 200, deleted.text
    body = deleted.json()
    assert body["photoUrl"] is None
    assert body["generatedAvatarUrl"] is None
    assert body["avatarUrl"] is None
    assert body["avatarSource"] == "photo"
    assert key not in photo_objects
    assert avatar_key not in photo_objects
    assert deleted_counter._value.get() == before + 1
    again = client.delete(f"/api/v1/pets/{pet_id}/photo", headers=headers)
    assert again.status_code == 200
    assert again.json()["photoUrl"] is None
    assert photo_objects == {}
    foreign = client.delete(f"/api/v1/pets/{pet_id}/photo", headers=_auth(stranger))
    assert foreign.status_code == 404
    assert foreign.json()["code"] == "NOT_FOUND"


def test_delete_generated_avatar_switches_the_source_back_to_the_photo(client, photo_objects):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    issued = _issue(client, pet_id, token, content_type="image/png", size=len(PNG_BYTES))
    key = issued.json()["key"]
    photo_objects[key] = PNG_BYTES
    client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": key}, headers=headers)
    generated = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    avatar_key = _object_key(generated.json()["generatedAvatarUrl"])
    client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "generated"}, headers=headers)
    removed_counter = DOMAIN_EVENTS_TOTAL.labels(entity="pet", action="generated_avatar_deleted")
    before = removed_counter._value.get()
    removed = client.delete(f"/api/v1/pets/{pet_id}/avatar/generated", headers=headers)
    assert removed.status_code == 200, removed.text
    body = removed.json()
    assert body["avatarSource"] == "photo"
    assert body["generatedAvatarUrl"] is None
    assert _object_key(body["photoUrl"]) == key
    assert body["avatarUrl"] == body["photoUrl"]
    assert avatar_key not in photo_objects
    assert photo_objects[key] == PNG_BYTES
    assert removed_counter._value.get() == before + 1
    again = client.delete(f"/api/v1/pets/{pet_id}/avatar/generated", headers=headers)
    assert again.status_code == 200
    assert _object_key(again.json()["photoUrl"]) == key
    assert again.json()["avatarSource"] == "photo"
    stranger = _register(client, login="stranger")[1]
    assert client.delete(f"/api/v1/pets/{pet_id}/avatar/generated", headers=_auth(stranger)).status_code == 404


def test_direct_upload_flow_can_skip_the_photo_and_then_use_it(client, photo_objects, generator):
    _, token = _register(client)
    headers = _auth(token)
    skipped = _create_pet(client, token, name="Без фото")
    assert skipped.status_code == 201
    assert skipped.json()["photoUrl"] is None
    assert skipped.json()["generatedAvatarUrl"] is None
    assert skipped.json()["avatarSource"] == "photo"

    pet_id = _create_pet(client, token, name="С фото").json()["id"]
    issued = _issue(client, pet_id, token, content_type="image/png", size=len(PNG_BYTES))
    assert issued.status_code == 200, issued.text
    key = issued.json()["key"]
    photo_objects[key] = PNG_BYTES
    confirmed = client.post(f"/api/v1/pets/{pet_id}/photo/confirm", json={"key": key}, headers=headers)
    assert confirmed.status_code == 200, confirmed.text
    assert _object_key(confirmed.json()["photoUrl"]) == key
    generated = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    assert generated.status_code == 200, generated.text
    assert generator.calls == [(PNG_BYTES, "image/png")]
    selected = client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "generated"}, headers=headers)
    assert selected.status_code == 200, selected.text
    assert selected.json()["avatarSource"] == "generated"
    assert selected.json()["avatarUrl"] == selected.json()["generatedAvatarUrl"]
    removed = client.delete(f"/api/v1/pets/{pet_id}/avatar/generated", headers=headers)
    assert removed.status_code == 200, removed.text
    assert removed.json()["avatarSource"] == "photo"
    assert removed.json()["generatedAvatarUrl"] is None
    assert removed.json()["avatarUrl"] == removed.json()["photoUrl"]
    assert client.get(f"/api/v1/pets/{skipped.json()['id']}", headers=headers).json()["photoUrl"] is None
