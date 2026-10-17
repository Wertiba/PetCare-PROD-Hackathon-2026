import io
import json
from datetime import UTC, datetime
from pathlib import Path
from time import time

import pytest
from conftest import CAT_BREED_ID
from alembic import command
from alembic.config import Config
from sqlalchemy import Double

from app.domain.events.enums import EventPeriod
from app.domain.events.periods import next_occurrence
from app.infra.database.mappings import metadata


def test_fractional_timestamp_roundtrip_and_epoch_zero(client, auth, pet_id, system_categories):
    instant = 1770000000.125
    event = client.post(
        "/api/v1/events",
        headers=auth,
        json={"petId": pet_id, "name": "Fractional", "schedule": instant},
    )
    assert event.status_code == 201
    body = event.json()
    assert body["schedule"] == instant
    assert isinstance(body["createdAt"], float)
    assert isinstance(body["updatedAt"], float)
    notification = client.post("/api/v1/notifications", headers=auth, json={"eventId": body["id"], "time": 0})
    assert notification.status_code == 201
    assert notification.json()["time"] == 0.0
    completed = client.post(f"/api/v1/events/{body['id']}/complete", headers=auth, json={"doneAt": 0})
    assert completed.status_code == 200
    assert completed.json()["event"]["doneAt"] == 0.0
    state = client.post(
        "/api/v1/states",
        headers=auth,
        json={"petId": pet_id, "catId": system_categories["weight"], "value": 1, "time": 0},
    )
    assert state.status_code == 201
    assert state.json()["time"] == 0.0
    selected = client.get("/api/v1/states", headers=auth, params={"from": 0, "to": 0})
    assert selected.json()["total"] == 1
    summary = client.get(
        "/api/v1/states/summary",
        headers=auth,
        params={"petId": pet_id, "catId": system_categories["weight"], "from": 0, "to": 0},
    )
    assert summary.json()["from"] == 0.0
    assert summary.json()["to"] == 0.0


def test_birth_timestamp_normalizes_to_utc_midnight(client, auth):
    response = client.post(
        "/api/v1/pets",
        headers=auth,
        json={"name": "Epoch", "breedId": CAT_BREED_ID, "birthDate": 43200.5},
    )
    assert response.status_code == 201
    assert response.json()["birthDate"] == 0.0


def test_iso_dates_are_rejected_and_error_timestamps_are_numeric(client, auth, pet_id):
    before = time()
    response = client.post(
        "/api/v1/events", headers=auth, json={"petId": pet_id, "name": "Old format", "schedule": "2026-01-01T00:00:00Z"}
    )
    assert response.status_code == 422
    assert before <= response.json()["timestamp"] <= time()
    assert client.get("/api/v1/events", headers=auth, params={"from": "2026-01-01"}).status_code == 422
    assert isinstance(client.get("/api/v1/users/me").json()["timestamp"], float)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_query_timestamps_return_validation_errors(client, auth, value):
    response = client.get("/api/v1/events", headers=auth, params={"from": value})
    assert response.status_code == 422


def test_calendar_recurrence_preserves_fractional_seconds_and_clamps_leap_days():
    base = datetime(2024, 2, 29, 12, 30, 0, 125000, tzinfo=UTC).timestamp()
    expected = datetime(2025, 2, 28, 12, 30, 0, 125000, tzinfo=UTC).timestamp()
    assert next_occurrence(base, EventPeriod.YEARLY) == expected
    assert next_occurrence(0.125, EventPeriod.DAILY) == 86400.125


@pytest.mark.parametrize("value", [1e100, -1e100, 253402300800.0, -62135596801.0])
@pytest.mark.parametrize("operation", ["create", "update", "complete"])
def test_unsupported_event_timestamps_return_422_without_writes(client, auth, pet_id, value, operation):
    payload = {"petId": pet_id, "name": "Recurring", "schedule": 1770000000.125, "period": "monthly"}
    if operation == "create":
        response = client.post("/api/v1/events", headers=auth, json={**payload, "schedule": value})
        field = "schedule"
    else:
        original = client.post("/api/v1/events", headers=auth, json=payload).json()
        url = f"/api/v1/events/{original['id']}"
        if operation == "update":
            response = client.patch(url, headers=auth, json={"schedule": value})
            field = "schedule"
        else:
            response = client.post(f"{url}/complete", headers=auth, json={"doneAt": value})
            field = "doneAt"
        assert client.get(url, headers=auth).json() == original
    assert response.status_code == 422
    assert response.json()["fieldErrors"][0]["field"] == field
    assert response.json()["fieldErrors"][0]["rejectedValue"] == value
    assert client.get("/api/v1/events", headers=auth).json()["total"] == (0 if operation == "create" else 1)


def test_all_persistent_instant_columns_are_numeric():
    names = {"created_at", "updated_at", "expires_at", "birth_date", "time", "schedule", "done_at"}
    columns = [column for table in metadata.tables.values() for column in table.columns if column.name in names]
    assert len(columns) == 22
    assert all(isinstance(column.type, Double) for column in columns)


def test_timestamp_migration_has_explicit_utc_and_reversible_conversions():
    upgrade_output = io.StringIO()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"), output_buffer=upgrade_output)
    command.upgrade(config, "0003_care_tracking:0004_epoch_timestamps", sql=True)
    sql = upgrade_output.getvalue()
    assert sql.count("TYPE DOUBLE PRECISION") == 16
    assert sql.count("EXTRACT(EPOCH FROM") == 16
    assert "\"birth_date\"::timestamp AT TIME ZONE 'UTC'" in sql
    downgrade_output = io.StringIO()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"), output_buffer=downgrade_output)
    command.downgrade(config, "0004_epoch_timestamps:0003_care_tracking", sql=True)
    sql = downgrade_output.getvalue()
    assert sql.count("to_timestamp(") == 16
    assert "AT TIME ZONE 'UTC')::date" in sql


def test_documented_timestamp_fields_are_numbers():
    schema = json.loads((Path(__file__).parents[1] / "docs/openapi.json").read_text())
    fields = {
        "UserReadResponse": ["createdAt", "updatedAt"],
        "PetReadResponse": ["birthDate", "createdAt", "updatedAt"],
        "EventReadResponse": ["schedule", "doneAt", "nextSchedule", "createdAt", "updatedAt"],
        "StateReadResponse": ["time", "createdAt"],
        "NotificationReadResponse": ["time", "createdAt"],
        "ErrorResponse": ["timestamp"],
    }
    for model, names in fields.items():
        for name in names:
            field = schema["components"]["schemas"][model]["properties"][name]
            variants = field.get("anyOf", [field])
            assert any(variant.get("type") == "number" for variant in variants), (model, name)
            assert all(variant.get("format") not in ["date", "date-time"] for variant in variants)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_body_timestamps_return_validation_errors(client, auth, pet_id, value):
    response = client.post(
        "/api/v1/events",
        headers={**auth, "Content-Type": "application/json"},
        content='{"petId": "' + pet_id + '", "name": "Invalid", "schedule": ' + value + "}",
    )
    assert response.status_code == 422
    assert response.json()["fieldErrors"][0]["field"] == "schedule"
    assert isinstance(response.json()["fieldErrors"][0]["rejectedValue"], str)
