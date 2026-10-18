import pytest
import uuid
from conftest import CAT_BREED_ID, CAT_ID, DOG_ID

pytestmark = pytest.mark.req("P.CATALOG")


@pytest.mark.req("5.1.2")
def test_everyone_reads_seeded_animals_and_breeds(client, auth):
    animals = client.get("/api/v1/animals", headers=auth).json()
    assert [item["name"] for item in animals["items"]] == ["Кошка", "Собака"]
    assert all(item["createdBy"] is None for item in animals["items"])
    cats = client.get("/api/v1/breeds", params={"animalId": CAT_ID}, headers=auth).json()
    assert cats["total"] == 1
    assert cats["items"][0] == {
        "id": CAT_BREED_ID,
        "animalId": CAT_ID,
        "name": "Британская короткошерстная",
        "createdBy": None,
        "createdAt": cats["items"][0]["createdAt"],
    }
    assert client.get(f"/api/v1/animals/{DOG_ID}", headers=auth).json()["name"] == "Собака"
    assert client.get(f"/api/v1/breeds/{CAT_BREED_ID}", headers=auth).status_code == 200
    assert client.get(f"/api/v1/animals/{uuid.uuid4()}", headers=auth).status_code == 404
    assert client.get(f"/api/v1/breeds/{uuid.uuid4()}", headers=auth).status_code == 404


@pytest.mark.req("P.ACCESS")
def test_only_admin_writes_the_catalog(client, auth):
    for method, path, payload in (
        ("post", "/api/v1/animals", {"name": "Хомяк"}),
        ("patch", f"/api/v1/animals/{CAT_ID}", {"name": "Кот"}),
        ("delete", f"/api/v1/animals/{CAT_ID}", None),
        ("post", "/api/v1/breeds", {"animalId": CAT_ID, "name": "Сфинкс"}),
        ("patch", f"/api/v1/breeds/{CAT_BREED_ID}", {"name": "Британец"}),
        ("delete", f"/api/v1/breeds/{CAT_BREED_ID}", None),
    ):
        response = client.request(method, path, json=payload, headers=auth)
        assert response.status_code == 403, (method, path)
        assert response.json()["code"] == "FORBIDDEN"
    assert client.get("/api/v1/animals", headers=auth).json()["total"] == 2


def test_admin_manages_animals_and_breeds(client, admin, auth):
    created = client.post("/api/v1/animals", json={"name": "  Хомяк "}, headers=admin)
    assert created.status_code == 201, created.text
    hamster = created.json()
    assert hamster["name"] == "Хомяк"
    assert hamster["createdBy"] is not None
    assert created.headers["location"] == f"/api/v1/animals/{hamster['id']}"
    listed = client.get("/api/v1/animals", headers=auth).json()
    assert [item["name"] for item in listed["items"]] == ["Кошка", "Собака", "Хомяк"]

    breed = client.post("/api/v1/breeds", json={"animalId": hamster["id"], "name": "Джунгарский"}, headers=admin)
    assert breed.status_code == 201, breed.text
    breed_id = breed.json()["id"]
    pet = client.post("/api/v1/pets", json={"name": "Хома", "breedId": breed_id}, headers=auth).json()
    assert pet["animal"]["name"] == "Хомяк"

    renamed = client.patch(f"/api/v1/animals/{hamster['id']}", json={"name": "Грызун"}, headers=admin)
    assert renamed.json()["name"] == "Грызун"
    moved = client.patch(f"/api/v1/breeds/{breed_id}", json={"animalId": CAT_ID}, headers=admin)
    assert moved.status_code == 200
    assert moved.json()["animalId"] == CAT_ID
    assert (
        client.patch(f"/api/v1/breeds/{breed_id}", json={"animalId": hamster["id"]}, headers=admin).status_code == 200
    )

    assert client.delete(f"/api/v1/animals/{hamster['id']}", headers=admin).status_code == 204
    assert client.get(f"/api/v1/breeds/{breed_id}", headers=admin).status_code == 404
    orphan = client.get(f"/api/v1/pets/{pet['id']}", headers=auth).json()
    assert orphan["breed"] is None
    assert orphan["animal"] is None


@pytest.mark.req("7.1")
def test_catalog_validation_and_duplicates(client, admin):
    duplicate = client.post("/api/v1/animals", json={"name": "Кошка"}, headers=admin)
    assert duplicate.status_code == 409
    same_breed = client.post(
        "/api/v1/breeds", json={"animalId": CAT_ID, "name": "Британская короткошерстная"}, headers=admin
    )
    assert same_breed.status_code == 409
    same_name_other_animal = client.post(
        "/api/v1/breeds", json={"animalId": DOG_ID, "name": "Британская короткошерстная"}, headers=admin
    )
    assert same_name_other_animal.status_code == 201
    unknown_animal = client.post("/api/v1/breeds", json={"animalId": str(uuid.uuid4()), "name": "X"}, headers=admin)
    assert unknown_animal.status_code == 422
    assert unknown_animal.json()["code"] == "ANIMAL_NOT_FOUND"
    assert unknown_animal.json()["details"] == {"field": "animalId"}
    blank = client.post("/api/v1/animals", json={"name": "  "}, headers=admin)
    assert blank.status_code == 422
    null_animal = client.patch(f"/api/v1/breeds/{CAT_BREED_ID}", json={"animalId": None}, headers=admin)
    assert null_animal.status_code == 422


def test_breed_search_by_name(client, auth):
    response = client.get("/api/v1/breeds", params={"q": "Брит"}, headers=auth).json()
    assert [item["id"] for item in response["items"]] == [CAT_BREED_ID]


@pytest.mark.req("P.ACCESS")
def test_requires_auth(client):
    assert client.get("/api/v1/animals").status_code == 401
    assert client.get("/api/v1/breeds").status_code == 401


@pytest.mark.req("7.1")
def test_names_differing_only_in_case_are_duplicates(client, admin):
    ferret = client.post("/api/v1/animals", json={"name": "Ferret"}, headers=admin).json()
    assert client.post("/api/v1/animals", json={"name": "FERRET"}, headers=admin).status_code == 409
    renamed = client.patch(f"/api/v1/animals/{ferret['id']}", json={"name": "ferret"}, headers=admin)
    assert renamed.status_code == 200
    breed = client.post("/api/v1/breeds", json={"animalId": ferret["id"], "name": "Sable"}, headers=admin).json()
    assert (
        client.post("/api/v1/breeds", json={"animalId": ferret["id"], "name": "sable"}, headers=admin).status_code
        == 409
    )
    other = client.post("/api/v1/breeds", json={"animalId": ferret["id"], "name": "Albino"}, headers=admin).json()
    assert client.patch(f"/api/v1/breeds/{other['id']}", json={"name": "SABLE"}, headers=admin).status_code == 409
    assert client.patch(f"/api/v1/breeds/{breed['id']}", json={"name": "SABLE"}, headers=admin).status_code == 200


def test_search_treats_like_wildcards_literally(client, auth):
    for q in ("_", "%"):
        assert client.get("/api/v1/animals", params={"q": q}, headers=auth).json()["total"] == 0
        assert client.get("/api/v1/breeds", params={"q": q}, headers=auth).json()["total"] == 0
