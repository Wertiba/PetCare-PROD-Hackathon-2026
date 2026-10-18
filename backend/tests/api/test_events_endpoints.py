import pytest
import uuid
from datetime import UTC, datetime, timedelta
from conftest import CAT_BREED_ID, DOG_BREED_ID, register_user
from app.infra.metrics import DOMAIN_EVENTS_TOTAL


def _timestamp(dt: datetime) -> float:
    return dt.timestamp()


def _create(client, headers, pet_id, **overrides):
    payload = {
        "petId": pet_id,
        "name": "Прививка от бешенства",
        "type": "vaccination",
        "schedule": 1793527200.0,
        "period": "yearly",
    }
    payload.update(overrides)
    return client.post("/api/v1/events", json=payload, headers=headers)


@pytest.mark.req("5.2.1")
def test_create_with_defaults_and_frontend_shape(client, auth, pet_id):
    minimal = client.post(
        "/api/v1/events", json={"petId": pet_id, "name": "Осмотр", "schedule": 1893492000.0}, headers=auth
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


@pytest.mark.req("5.4.1")
def test_next_schedule_is_calculated(client, auth, pet_id):
    body = _create(client, auth, pet_id, schedule=1769853600.0, period="monthly").json()
    assert body["nextSchedule"] == 1772272800.0
    yearly = _create(client, auth, pet_id).json()
    assert yearly["nextSchedule"] == 1825063200.0


@pytest.mark.req("5.4.1", "5.4.5")
def test_complete_plans_next_occurrence(client, auth, pet_id):
    completed = DOMAIN_EVENTS_TOTAL.labels(entity="event", action="completed")
    planned = DOMAIN_EVENTS_TOTAL.labels(entity="event", action="auto_planned")
    before = (completed._value.get(), planned._value.get())
    event_id = _create(client, auth, pet_id, schedule=1898589600.0, period="quarterly").json()["id"]
    response = client.post(f"/api/v1/events/{event_id}/complete", headers=auth)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["event"]["status"] == "done"
    assert body["event"]["doneAt"] is not None
    assert body["nextEvent"]["status"] == "planned"
    assert body["nextEvent"]["schedule"] == 1906538400.0
    assert body["nextEvent"]["name"] == "Прививка от бешенства"
    assert body["nextEvent"]["type"] == "vaccination"
    again = client.post(f"/api/v1/events/{event_id}/complete", headers=auth)
    assert again.status_code == 409
    assert again.json()["code"] == "EVENT_NOT_PLANNED"
    assert (completed._value.get(), planned._value.get()) == (before[0] + 1, before[1] + 1)


@pytest.mark.req("5.4.1")
def test_late_completion_counts_from_done_date(client, auth, pet_id):
    event_id = _create(client, auth, pet_id, schedule=1768039200.0, period="yearly").json()["id"]
    response = client.post(f"/api/v1/events/{event_id}/complete", json={"doneAt": 1773576000.0}, headers=auth)
    body = response.json()
    assert body["event"]["doneAt"] == 1773576000.0
    assert body["nextEvent"]["schedule"] == 1805112000.0


@pytest.mark.req("5.2.3")
def test_one_off_completion_has_no_next(client, auth, pet_id):
    event_id = _create(client, auth, pet_id, period="none", type="vet_visit").json()["id"]
    body = client.post(f"/api/v1/events/{event_id}/complete", headers=auth).json()
    assert body["nextEvent"] is None


@pytest.mark.req("5.4.1")
def test_patch_status_done_also_plans_next(client, auth, pet_id):
    completed = DOMAIN_EVENTS_TOTAL.labels(entity="event", action="completed")
    planned_counter = DOMAIN_EVENTS_TOTAL.labels(entity="event", action="auto_planned")
    before = (completed._value.get(), planned_counter._value.get())
    event_id = _create(client, auth, pet_id, schedule=1893488400.0, period="weekly").json()["id"]
    patched = client.patch(f"/api/v1/events/{event_id}", json={"status": "done"}, headers=auth)
    assert patched.status_code == 200
    assert patched.json()["status"] == "done"
    planned = client.get("/api/v1/events", params={"petId": pet_id, "status": "planned"}, headers=auth).json()
    assert [item["schedule"] for item in planned["items"]] == [1894093200.0]
    assert client.patch(f"/api/v1/events/{event_id}", json={"status": "done"}, headers=auth).status_code == 200
    assert (completed._value.get(), planned_counter._value.get()) == (before[0] + 1, before[1] + 1)
    reopened = client.patch(f"/api/v1/events/{event_id}", json={"status": "planned"}, headers=auth)
    assert reopened.json()["doneAt"] is None


@pytest.mark.req("5.4.6")
def test_upcoming_includes_overdue_and_excludes_far_and_done(client, auth, pet_id):
    now = datetime.now(UTC)
    overdue = _create(client, auth, pet_id, name="Просрочено", schedule=_timestamp(now - timedelta(days=2))).json()
    soon = _create(client, auth, pet_id, name="Скоро", schedule=_timestamp(now + timedelta(days=3))).json()
    _create(client, auth, pet_id, name="Нескоро", schedule=_timestamp(now + timedelta(days=90)))
    _create(client, auth, pet_id, name="Сделано", status="done", schedule=_timestamp(now + timedelta(days=1)))
    response = client.get("/api/v1/events/upcoming", params={"days": 30}, headers=auth)
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["id"] for item in items] == [overdue["id"], soon["id"]]
    assert items[0]["isOverdue"] is True
    assert items[1]["isOverdue"] is False


@pytest.mark.req("5.2.1", "5.2.2", "5.2.3")
def test_list_filters(client, auth, pet_id):
    _create(client, auth, pet_id, type="vaccination", schedule=1777593600.0)
    _create(client, auth, pet_id, type="parasite_treatment", schedule=1780272000.0)
    _create(client, auth, pet_id, type="vet_visit", schedule=1782864000.0)
    vaccinations = client.get("/api/v1/events", params={"type": "vaccination"}, headers=auth).json()
    assert vaccinations["total"] == 1
    summer = client.get("/api/v1/events", params={"from": 1780272000.0, "to": 1785542400.0}, headers=auth).json()
    assert [item["type"] for item in summer["items"]] == ["vet_visit", "parasite_treatment"]


@pytest.mark.req("P.ACCESS")
def test_isolation_and_unknown_pet(client):
    _, owner = register_user(client, login="owner")
    _, stranger = register_user(client, login="stranger")
    pet = client.post("/api/v1/pets", json={"name": "Рекс", "breedId": DOG_BREED_ID}, headers=owner).json()["id"]
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


@pytest.mark.req("5.2.1", "7.1")
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


@pytest.mark.req("5.2.1")
def test_deleting_pet_cascades_to_events(client, auth, pet_id):
    event_id = _create(client, auth, pet_id).json()["id"]
    client.delete(f"/api/v1/pets/{pet_id}", headers=auth)
    assert client.get(f"/api/v1/events/{event_id}", headers=auth).status_code == 404


@pytest.mark.req("5.4.1")
def test_recording_a_recent_done_event_plans_the_next_from_its_date(client, auth, pet_id):
    """A vaccination done two months ago: the next one is due a year after it, not a year after today."""
    done_on = datetime.now(UTC) - timedelta(days=60)
    body = _create(client, auth, pet_id, status="done", schedule=_timestamp(done_on)).json()
    assert body["doneAt"] == _timestamp(done_on)
    planned = client.get("/api/v1/events", params={"petId": pet_id, "status": "planned"}, headers=auth).json()
    assert [item["schedule"] for item in planned["items"]] == [body["nextSchedule"]]
    assert body["nextSchedule"] < _timestamp(datetime.now(UTC) + timedelta(days=310))


@pytest.mark.req("5.4.1")
def test_recording_old_history_does_not_plan_past_occurrences(client, auth, pet_id):
    _create(client, auth, pet_id, status="done", schedule=_timestamp(datetime.now(UTC) - timedelta(days=800)))
    planned = client.get("/api/v1/events", params={"petId": pet_id, "status": "planned"}, headers=auth).json()
    assert planned["items"] == []


@pytest.mark.req("5.4.1")
def test_reopening_and_completing_again_does_not_duplicate_the_next_event(client, auth, pet_id):
    event_id = _create(client, auth, pet_id, schedule=1893488400.0, period="weekly").json()["id"]
    for status in ("done", "planned", "done"):
        assert client.patch(f"/api/v1/events/{event_id}", json={"status": status}, headers=auth).status_code == 200
    planned = client.get("/api/v1/events", params={"petId": pet_id, "status": "planned"}, headers=auth).json()
    assert planned["total"] == 1


@pytest.mark.req("5.4.1")
def test_completion_date_cannot_be_in_the_future(client, auth, pet_id):
    event_id = _create(client, auth, pet_id).json()["id"]
    later = _timestamp(datetime.now(UTC) + timedelta(days=30))
    response = client.post(f"/api/v1/events/{event_id}/complete", json={"doneAt": later}, headers=auth)
    assert response.status_code == 422
    assert client.get(f"/api/v1/events/{event_id}", headers=auth).json()["status"] == "planned"


def test_pages_of_events_on_the_same_time_neither_repeat_nor_skip(client, auth, pet_id):
    created = {_create(client, auth, pet_id, name=f"Осмотр {n}", schedule=1893492000.0).json()["id"] for n in range(5)}
    seen = [
        item["id"]
        for page in range(5)
        for item in client.get("/api/v1/events", params={"page": page, "size": 1}, headers=auth).json()["items"]
    ]
    assert sorted(seen) == sorted(created)
