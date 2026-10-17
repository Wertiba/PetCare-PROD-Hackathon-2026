import pytest
import uuid
from conftest import DOG_BREED_ID, register_user

pytestmark = pytest.mark.req("P.CATALOG")


def _create(client, headers, **overrides):
    payload = {"name": "Игрушки", "kind": "count", "type": "check", "unit": "none"}
    payload.update(overrides)
    return client.post("/api/v1/categories", json=payload, headers=headers)


@pytest.mark.req("5.2.5", "5.3.4")
def test_list_shows_system_first_then_own(client, auth, system_categories):
    created = _create(client, auth, name="Аквариум")
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["isSystem"] is False
    assert body["createdBy"] is not None
    assert created.headers["location"] == f"/api/v1/categories/{body['id']}"
    listed = client.get("/api/v1/categories", params={"size": 100}, headers=auth).json()
    assert listed["total"] == 5
    assert listed["items"][-1]["name"] == "Аквариум"
    assert all((item["isSystem"] for item in listed["items"][:-1]))


def test_filters_by_type_and_name(client, auth, system_categories):
    scale = client.get("/api/v1/categories", params={"type": "scale"}, headers=auth).json()
    assert [item["name"] for item in scale["items"]] == ["Аппетит"]
    by_name = client.get("/api/v1/categories", params={"q": "Корм"}, headers=auth).json()
    assert {item["name"] for item in by_name["items"]} == {"Корм", "Корм понравился"}


@pytest.mark.req("P.ACCESS")
def test_categories_are_shared_but_only_the_author_changes_them(client, system_categories):
    _, owner = register_user(client, login="owner")
    _, stranger = register_user(client, login="stranger")
    category_id = _create(client, owner).json()["id"]
    assert client.get(f"/api/v1/categories/{category_id}", headers=stranger).status_code == 200
    assert client.get("/api/v1/categories", headers=stranger).json()["total"] == 5
    patch = client.patch(f"/api/v1/categories/{category_id}", json={"name": "x"}, headers=stranger)
    assert patch.status_code == 403
    assert patch.json()["code"] == "FORBIDDEN"
    assert client.delete(f"/api/v1/categories/{category_id}", headers=stranger).status_code == 403
    assert client.get(f"/api/v1/categories/{uuid.uuid4()}", headers=stranger).status_code == 404


@pytest.mark.req("P.ACCESS")
def test_system_category_is_read_only(client, auth, system_categories):
    weight_id = system_categories["weight"]
    assert client.get(f"/api/v1/categories/{weight_id}", headers=auth).status_code == 200
    patch = client.patch(f"/api/v1/categories/{weight_id}", json={"name": "Масса"}, headers=auth)
    assert patch.status_code == 403
    assert patch.json()["code"] == "SYSTEM_CATEGORY_READ_ONLY"
    assert client.delete(f"/api/v1/categories/{weight_id}", headers=auth).status_code == 403


@pytest.mark.req("P.ACCESS")
def test_admin_changes_any_category(client, admin, system_categories):
    weight_id = system_categories["weight"]
    patch = client.patch(f"/api/v1/categories/{weight_id}", json={"name": "Масса"}, headers=admin)
    assert patch.status_code == 200
    assert patch.json()["name"] == "Масса"
    assert client.delete(f"/api/v1/categories/{weight_id}", headers=admin).status_code == 204


def test_category_used_by_others_keeps_its_meaning(client):
    _, owner = register_user(client, login="owner")
    _, other = register_user(client, login="other")
    category_id = _create(client, owner).json()["id"]
    pet = client.post("/api/v1/pets", json={"name": "Рекс", "breedId": DOG_BREED_ID}, headers=other).json()["id"]
    state = client.post("/api/v1/states", json={"petId": pet, "categoryId": category_id, "value": 1}, headers=other)
    assert state.status_code == 201, state.text
    deleted = client.delete(f"/api/v1/categories/{category_id}", headers=owner)
    assert deleted.status_code == 409
    assert deleted.json()["code"] == "CATEGORY_IN_USE"
    retyped = client.patch(f"/api/v1/categories/{category_id}", json={"type": "number"}, headers=owner)
    assert retyped.status_code == 409
    renamed = client.patch(f"/api/v1/categories/{category_id}", json={"name": "Мячики", "type": "check"}, headers=owner)
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Мячики"


def test_update_and_delete_own(client, auth):
    category_id = _create(client, auth).json()["id"]
    updated = client.patch(
        f"/api/v1/categories/{category_id}", json={"name": "  Мячики ", "unit": "times"}, headers=auth
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Мячики"
    assert updated.json()["unit"] == "times"
    assert updated.json()["kind"] == "count"
    assert client.delete(f"/api/v1/categories/{category_id}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/categories/{category_id}", headers=auth).status_code == 404


@pytest.mark.req("7.1")
def test_validation_errors(client, auth):
    blank = _create(client, auth, name="  ")
    assert blank.status_code == 422
    assert "name" in [err["field"] for err in blank.json()["fieldErrors"]]
    bad_kind = _create(client, auth, kind="median")
    assert bad_kind.status_code == 422
    assert "kind" in [err["field"] for err in bad_kind.json()["fieldErrors"]]


@pytest.mark.req("P.ACCESS")
def test_requires_auth(client):
    assert client.get("/api/v1/categories").status_code == 401
    assert client.get(f"/api/v1/categories/{uuid.uuid4()}").status_code == 401
