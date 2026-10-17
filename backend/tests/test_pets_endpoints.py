import uuid
from datetime import UTC, date, datetime
import pytest
from conftest import CAT_BREED_ID, CAT_ID, DOG_BREED_ID, DOG_ID

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
    assert response.headers["location"] == f"/api/v1/pets/{body['id']}"


def test_blank_name_is_422(client):
    _, token = _register(client)
    response = _create_pet(client, token, name="   ")
    assert response.status_code == 422
    fields = [err["field"] for err in response.json()["fieldErrors"]]
    assert "name" in fields


def test_null_name_on_patch_is_422(client):
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    response = client.patch(f"/api/v1/pets/{pet_id}", json={"name": None}, headers=_auth(token))
    assert response.status_code == 422
    fields = [err["field"] for err in response.json()["fieldErrors"]]
    assert "name" in fields


def test_future_birth_date_is_422(client):
    _, token = _register(client)
    response = _create_pet(client, token, birthDate=4070908800.0)
    assert response.status_code == 422
    fields = [err["field"] for err in response.json()["fieldErrors"]]
    assert "birthDate" in fields


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


def test_breed_is_required_and_must_exist(client):
    _, token = _register(client)
    missing = _create_pet(client, token, breedId=str(uuid.uuid4()))
    assert missing.status_code == 422
    assert missing.json()["code"] == "BREED_NOT_FOUND"
    assert missing.json()["details"]["field"] == "breedId"
    response = client.post("/api/v1/pets", json={"name": "Барсик"}, headers=_auth(token))
    assert response.status_code == 422
    assert "breedId" in [err["field"] for err in response.json()["fieldErrors"]]


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


def test_pet_keeps_living_after_its_breed_is_deleted(client, admin):
    _, token = _register(client)
    breed = client.post("/api/v1/breeds", json={"animalId": CAT_ID, "name": "Сфинкс"}, headers=admin).json()
    pet_id = _create_pet(client, token, breedId=breed["id"]).json()["id"]
    assert client.delete(f"/api/v1/breeds/{breed['id']}", headers=admin).status_code == 204
    body = client.get(f"/api/v1/pets/{pet_id}", headers=_auth(token)).json()
    assert body["breed"] is None
    assert body["animal"] is None


def test_photo_upload_wrong_type_and_too_large(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.infra.photos.di.get_media_dir", lambda: tmp_path)
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    ok = client.put(
        f"/api/v1/pets/{pet_id}/photo", files={"file": ("pet.png", PNG_BYTES, "image/png")}, headers=headers
    )
    assert ok.status_code == 200
    photo_url = ok.json()["photoUrl"]
    assert photo_url.startswith("/media/pets/")
    assert photo_url.endswith(".png")
    stored = tmp_path / "pets" / photo_url.rsplit("/", 1)[-1]
    assert stored.is_file()
    assert stored.read_bytes() == PNG_BYTES
    replaced = client.put(
        f"/api/v1/pets/{pet_id}/photo", files={"file": ("pet2.png", PNG_BYTES, "image/png")}, headers=headers
    )
    assert replaced.status_code == 200
    assert not stored.exists()
    new_path = tmp_path / "pets" / replaced.json()["photoUrl"].rsplit("/", 1)[-1]
    assert new_path.is_file()
    wrong = client.put(
        f"/api/v1/pets/{pet_id}/photo", files={"file": ("notes.txt", b"hello", "text/plain")}, headers=headers
    )
    assert wrong.status_code == 415
    assert wrong.json()["code"] == "UNSUPPORTED_FILE_TYPE"
    assert new_path.is_file()
    monkeypatch.setattr("app.presentation.http.uploads.MAX_PHOTO_BYTES", 8)
    too_big = client.put(
        f"/api/v1/pets/{pet_id}/photo", files={"file": ("big.png", b"x" * 32, "image/png")}, headers=headers
    )
    assert too_big.status_code == 413
    assert too_big.json()["code"] == "FILE_TOO_LARGE"
    assert new_path.is_file()


def test_delete_pet_removes_photo_file(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.infra.photos.di.get_media_dir", lambda: tmp_path)
    _, token = _register(client)
    pet_id = _create_pet(client, token).json()["id"]
    headers = _auth(token)
    uploaded = client.put(
        f"/api/v1/pets/{pet_id}/photo", files={"file": ("pet.png", PNG_BYTES, "image/png")}, headers=headers
    )
    photo_path = tmp_path / "pets" / uploaded.json()["photoUrl"].rsplit("/", 1)[-1]
    assert photo_path.is_file()
    deleted = client.delete(f"/api/v1/pets/{pet_id}", headers=headers)
    assert deleted.status_code == 204
    assert not photo_path.exists()
    assert client.get(f"/api/v1/pets/{pet_id}", headers=headers).status_code == 404
