import uuid
from datetime import UTC, datetime, timedelta

from conftest import register_user


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _create(client, headers, pet_id, **overrides):
    payload = {
        "petId": pet_id,
        "name": "Прививка от бешенства",
        "type": "vaccination",
        "schedule": "2026-11-01T10:00:00Z",
        "period": "yearly",
    }
    payload.update(overrides)
    return client.post("/api/v1/events", json=payload, headers=headers)


def test_create_with_defaults_and_frontend_shape(client, auth, pet_id):
    minimal = client.post(
        "/api/v1/events",
        json={"petId": pet_id, "name": "Осмотр", "schedule": "2030-01-01T10:00:00Z"},
        headers=auth,
    )
    assert minimal.status_code == 201, minimal.text
    body = minimal.json()
    assert body["type"] == "other"
    assert body["status"] == "planned"
    assert body["period"] == "none"
    assert body["nextSchedule"] is None
    assert body["isOverdue"] is False
    assert body["doneAt"] is None
    assert minimal.headers["location"] == f"/api/v1/events/{body['id']}"


def test_next_schedule_is_calculated(client, auth, pet_id):
    body = _create(client, auth, pet_id, schedule="2026-01-31T10:00:00Z", period="monthly").json()
    assert body["nextSchedule"] == "2026-02-28T10:00:00Z"

    yearly = _create(client, auth, pet_id).json()
    assert yearly["nextSchedule"] == "2027-11-01T10:00:00Z"


def test_complete_plans_next_occurrence(client, auth, pet_id):
    event_id = _create(client, auth, pet_id, schedule="2030-03-01T10:00:00Z", period="quarterly").json()["id"]

    response = client.post(f"/api/v1/events/{event_id}/complete", headers=auth)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["event"]["status"] == "done"
    assert body["event"]["doneAt"] is not None
    assert body["nextEvent"]["status"] == "planned"
    assert body["nextEvent"]["schedule"] == "2030-06-01T10:00:00Z"
    assert body["nextEvent"]["name"] == "Прививка от бешенства"
    assert body["nextEvent"]["type"] == "vaccination"

    again = client.post(f"/api/v1/events/{event_id}/complete", headers=auth)
    assert again.status_code == 409
    assert again.json()["code"] == "EVENT_NOT_PLANNED"


def test_late_completion_counts_from_done_date(client, auth, pet_id):
    event_id = _create(client, auth, pet_id, schedule="2026-01-10T10:00:00Z", period="yearly").json()["id"]

    response = client.post(
        f"/api/v1/events/{event_id}/complete", json={"doneAt": "2026-03-15T12:00:00Z"}, headers=auth
    )
    body = response.json()
    assert body["event"]["doneAt"] == "2026-03-15T12:00:00Z"
    assert body["nextEvent"]["schedule"] == "2027-03-15T12:00:00Z"


def test_one_off_completion_has_no_next(client, auth, pet_id):
    event_id = _create(client, auth, pet_id, period="none", type="vet_visit").json()["id"]
    body = client.post(f"/api/v1/events/{event_id}/complete", headers=auth).json()
    assert body["nextEvent"] is None


def test_patch_status_done_also_plans_next(client, auth, pet_id):
    event_id = _create(client, auth, pet_id, schedule="2030-01-01T09:00:00Z", period="weekly").json()["id"]

    patched = client.patch(f"/api/v1/events/{event_id}", json={"status": "done"}, headers=auth)
    assert patched.status_code == 200
    assert patched.json()["status"] == "done"

    planned = client.get("/api/v1/events", params={"petId": pet_id, "status": "planned"}, headers=auth).json()
    assert [item["schedule"] for item in planned["items"]] == ["2030-01-08T09:00:00Z"]

    reopened = client.patch(f"/api/v1/events/{event_id}", json={"status": "planned"}, headers=auth)
    assert reopened.json()["doneAt"] is None


def test_upcoming_includes_overdue_and_excludes_far_and_done(client, auth, pet_id):
    now = datetime.now(UTC)
    overdue = _create(client, auth, pet_id, name="Просрочено", schedule=_iso(now - timedelta(days=2))).json()
    soon = _create(client, auth, pet_id, name="Скоро", schedule=_iso(now + timedelta(days=3))).json()
    _create(client, auth, pet_id, name="Нескоро", schedule=_iso(now + timedelta(days=90)))
    _create(client, auth, pet_id, name="Сделано", status="done", schedule=_iso(now + timedelta(days=1)))

    response = client.get("/api/v1/events/upcoming", params={"days": 30}, headers=auth)
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["id"] for item in items] == [overdue["id"], soon["id"]]
    assert items[0]["isOverdue"] is True
    assert items[1]["isOverdue"] is False


def test_list_filters(client, auth, pet_id):
    _create(client, auth, pet_id, type="vaccination", schedule="2026-05-01T00:00:00Z")
    _create(client, auth, pet_id, type="parasite_treatment", schedule="2026-06-01T00:00:00Z")
    _create(client, auth, pet_id, type="vet_visit", schedule="2026-07-01T00:00:00Z")

    vaccinations = client.get("/api/v1/events", params={"type": "vaccination"}, headers=auth).json()
    assert vaccinations["total"] == 1

    summer = client.get(
        "/api/v1/events", params={"from": "2026-06-01T00:00:00Z", "to": "2026-08-01T00:00:00Z"}, headers=auth
    ).json()
    assert [item["type"] for item in summer["items"]] == ["vet_visit", "parasite_treatment"]


def test_isolation_and_unknown_pet(client):
    _, owner = register_user(client, email="owner@petcare.dev")
    _, stranger = register_user(client, email="stranger@petcare.dev")
    pet = client.post("/api/v1/pets", json={"name": "Рекс", "type": "dog"}, headers=owner).json()["id"]
    event_id = _create(client, owner, pet).json()["id"]

    assert client.get(f"/api/v1/events/{event_id}", headers=stranger).status_code == 404
    assert client.patch(f"/api/v1/events/{event_id}", json={"name": "x"}, headers=stranger).status_code == 404
    assert client.post(f"/api/v1/events/{event_id}/complete", headers=stranger).status_code == 404
    assert client.delete(f"/api/v1/events/{event_id}", headers=stranger).status_code == 404
    assert client.get("/api/v1/events", headers=stranger).json()["total"] == 0

    foreign = _create(client, stranger, pet)
    assert foreign.status_code == 422
    assert foreign.json()["code"] == "PET_NOT_FOUND"
    assert _create(client, stranger, str(uuid.uuid4())).json()["code"] == "PET_NOT_FOUND"


def test_update_validation_and_delete(client, auth, pet_id):
    event_id = _create(client, auth, pet_id).json()["id"]

    renamed = client.patch(
        f"/api/v1/events/{event_id}",
        json={"name": " Комплексная прививка ", "description": "Нобивак DHPPi+L"},
        headers=auth,
    )
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Комплексная прививка"
    assert renamed.json()["description"] == "Нобивак DHPPi+L"

    assert client.patch(f"/api/v1/events/{event_id}", json={"schedule": None}, headers=auth).status_code == 422
    assert client.patch(f"/api/v1/events/{event_id}", json={"name": ""}, headers=auth).status_code == 422
    assert client.patch(f"/api/v1/events/{event_id}", json={"period": "hourly"}, headers=auth).status_code == 422

    assert client.delete(f"/api/v1/events/{event_id}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/events/{event_id}", headers=auth).status_code == 404


def test_deleting_pet_cascades_to_events(client, auth, pet_id):
    event_id = _create(client, auth, pet_id).json()["id"]
    client.delete(f"/api/v1/pets/{pet_id}", headers=auth)
    assert client.get(f"/api/v1/events/{event_id}", headers=auth).status_code == 404
