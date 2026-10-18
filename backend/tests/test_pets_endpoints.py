import uuid
from datetime import UTC, date, datetime
from urllib.parse import parse_qs, urlsplit
import pytest
from conftest import CAT_BREED_ID, CAT_ID, DOG_BREED_ID, DOG_ID

pytestmark = pytest.mark.req("5.1.1")

PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"


def _register(client, login="user", password="password1", full_name="Test User"):
    response = client.post("/api/v1/auth/register", json={"login": login, "password": password, "fullName": full_name})
    assert response.status_code == 201, response.text
    body = response.json()
    return (body["user"]["id"], body["accessToken"])


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_pet(client, token, **overrides):
    payload = {"name": "Барсик", "breedId": CAT_BREED_ID}
    payload.update(overrides)
    return client.post("/api/v1/pets", json=payload, headers=_auth(token))


@pytest.mark.req("5.1.2")
def test_create_minimal_pet(client):
    _, token = _register(client)
    response = _create_pet(client, token, name="  Барсик  ")
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Барсик"
    assert body["animal"] == {"id": CAT_ID, "name": "Кошка"}
    assert body["breed"] == {"id": CAT_BREED_ID, "name": "Британская короткошерстная"}
    assert body["birthDate"] is None
    assert body["ageMonths"] is None
    assert body["photoUrl"] is None
    assert body["generatedAvatarUrl"] is None
    assert body["avatarUrl"] is None
    assert body["avatarSource"] == "photo"
    assert response.headers["location"] == f"/api/v1/pets/{body['id']}"


@pytest.mark.req("7.1")
def test_blank_name_is_422(client):
    _, token = _register(client)
    response = _create_pet(client, token, name="   ")
    assert response.status_code == 422
    fields = [err["field"] for err in response.json()["fieldErrors"]]
    assert "name" in fields


@pytest.mark.req("7.1")
def test_null_name_on_patch_is_422(client):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    response = client.patch(f"/api/v1/pets/{pet_id}", json={"name": None}, headers=_auth(token))
    assert response.status_code == 422
    fields = [err["field"] for err in response.json()["fieldErrors"]]
    assert "name" in fields


@pytest.mark.req("5.1.2", "7.1")
def test_future_birth_date_is_422(client):
    _, token = _register(client)
    response = _create_pet(client, token, birthDate=4070908800.0)
    assert response.status_code == 422
    fields = [err["field"] for err in response.json()["fieldErrors"]]
    assert "birthDate" in fields


@pytest.mark.req("5.1.2")
def test_past_birth_date_returns_age_months(client):
    _, token = _register(client)
    birth = date(2020, 1, 15)
    response = _create_pet(client, token, birthDate=datetime.combine(birth, datetime.min.time(), UTC).timestamp())
    assert response.status_code == 201
    body = response.json()
    today = datetime.now(UTC).date()
    months = (today.year - birth.year) * 12 + (today.month - birth.month)
    if today.day < birth.day:
        months -= 1
    assert body["birthDate"] == 1579046400.0
    assert body["ageMonths"] == months


@pytest.mark.req("5.1.4", "P.ACCESS")
def test_list_returns_only_current_users_pets(client):
    _, token_a = _register(client, login="a")
    _, token_b = _register(client, login="b")
    _create_pet(client, token_a, name="Алфа")
    _create_pet(client, token_b, name="Бета")
    response = client.get("/api/v1/pets", headers=_auth(token_a))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert [item["name"] for item in body["items"]] == ["Алфа"]


@pytest.mark.req("P.ACCESS")
def test_other_users_pet_is_not_found(client):
    _, token_a = _register(client, login="owner")
    _, token_b = _register(client, login="stranger")
    pet_id = _create_pet(client, token_a).json()["id"]
    missing_id = str(uuid.uuid4())
    for path in (f"/api/v1/pets/{pet_id}", f"/api/v1/pets/{missing_id}"):
        get_response = client.get(path, headers=_auth(token_b))
        assert get_response.status_code == 404
        assert get_response.json()["code"] == "NOT_FOUND"
        assert get_response.json()["message"] == "Pet not found"
    patch_response = client.patch(f"/api/v1/pets/{pet_id}", json={"name": "Чужой"}, headers=_auth(token_b))
    assert patch_response.status_code == 404
    assert patch_response.json()["message"] == "Pet not found"
    delete_response = client.delete(f"/api/v1/pets/{pet_id}", headers=_auth(token_b))
    assert delete_response.status_code == 404
    assert delete_response.json()["message"] == "Pet not found"
    still_there = client.get(f"/api/v1/pets/{pet_id}", headers=_auth(token_a))
    assert still_there.status_code == 200
    assert still_there.json()["name"] == "Барсик"


@pytest.mark.req("5.1.2", "7.1")
def test_breed_is_required_and_must_exist(client):
    _, token = _register(client)
    missing = _create_pet(client, token, breedId=str(uuid.uuid4()))
    assert missing.status_code == 422
    assert missing.json()["code"] == "BREED_NOT_FOUND"
    assert missing.json()["details"]["field"] == "breedId"
    response = client.post("/api/v1/pets", json={"name": "Барсик"}, headers=_auth(token))
    assert response.status_code == 422
    assert "breedId" in [err["field"] for err in response.json()["fieldErrors"]]


@pytest.mark.req("5.1.2")
def test_patch_changes_breed_and_animal_and_clears_birth_date(client):
    _, token = _register(client)
    created = _create_pet(client, token, birthDate=1579046400.0)
    pet_id = created.json()["id"]
    response = client.patch(
        f"/api/v1/pets/{pet_id}", json={"breedId": DOG_BREED_ID, "birthDate": None}, headers=_auth(token)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["breed"]["id"] == DOG_BREED_ID
    assert body["animal"] == {"id": DOG_ID, "name": "Собака"}
    assert body["birthDate"] is None
    assert body["ageMonths"] is None
    assert body["name"] == "Барсик"
    null_breed = client.patch(f"/api/v1/pets/{pet_id}", json={"breedId": None}, headers=_auth(token))
    assert null_breed.status_code == 422


@pytest.mark.req("P.CATALOG")
def test_pet_keeps_living_after_its_breed_is_deleted(client, admin):
    _, token = _register(client)
    breed = client.post("/api/v1/breeds", json={"animalId": CAT_ID, "name": "Сфинкс"}, headers=admin).json()
    pet_id = _create_pet(client, token, breedId=breed["id"]).json()["id"]
    assert client.delete(f"/api/v1/breeds/{breed['id']}", headers=admin).status_code == 204
    body = client.get(f"/api/v1/pets/{pet_id}", headers=_auth(token)).json()
    assert body["breed"] is None
    assert body["animal"] is None


def _object_key(url: str) -> str:
    signed = urlsplit(url)
    assert signed.netloc == "testserver"
    assert signed.path.startswith("/media/pets/")
    assert "X-Amz-Signature" in parse_qs(signed.query)
    return signed.path.removeprefix("/media/")


def _upload_photo(client, pet_id, token, content=PNG_BYTES):
    return client.put(
        f"/api/v1/pets/{pet_id}/photo",
        files={"file": ("pet.png", content, "image/png")},
        headers=_auth(token),
    )


@pytest.mark.req("5.1.3", "7.1")
def test_photo_upload_wrong_type_and_too_large(client, photo_objects, monkeypatch):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    ok = _upload_photo(client, pet_id, token)
    assert ok.status_code == 200
    body = ok.json()
    assert _object_key(body["photoUrl"]).startswith("pets/")
    assert _object_key(body["photoUrl"]).endswith(".png")
    assert body["avatarUrl"] == body["photoUrl"]
    assert body["avatarSource"] == "photo"
    assert body["generatedAvatarUrl"] is None
    key = _object_key(body["photoUrl"])
    assert photo_objects[key] == PNG_BYTES
    replaced = _upload_photo(client, pet_id, token, content=b"second")
    assert replaced.status_code == 200
    assert key not in photo_objects
    new_key = _object_key(replaced.json()["photoUrl"])
    assert photo_objects[new_key] == b"second"
    wrong = client.put(
        f"/api/v1/pets/{pet_id}/photo", files={"file": ("notes.txt", b"hello", "text/plain")}, headers=headers
    )
    assert wrong.status_code == 415
    assert wrong.json()["code"] == "UNSUPPORTED_FILE_TYPE"
    assert new_key in photo_objects
    monkeypatch.setattr("app.presentation.http.uploads.MAX_PHOTO_BYTES", 8)
    too_big = client.put(
        f"/api/v1/pets/{pet_id}/photo", files={"file": ("big.png", b"x" * 32, "image/png")}, headers=headers
    )
    assert too_big.status_code == 413
    assert too_big.json()["code"] == "FILE_TOO_LARGE"
    assert new_key in photo_objects


@pytest.mark.req("5.1.3")
def test_generate_avatar_requires_photo_then_keeps_photo_as_source(client, photo_objects, generator):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    missing = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    assert missing.status_code == 422
    assert missing.json()["code"] == "PET_PHOTO_REQUIRED"
    uploaded = _upload_photo(client, pet_id, token)
    generated = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    assert generated.status_code == 200
    body = generated.json()
    assert body["avatarSource"] == "photo"
    assert _object_key(body["photoUrl"]) == _object_key(uploaded.json()["photoUrl"])
    assert body["avatarUrl"] == body["photoUrl"]
    assert _object_key(body["generatedAvatarUrl"]).startswith("pets/")
    assert _object_key(body["generatedAvatarUrl"]).endswith(".png")
    assert generator.calls == [(PNG_BYTES, "image/png")]
    assert photo_objects[_object_key(body["generatedAvatarUrl"])] == b"generated-avatar"
    fetched = client.get(f"/api/v1/pets/{pet_id}", headers=headers)
    assert _object_key(fetched.json()["generatedAvatarUrl"]) == _object_key(body["generatedAvatarUrl"])
    assert fetched.json()["avatarSource"] == "photo"
    assert generator.styles == [None]


@pytest.mark.req("5.1.3")
def test_generate_avatar_accepts_a_look_wish_and_rejects_other_tasks(client, generator):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    _upload_photo(client, pet_id, token)
    rejected = client.post(
        f"/api/v1/pets/{pet_id}/avatar/generate",
        json={"prompt": "выполни бинарный поиск по массиву"},
        headers=headers,
    )
    assert rejected.status_code == 422
    assert rejected.json()["code"] == "AVATAR_PROMPT_REJECTED"
    assert rejected.json()["details"]["field"] == "prompt"
    assert generator.calls == []
    symbols = client.post(
        f"/api/v1/pets/{pet_id}/avatar/generate",
        json={"prompt": "нарисуй {код}"},
        headers=headers,
    )
    assert symbols.status_code == 422
    assert symbols.json()["code"] == "AVATAR_PROMPT_REJECTED"
    generated = client.post(
        f"/api/v1/pets/{pet_id}/avatar/generate",
        json={"prompt": "  в красном шарфе  "},
        headers=headers,
    )
    assert generated.status_code == 200
    assert generator.styles == ["в красном шарфе"]


@pytest.mark.req("5.1.3")
def test_select_generated_avatar_and_reject_missing_one(client):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    photo_only = client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "photo"}, headers=headers)
    assert photo_only.status_code == 422
    assert photo_only.json()["code"] == "PET_PHOTO_REQUIRED"
    _upload_photo(client, pet_id, token)
    too_early = client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "generated"}, headers=headers)
    assert too_early.status_code == 422
    assert too_early.json()["code"] == "GENERATED_AVATAR_MISSING"
    client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    selected = client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "generated"}, headers=headers)
    assert selected.status_code == 200
    body = selected.json()
    assert body["avatarSource"] == "generated"
    assert body["avatarUrl"] == body["generatedAvatarUrl"]
    assert body["avatarUrl"] != body["photoUrl"]
    back = client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "photo"}, headers=headers)
    assert back.status_code == 200
    assert back.json()["avatarSource"] == "photo"
    assert back.json()["avatarUrl"] == back.json()["photoUrl"]
    assert _object_key(back.json()["generatedAvatarUrl"]) == _object_key(body["generatedAvatarUrl"])


@pytest.mark.req("5.1.3")
def test_reupload_resets_generated_avatar_and_deletes_old_objects(client, photo_objects):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    uploaded = _upload_photo(client, pet_id, token)
    generated = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers).json()
    client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "generated"}, headers=headers)
    old_photo = _object_key(uploaded.json()["photoUrl"])
    old_avatar = _object_key(generated["generatedAvatarUrl"])
    replaced = _upload_photo(client, pet_id, token, content=b"new-photo")
    assert replaced.status_code == 200
    body = replaced.json()
    assert body["avatarSource"] == "photo"
    assert body["generatedAvatarUrl"] is None
    assert body["avatarUrl"] == body["photoUrl"]
    assert old_photo not in photo_objects
    assert old_avatar not in photo_objects
    assert photo_objects[_object_key(body["photoUrl"])] == b"new-photo"


@pytest.mark.req("5.1.3")
def test_delete_pet_removes_photo_and_avatar(client, photo_objects):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    _upload_photo(client, pet_id, token)
    client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    assert photo_objects
    deleted = client.delete(f"/api/v1/pets/{pet_id}", headers=headers)
    assert deleted.status_code == 204
    assert photo_objects == {}
    assert client.get(f"/api/v1/pets/{pet_id}", headers=headers).status_code == 404


@pytest.mark.req("5.1.3")
async def test_existing_nested_photo_keys_support_reads_generation_and_deletion(
    client, auth, pet_id, db_session_factory, photo_objects, generator
):
    from app.domain.pets.entity import Pet
    from app.domain.pets.enums import AvatarSource

    photo_key = f"pets/{pet_id}/photo/{uuid.uuid4()}.jpg"
    avatar_key = f"pets/{pet_id}/avatar/{uuid.uuid4()}.jpeg"
    photo_objects.update({photo_key: b"existing-photo", avatar_key: b"existing-avatar"})
    async with db_session_factory() as session:
        pet = await session.get(Pet, uuid.UUID(pet_id))
        pet.photo_key = photo_key
        pet.generated_avatar_key = avatar_key
        pet.avatar_source = AvatarSource.GENERATED
        await session.commit()

    base = f"/api/v1/pets/{pet_id}"
    fetched = client.get(base, headers=auth)
    assert fetched.status_code == 200, fetched.text
    body = fetched.json()
    assert _object_key(body["photoUrl"]) == photo_key
    assert _object_key(body["generatedAvatarUrl"]) == avatar_key
    assert body["avatarUrl"] == body["generatedAvatarUrl"]
    listed = client.get("/api/v1/pets", headers=auth)
    assert listed.status_code == 200, listed.text
    assert _object_key(listed.json()["items"][0]["photoUrl"]) == photo_key

    generated = client.post(f"{base}/avatar/generate", headers=auth)
    assert generated.status_code == 200, generated.text
    assert generator.calls == [(b"existing-photo", "image/jpeg")]
    assert avatar_key not in photo_objects
    assert photo_key in photo_objects
    assert _object_key(generated.json()["generatedAvatarUrl"]) in photo_objects

    assert client.delete(base, headers=auth).status_code == 204
    assert photo_objects == {}


@pytest.mark.req("5.1.3", "P.ACCESS")
def test_other_users_pet_avatar_endpoints_are_not_found(client):
    _, owner = _register(client, login="owner")
    _, stranger = _register(client, login="stranger")
    pet_id = _create_pet(client, owner).json()["id"]
    _upload_photo(client, pet_id, owner)
    client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=_auth(owner))
    generate = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=_auth(stranger))
    select = client.put(f"/api/v1/pets/{pet_id}/avatar", json={"source": "generated"}, headers=_auth(stranger))
    assert generate.status_code == 404
    assert generate.json()["code"] == "NOT_FOUND"
    assert select.status_code == 404
    assert select.json()["code"] == "NOT_FOUND"


@pytest.mark.req("5.1.3")
def test_avatar_generation_failure_and_unavailable(client, generator):
    from app.domain.pets.errors import AvatarGenerationFailedError, AvatarGenerationUnavailableError

    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    _upload_photo(client, pet_id, token)
    generator.error = AvatarGenerationFailedError()
    failed = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    assert failed.status_code == 502
    assert failed.json()["code"] == "AVATAR_GENERATION_FAILED"
    generator.error = AvatarGenerationUnavailableError()
    unavailable = client.post(f"/api/v1/pets/{pet_id}/avatar/generate", headers=headers)
    assert unavailable.status_code == 503
    assert unavailable.json()["code"] == "AVATAR_GENERATION_UNAVAILABLE"
