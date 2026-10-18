"""Input that Postgres cannot store must be refused with 422, not fail in the driver with a 500."""

import pytest

INT32_MAX = 2**31 - 1


@pytest.mark.req("P.ARCH")
def test_food_weight_beyond_int32_is_rejected(client, auth, pet_id):
    response = client.post(
        "/api/v1/foods", json={"petId": pet_id, "name": "Корм", "weight": INT32_MAX + 1}, headers=auth
    )
    assert response.status_code == 422
    assert any(error["field"] == "weight" for error in response.json()["fieldErrors"])


@pytest.mark.req("P.ARCH")
def test_state_value_beyond_int32_is_rejected(client, auth, pet_id, system_categories):
    response = client.post(
        "/api/v1/states",
        json={"petId": pet_id, "categoryId": system_categories["weight"], "value": INT32_MAX + 1},
        headers=auth,
    )
    assert response.status_code == 422


@pytest.mark.req("P.TIME", "P.REPORT")
def test_state_time_outside_date_range_is_rejected(client, auth, pet_id, system_categories):
    """Such a time used to be stored and then broke the PDF report with a 500."""
    response = client.post(
        "/api/v1/states",
        json={"petId": pet_id, "categoryId": system_categories["weight"], "value": 4200, "time": 1e300},
        headers=auth,
    )
    assert response.status_code == 422
    assert client.get(f"/api/v1/pets/{pet_id}/report", headers=auth).status_code == 200


@pytest.mark.req("P.TIME")
def test_notification_time_outside_date_range_is_rejected(client, auth, pet_id):
    event = client.post("/api/v1/events", json={"petId": pet_id, "name": "Прививка", "schedule": 1e9}, headers=auth)
    response = client.post("/api/v1/notifications", json={"eventId": event.json()["id"], "time": 1e300}, headers=auth)
    assert response.status_code == 422


@pytest.mark.req("P.ARCH")
@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/api/v1/notes", {"content": "a\x00b"}),
        ("/api/v1/foods", {"name": "Корм", "ingredients": ["a\x00"]}),
    ],
)
def test_text_with_nul_is_rejected(client, auth, pet_id, path, body):
    response = client.post(path, json={"petId": pet_id, **body}, headers=auth)
    assert response.status_code == 422


@pytest.mark.req("P.ARCH")
def test_search_with_nul_is_rejected(client, auth):
    assert client.get("/api/v1/animals", params={"q": "\x00"}, headers=auth).status_code == 422


@pytest.mark.req("P.ARCH")
def test_huge_page_is_rejected(client, auth):
    assert client.get("/api/v1/pets", params={"page": 10**18}, headers=auth).status_code == 422


@pytest.mark.req("P.AUTH")
def test_login_with_oversized_password_is_rejected(client):
    """The hasher refuses passwords over 4 KB with an unhandled error."""
    response = client.post("/api/v1/auth/login", json={"login": "someone", "password": "x" * 100_000})
    assert response.status_code == 422
