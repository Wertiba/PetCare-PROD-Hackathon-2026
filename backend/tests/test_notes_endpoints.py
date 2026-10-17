import uuid
from conftest import CAT_BREED_ID, register_user


def test_crud(client, auth, pet_id):
    created = client.post("/api/v1/notes", json={"petId": pet_id, "content": "  Боится пылесоса "}, headers=auth)
    assert created.status_code == 201, created.text
    note = created.json()
    assert note["content"] == "Боится пылесоса"
    assert note["petId"] == pet_id
    assert created.headers["location"] == f"/api/v1/notes/{note['id']}"
    assert client.get(f"/api/v1/notes/{note['id']}", headers=auth).json() == note
    updated = client.patch(f"/api/v1/notes/{note['id']}", json={"content": "Уже не боится"}, headers=auth)
    assert updated.status_code == 200
    assert updated.json()["content"] == "Уже не боится"
    assert updated.json()["updatedAt"] >= note["updatedAt"]
    assert client.delete(f"/api/v1/notes/{note['id']}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/notes/{note['id']}", headers=auth).status_code == 404


def test_list_filters_by_pet_and_text_newest_first(client, auth, pet_id):
    other_pet = client.post("/api/v1/pets", json={"name": "Мурка", "breedId": CAT_BREED_ID}, headers=auth).json()["id"]
    for pet, content in ((pet_id, "Любит курицу"), (pet_id, "Прививка в мае"), (other_pet, "Любит рыбу")):
        assert client.post("/api/v1/notes", json={"petId": pet, "content": content}, headers=auth).status_code == 201
    by_pet = client.get("/api/v1/notes", params={"petId": pet_id}, headers=auth).json()
    assert [item["content"] for item in by_pet["items"]] == ["Прививка в мае", "Любит курицу"]
    by_text = client.get("/api/v1/notes", params={"q": "Любит"}, headers=auth).json()
    assert by_text["total"] == 2


def test_other_users_notes_are_invisible(client, auth, pet_id):
    note_id = client.post("/api/v1/notes", json={"petId": pet_id, "content": "Секрет"}, headers=auth).json()["id"]
    _, stranger = register_user(client, login="stranger")
    assert client.get(f"/api/v1/notes/{note_id}", headers=stranger).status_code == 404
    assert client.patch(f"/api/v1/notes/{note_id}", json={"content": "x"}, headers=stranger).status_code == 404
    assert client.delete(f"/api/v1/notes/{note_id}", headers=stranger).status_code == 404
    assert client.get("/api/v1/notes", headers=stranger).json()["total"] == 0
    foreign = client.post("/api/v1/notes", json={"petId": pet_id, "content": "x"}, headers=stranger)
    assert foreign.status_code == 422
    assert foreign.json()["code"] == "PET_NOT_FOUND"


def test_validation_and_pet_cascade(client, auth, pet_id):
    blank = client.post("/api/v1/notes", json={"petId": pet_id, "content": "   "}, headers=auth)
    assert blank.status_code == 422
    too_long = client.post("/api/v1/notes", json={"petId": pet_id, "content": "x" * 2001}, headers=auth)
    assert too_long.status_code == 422
    note_id = client.post("/api/v1/notes", json={"petId": pet_id, "content": "x"}, headers=auth).json()["id"]
    assert client.delete(f"/api/v1/pets/{pet_id}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/notes/{note_id}", headers=auth).status_code == 404


def test_requires_auth(client):
    assert client.get("/api/v1/notes").status_code == 401
    assert client.get(f"/api/v1/notes/{uuid.uuid4()}").status_code == 401
