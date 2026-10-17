import uuid
from conftest import register_user


def _create(client, headers, **overrides):
    payload = {"name": "Игрушки", "kind": "count", "type": "check", "unit": "none"}
    payload.update(overrides)
    return client.post("/api/v1/categories", json=payload, headers=headers)


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


def test_other_users_category_is_invisible(client, system_categories):
    _, owner = register_user(client, login="owner")
    _, stranger = register_user(client, login="stranger")
    category_id = _create(client, owner).json()["id"]
    assert client.get(f"/api/v1/categories/{category_id}", headers=stranger).status_code == 404
    assert client.patch(f"/api/v1/categories/{category_id}", json={"name": "x"}, headers=stranger).status_code == 404
    assert client.delete(f"/api/v1/categories/{category_id}", headers=stranger).status_code == 404
    assert client.get("/api/v1/categories", headers=stranger).json()["total"] == 4


def test_system_category_is_read_only(client, auth, system_categories):
    weight_id = system_categories["weight"]
    assert client.get(f"/api/v1/categories/{weight_id}", headers=auth).status_code == 200
    patch = client.patch(f"/api/v1/categories/{weight_id}", json={"name": "Масса"}, headers=auth)
    assert patch.status_code == 403
    assert patch.json()["code"] == "SYSTEM_CATEGORY_READ_ONLY"
    assert client.delete(f"/api/v1/categories/{weight_id}", headers=auth).status_code == 403


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


def test_validation_errors(client, auth):
    blank = _create(client, auth, name="  ")
    assert blank.status_code == 422
    assert "name" in [err["field"] for err in blank.json()["fieldErrors"]]
    bad_kind = _create(client, auth, kind="median")
    assert bad_kind.status_code == 422
    assert "kind" in [err["field"] for err in bad_kind.json()["fieldErrors"]]


def test_requires_auth(client):
    assert client.get("/api/v1/categories").status_code == 401
    assert client.get(f"/api/v1/categories/{uuid.uuid4()}").status_code == 401
