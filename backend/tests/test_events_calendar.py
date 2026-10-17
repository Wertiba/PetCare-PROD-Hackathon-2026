import uuid
from datetime import UTC, datetime, timedelta

from conftest import CAT_BREED_ID, DOG_BREED_ID, register_user

from app.infra.metrics import DOMAIN_EVENTS_TOTAL


def _timestamp(moment: datetime) -> float:
    return moment.timestamp()


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


def _pet(client, headers, name, breed_id):
    response = client.post("/api/v1/pets", json={"name": name, "breedId": breed_id}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_calendar_requires_auth_and_is_not_parsed_as_event_id(client):
    response = client.get("/api/v1/events/calendar.ics")
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_calendar_file_of_planned_events(client, auth, pet_id):
    exported = DOMAIN_EVENTS_TOTAL.labels(entity="event", action="calendar_exported")
    before = exported._value.get()
    now = datetime.now(UTC)
    rex = _pet(client, auth, "Рекс", DOG_BREED_ID)
    overdue = _create(client, auth, pet_id, name="Просрочено", schedule=_timestamp(now - timedelta(days=2))).json()
    later = _create(client, auth, pet_id, name="Позже", schedule=1800000000.0, period="monthly").json()
    rex_event = _create(
        client, auth, rex, name="Стрижка", type="grooming", schedule=1710000000.0, period="weekly"
    ).json()
    earlier = _create(
        client, auth, pet_id, name="Раньше", schedule=1700000000.0, period="none", description="заметка"
    ).json()
    done = _create(client, auth, pet_id, name="Сделано", status="done", schedule=1750000000.0).json()
    cancelled = _create(client, auth, pet_id, name="Отменено", status="cancelled", schedule=1760000000.0).json()
    _, stranger = register_user(client, login="stranger")
    foreign_pet = _pet(client, stranger, "Чужой", DOG_BREED_ID)
    foreign = _create(client, stranger, foreign_pet, name="Чужое").json()

    response = client.get("/api/v1/events/calendar.ics", headers=auth)
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "text/calendar; charset=utf-8"
    assert response.headers["content-disposition"] == 'attachment; filename="petcare.ics"'
    body = response.text
    assert body.startswith("BEGIN:VCALENDAR\r\n")
    assert "BEGIN:VCALENDAR" in body
    assert f"UID:{overdue['id']}@petcare" in body
    assert f"UID:{later['id']}@petcare" in body
    assert f"UID:{earlier['id']}@petcare" in body
    assert f"UID:{rex_event['id']}@petcare" in body
    assert "SUMMARY:Рекс: Стрижка" in body
    assert "CATEGORIES:Груминг" in body
    assert "RRULE:FREQ=WEEKLY" in body
    assert f"UID:{done['id']}@petcare" not in body
    assert f"UID:{cancelled['id']}@petcare" not in body
    assert f"UID:{foreign['id']}@petcare" not in body
    assert body.index(f"UID:{earlier['id']}@petcare") < body.index(f"UID:{overdue['id']}@petcare")
    assert body.index(f"UID:{overdue['id']}@petcare") < body.index(f"UID:{later['id']}@petcare")
    assert "SUMMARY:Барсик: Просрочено" in body
    assert "RRULE:FREQ=MONTHLY" in body
    assert "TRIGGER:-PT1440M" in body
    assert "DESCRIPTION:Прививка\\n\\nзаметка" in body
    assert exported._value.get() == before + 1


def test_calendar_pet_filter_changes_the_filename(client, auth, pet_id):
    other = _pet(client, auth, "Рекс", DOG_BREED_ID)
    own = _create(client, auth, pet_id, name="Своё").json()
    rex = _create(client, auth, other, name="Для Рекса", type="grooming").json()
    response = client.get("/api/v1/events/calendar.ics", params={"petId": pet_id}, headers=auth)
    assert response.status_code == 200, response.text
    assert response.headers["content-disposition"] == f'attachment; filename="petcare-{pet_id}.ics"'
    assert f"UID:{own['id']}@petcare" in response.text
    assert f"UID:{rex['id']}@petcare" not in response.text
    assert "SUMMARY:Барсик: Своё" in response.text
    assert "Груминг" not in response.text


def test_calendar_missing_or_foreign_pet(client, auth):
    _, stranger = register_user(client, login="other-owner")
    foreign_pet = _pet(client, stranger, "Мурка", CAT_BREED_ID)
    for pet in (foreign_pet, str(uuid.uuid4())):
        response = client.get("/api/v1/events/calendar.ics", params={"petId": pet}, headers=auth)
        assert response.status_code == 404
        assert response.json()["code"] == "NOT_FOUND"
        assert response.json()["message"] == "Pet not found"


def test_calendar_alarm_minutes(client, auth, pet_id):
    _create(client, auth, pet_id)
    silent = client.get("/api/v1/events/calendar.ics", params={"alarmMinutes": 0}, headers=auth)
    assert silent.status_code == 200
    assert "VALARM" not in silent.text
    assert client.get("/api/v1/events/calendar.ics", params={"alarmMinutes": -1}, headers=auth).status_code == 422
    assert client.get("/api/v1/events/calendar.ics", params={"alarmMinutes": 10081}, headers=auth).status_code == 422
    edge = client.get("/api/v1/events/calendar.ics", params={"alarmMinutes": 10080}, headers=auth)
    assert edge.status_code == 200
    assert "TRIGGER:-PT10080M" in edge.text
