from datetime import UTC, datetime
import pytest
from app.domain.events.enums import EventPeriod
from app.domain.events.periods import next_occurrence


def test_me_returns_and_updates_profile(client, auth):
    me = client.get("/api/v1/users/me", headers=auth)
    assert me.status_code == 200
    assert me.json()["login"] == "user"
    updated = client.patch("/api/v1/users/me", json={"fullName": "Новое Имя"}, headers=auth)
    assert updated.status_code == 200
    assert updated.json()["fullName"] == "Новое Имя"
    assert client.get("/api/v1/users/me", headers=auth).json()["fullName"] == "Новое Имя"
    assert client.patch("/api/v1/users/me", json={"fullName": "!"}, headers=auth).status_code == 422
    assert client.get("/api/v1/users/me").status_code == 401


def test_fish_is_a_valid_pet_type(client, auth):
    response = client.post("/api/v1/pets", json={"name": "Немо", "type": "fish"}, headers=auth)
    assert response.status_code == 201
    assert response.json()["userId"]


def test_metrics_endpoint_exposes_request_and_domain_counters(client, auth, pet_id):
    client.get(f"/api/v1/pets/{pet_id}", headers=auth)
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert 'petcare_http_requests_total{method="GET",path="/api/v1/pets/{pet_id}",status="200"}' in text
    assert "petcare_http_request_duration_seconds_bucket" in text
    assert 'petcare_domain_events_total{action="created",entity="pet"}' in text


def test_trace_id_is_echoed_and_used_in_errors(client):
    response = client.get("/api/v1/pets", headers={"X-Trace-Id": "my-trace-123"})
    assert response.status_code == 401
    assert response.headers["X-Trace-Id"] == "my-trace-123"
    assert response.json()["traceId"] == "my-trace-123"


def test_validation_error_with_non_uuid_trace_id(client):
    response = client.post("/api/v1/auth/login", json={}, headers={"X-Trace-Id": "not-a-uuid"})
    assert response.status_code == 422
    assert response.json()["traceId"] == "not-a-uuid"


@pytest.mark.parametrize(
    ("period", "expected"),
    [
        (EventPeriod.NONE, None),
        (EventPeriod.DAILY, datetime(2026, 1, 31, 9, tzinfo=UTC)),
        (EventPeriod.WEEKLY, datetime(2026, 2, 6, 9, tzinfo=UTC)),
        (EventPeriod.MONTHLY, datetime(2026, 2, 28, 9, tzinfo=UTC)),
        (EventPeriod.QUARTERLY, datetime(2026, 4, 30, 9, tzinfo=UTC)),
        (EventPeriod.HALF_YEAR, datetime(2026, 7, 30, 9, tzinfo=UTC)),
        (EventPeriod.YEARLY, datetime(2027, 1, 30, 9, tzinfo=UTC)),
    ],
)
def test_next_occurrence(period, expected):
    base = datetime(2026, 1, 30, 9, tzinfo=UTC)
    assert next_occurrence(base.timestamp(), period) == (expected.timestamp() if expected else None)
