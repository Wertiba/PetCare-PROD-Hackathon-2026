import uuid
from datetime import UTC, datetime, timedelta
import pytest
from conftest import register_user

pytestmark = pytest.mark.req("5.4.5")


@pytest.fixture
def event_id(client, auth, pet_id):
    response = client.post(
        "/api/v1/events", json={"petId": pet_id, "name": "Таблетка от глистов", "schedule": 1893492000.0}, headers=auth
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_defaults_to_event_schedule(client, auth, pet_id, event_id):
    response = client.post("/api/v1/notifications", json={"eventId": event_id}, headers=auth)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["eventId"] == event_id
    assert body["petId"] == pet_id
    assert body["eventName"] == "Таблетка от глистов"
    assert body["type"] == "app"
    assert body["status"] == "pending"
    assert body["time"] == 1893492000.0
    assert response.headers["location"] == f"/api/v1/notifications/{body['id']}"


@pytest.mark.req("5.4.6")
def test_due_filter_and_mark_read(client, auth, event_id):
    past = (datetime.now(UTC) - timedelta(minutes=5)).timestamp()
    due = client.post(
        "/api/v1/notifications", json={"eventId": event_id, "time": past, "type": "web_push"}, headers=auth
    ).json()
    client.post("/api/v1/notifications", json={"eventId": event_id}, headers=auth)
    assert client.get("/api/v1/notifications", headers=auth).json()["total"] == 2
    due_now = client.get("/api/v1/notifications", params={"due": "true"}, headers=auth).json()
    assert [item["id"] for item in due_now["items"]] == [due["id"]]
    read = client.patch(f"/api/v1/notifications/{due['id']}", json={"status": "read"}, headers=auth)
    assert read.status_code == 200
    assert read.json()["status"] == "read"
    assert client.get("/api/v1/notifications", params={"due": "true"}, headers=auth).json()["total"] == 0
    by_status = client.get("/api/v1/notifications", params={"status": "read"}, headers=auth).json()
    assert by_status["total"] == 1


def test_filter_by_event(client, auth, pet_id, event_id):
    other_event = client.post(
        "/api/v1/events", json={"petId": pet_id, "name": "Груминг", "schedule": 1896170400.0}, headers=auth
    ).json()["id"]
    client.post("/api/v1/notifications", json={"eventId": event_id}, headers=auth)
    client.post("/api/v1/notifications", json={"eventId": other_event}, headers=auth)
    only_one = client.get("/api/v1/notifications", params={"eventId": other_event}, headers=auth).json()
    assert [item["eventName"] for item in only_one["items"]] == ["Груминг"]


@pytest.mark.req("P.ACCESS")
def test_isolation_and_unknown_event(client, event_id, auth):
    notification_id = client.post("/api/v1/notifications", json={"eventId": event_id}, headers=auth).json()["id"]
    _, stranger = register_user(client, login="stranger")
    assert client.get(f"/api/v1/notifications/{notification_id}", headers=stranger).status_code == 404
    assert (
        client.patch(f"/api/v1/notifications/{notification_id}", json={"status": "read"}, headers=stranger).status_code
        == 404
    )
    assert client.delete(f"/api/v1/notifications/{notification_id}", headers=stranger).status_code == 404
    assert client.get("/api/v1/notifications", headers=stranger).json()["total"] == 0
    foreign = client.post("/api/v1/notifications", json={"eventId": event_id}, headers=stranger)
    assert foreign.status_code == 422
    assert foreign.json()["code"] == "EVENT_NOT_FOUND"
    missing = client.post("/api/v1/notifications", json={"eventId": str(uuid.uuid4())}, headers=stranger)
    assert missing.json()["details"] == {"field": "eventId"}


def test_delete_and_cascade_from_event(client, auth, event_id):
    first = client.post("/api/v1/notifications", json={"eventId": event_id}, headers=auth).json()["id"]
    second = client.post("/api/v1/notifications", json={"eventId": event_id}, headers=auth).json()["id"]
    assert client.delete(f"/api/v1/notifications/{first}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/notifications/{first}", headers=auth).status_code == 404
    client.delete(f"/api/v1/events/{event_id}", headers=auth)
    assert client.get(f"/api/v1/notifications/{second}", headers=auth).status_code == 404


@pytest.mark.req("7.1")
def test_invalid_values(client, auth, event_id):
    bad_type = client.post("/api/v1/notifications", json={"eventId": event_id, "type": "sms"}, headers=auth)
    assert bad_type.status_code == 422
    notification_id = client.post("/api/v1/notifications", json={"eventId": event_id}, headers=auth).json()["id"]
    null_status = client.patch(f"/api/v1/notifications/{notification_id}", json={"status": None}, headers=auth)
    assert null_status.status_code == 422
