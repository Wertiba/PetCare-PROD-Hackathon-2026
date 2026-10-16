import uuid

import pytest
from conftest import register_user


def _record(client, headers, pet_id, cat_id, value, time=None, **extra):
    payload = {"petId": pet_id, "catId": cat_id, "value": value, **extra}
    if time is not None:
        payload["time"] = time
    return client.post("/api/v1/states", json=payload, headers=headers)


def test_create_and_read_state(client, auth, pet_id, system_categories):
    created = _record(
        client, auth, pet_id, system_categories["weight"], 4200, "2026-10-01T09:00:00+03:00", note="  после еды "
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["value"] == 4200
    assert body["time"] == "2026-10-01T06:00:00Z"
    assert body["note"] == "после еды"
    assert created.headers["location"] == f"/api/v1/states/{body['id']}"

    fetched = client.get(f"/api/v1/states/{body['id']}", headers=auth)
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_time_defaults_to_now(client, auth, pet_id, system_categories):
    body = _record(client, auth, pet_id, system_categories["food"], 120).json()
    assert body["time"].endswith("Z")


@pytest.mark.parametrize(
    ("category", "value"),
    [("liked", 2), ("liked", -1), ("appetite", 0), ("appetite", 6), ("weight", -5)],
)
def test_value_must_fit_category_type(client, auth, pet_id, system_categories, category, value):
    response = _record(client, auth, pet_id, system_categories[category], value)
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "INVALID_VALUE"
    assert body["details"] == {"field": "value", "value": value}


def test_unknown_or_foreign_pet_and_category(client, system_categories):
    _, owner = register_user(client, email="owner@petcare.dev")
    _, stranger = register_user(client, email="stranger@petcare.dev")
    owner_pet = client.post("/api/v1/pets", json={"name": "Рекс", "type": "dog"}, headers=owner).json()["id"]
    owner_category = client.post(
        "/api/v1/categories", json={"name": "Секрет", "kind": "sum", "type": "number"}, headers=owner
    ).json()["id"]
    stranger_pet = client.post("/api/v1/pets", json={"name": "Мурка", "type": "cat"}, headers=stranger).json()["id"]

    foreign_pet = _record(client, stranger, owner_pet, system_categories["food"], 10)
    assert foreign_pet.status_code == 422
    assert foreign_pet.json()["code"] == "PET_NOT_FOUND"
    assert foreign_pet.json()["details"] == {"field": "petId"}

    foreign_category = _record(client, stranger, stranger_pet, owner_category, 10)
    assert foreign_category.status_code == 422
    assert foreign_category.json()["code"] == "CATEGORY_NOT_FOUND"

    missing_category = _record(client, stranger, stranger_pet, str(uuid.uuid4()), 10)
    assert missing_category.json()["code"] == "CATEGORY_NOT_FOUND"


def test_list_filters_and_isolation(client, system_categories):
    _, owner = register_user(client, email="owner@petcare.dev")
    _, stranger = register_user(client, email="stranger@petcare.dev")
    pet = client.post("/api/v1/pets", json={"name": "Рекс", "type": "dog"}, headers=owner).json()["id"]
    other_pet = client.post("/api/v1/pets", json={"name": "Шарик", "type": "dog"}, headers=owner).json()["id"]

    _record(client, owner, pet, system_categories["weight"], 10000, "2026-09-01T00:00:00Z")
    _record(client, owner, pet, system_categories["weight"], 10500, "2026-10-01T00:00:00Z")
    _record(client, owner, pet, system_categories["food"], 300, "2026-10-01T08:00:00Z")
    _record(client, owner, other_pet, system_categories["food"], 200, "2026-10-01T08:00:00Z")

    everything = client.get("/api/v1/states", headers=owner).json()
    assert everything["total"] == 4

    weights = client.get(
        "/api/v1/states", params={"petId": pet, "catId": system_categories["weight"]}, headers=owner
    ).json()
    assert [item["value"] for item in weights["items"]] == [10500, 10000]

    september = client.get(
        "/api/v1/states", params={"petId": pet, "from": "2026-09-01T00:00:00Z", "to": "2026-09-30T23:59:59Z"},
        headers=owner,
    ).json()
    assert [item["value"] for item in september["items"]] == [10000]

    assert client.get("/api/v1/states", headers=stranger).json()["total"] == 0
    state_id = everything["items"][0]["id"]
    assert client.get(f"/api/v1/states/{state_id}", headers=stranger).status_code == 404
    assert client.delete(f"/api/v1/states/{state_id}", headers=stranger).status_code == 404


def test_update_and_delete(client, auth, pet_id, system_categories):
    state_id = _record(client, auth, pet_id, system_categories["appetite"], 3).json()["id"]

    updated = client.patch(f"/api/v1/states/{state_id}", json={"value": 5, "note": "ел жадно"}, headers=auth)
    assert updated.status_code == 200
    assert updated.json()["value"] == 5
    assert updated.json()["note"] == "ел жадно"

    invalid = client.patch(f"/api/v1/states/{state_id}", json={"value": 9}, headers=auth)
    assert invalid.status_code == 422
    assert invalid.json()["code"] == "INVALID_VALUE"

    null_value = client.patch(f"/api/v1/states/{state_id}", json={"value": None}, headers=auth)
    assert null_value.status_code == 422

    assert client.delete(f"/api/v1/states/{state_id}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/states/{state_id}", headers=auth).status_code == 404


@pytest.mark.parametrize(
    ("category", "values", "expected"),
    [
        ("weight", [4000, 4100, 4300], 4300.0),  # last by time
        ("food", [100, 150, 50], 300.0),  # sum
        ("appetite", [2, 4, 3], 3.0),  # avg
        ("liked", [1, 0, 1], 3.0),  # count of records
    ],
)
def test_summary_aggregates_by_kind(client, auth, pet_id, system_categories, category, values, expected):
    for day, value in enumerate(values, start=1):
        _record(client, auth, pet_id, system_categories[category], value, f"2026-10-0{day}T12:00:00Z")

    response = client.get(
        "/api/v1/states/summary", params={"petId": pet_id, "catId": system_categories[category]}, headers=auth
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["value"] == expected
    assert body["count"] == 3


def test_summary_with_period_and_empty(client, auth, pet_id, system_categories):
    food = system_categories["food"]
    _record(client, auth, pet_id, food, 100, "2026-10-01T12:00:00Z")
    _record(client, auth, pet_id, food, 200, "2026-10-02T12:00:00Z")

    one_day = client.get(
        "/api/v1/states/summary",
        params={"petId": pet_id, "catId": food, "from": "2026-10-02T00:00:00Z", "to": "2026-10-02T23:59:59Z"},
        headers=auth,
    ).json()
    assert one_day["value"] == 200.0
    assert one_day["from"] == "2026-10-02T00:00:00Z"

    empty = client.get(
        "/api/v1/states/summary", params={"petId": pet_id, "catId": system_categories["weight"]}, headers=auth
    ).json()
    assert empty == {
        "petId": pet_id,
        "catId": system_categories["weight"],
        "kind": "last",
        "unit": "g",
        "value": None,
        "count": 0,
        "from": None,
        "to": None,
    }


def test_deleting_pet_cascades_to_states(client, auth, pet_id, system_categories):
    state_id = _record(client, auth, pet_id, system_categories["food"], 10).json()["id"]
    assert client.delete(f"/api/v1/pets/{pet_id}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/states/{state_id}", headers=auth).status_code == 404
