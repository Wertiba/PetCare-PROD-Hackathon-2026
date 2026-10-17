"""Paths the happy-flow tests do not reach: database outages, deactivated and deleted accounts,
password rules and partial updates."""

import re
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from conftest import DOG_BREED_ID, register_user
from sqlalchemy import delete, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.health import SqlAlchemyDatabaseHealth
from app.infra.database.mappings import refresh_tokens, users


async def _set_active(db_session_factory, user_id: str, active: bool) -> None:
    async with db_session_factory() as session:
        await session.execute(update(users).where(users.c.id == uuid.UUID(user_id)).values(is_active=active))
        await session.commit()


@pytest.mark.req("P.OBS")
def test_readiness_reports_ready_database(client):
    response = client.get("/health/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {"database": "ready"}}


@pytest.mark.req("P.OBS")
def test_readiness_reports_unavailable_database(client, monkeypatch):
    async def down(self):
        raise ConnectionRefusedError("connection refused")

    monkeypatch.setattr(SqlAlchemyDatabaseHealth, "check", down)
    response = client.get("/health/readiness")
    assert response.status_code == 503
    assert response.json() == {"status": "not ready", "checks": {"database": "not ready: connection refused"}}


@pytest.mark.req("P.OBS", "P.ACCESS")
@pytest.mark.parametrize(
    ("path", "table"),
    [
        ("/api/v1/pets", "pets"),
        ("/api/v1/events", "events"),
        ("/api/v1/events/upcoming", "events"),
        ("/api/v1/states", "states"),
        ("/api/v1/foods", "food"),
        ("/api/v1/notes", "notes"),
        ("/api/v1/notifications", "notifications"),
        ("/api/v1/categories", "categories"),
        ("/api/v1/animals", "animals"),
        ("/api/v1/breeds", "breeds"),
        ("/api/v1/users/me", "users"),
    ],
)
def test_database_outage_returns_uniform_500(client, auth, monkeypatch, path, table):
    """A failing query becomes 500 INTERNAL_ERROR with the trace id, never a stack trace or a partial answer."""
    original = AsyncSession.execute
    reads_table = re.compile(rf"\bFROM {table}\b")
    # Authentication reads users once before the endpoint does; let that read through.
    skip = 1 if table == "users" else 0
    seen = 0

    async def failing(self, statement, *args, **kwargs):
        nonlocal seen
        if reads_table.search(str(statement)):
            seen += 1
            if seen > skip:
                raise OperationalError(str(statement), {}, Exception("server closed the connection"))
        return await original(self, statement, *args, **kwargs)

    monkeypatch.setattr(AsyncSession, "execute", failing)
    response = client.get(path, headers=auth)
    assert response.status_code == 500, response.text
    body = response.json()
    assert body["code"] == "INTERNAL_ERROR"
    assert body["traceId"] == response.headers["x-trace-id"]
    assert "server closed" not in response.text


@pytest.mark.req("P.AUTH", "P.ACCESS")
async def test_deactivated_user_cannot_log_in_refresh_or_use_tokens(client, db_session_factory):
    user_id, headers = register_user(client, login="blocked", password="password1")
    refresh_cookie = client.cookies.get("refreshToken")
    await _set_active(db_session_factory, user_id, False)

    login = client.post("/api/v1/auth/login", json={"login": "blocked", "password": "password1"})
    assert login.status_code == 423
    assert login.json()["code"] == "USER_INACTIVE"
    assert client.get("/api/v1/users/me", headers=headers).status_code == 401
    client.cookies.set("refreshToken", refresh_cookie)
    assert client.post("/api/v1/auth/refresh").status_code == 401


@pytest.mark.req("P.AUTH")
async def test_token_of_a_deleted_user_is_rejected(client, db_session_factory):
    user_id, headers = register_user(client, login="gone")
    async with db_session_factory() as session:
        await session.execute(delete(refresh_tokens).where(refresh_tokens.c.user_id == uuid.UUID(user_id)))
        await session.execute(delete(users).where(users.c.id == uuid.UUID(user_id)))
        await session.commit()
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.req("P.AUTH", "7.1")
@pytest.mark.parametrize(
    ("password", "issue"),
    [
        ("short1", "between 8 and 72"),
        ("onlyletters", "at least one digit"),
        ("1234567890", "at least one letter"),
    ],
)
def test_password_rules_point_at_the_password_field(client, password, issue):
    response = client.post("/api/v1/auth/register", json={"login": "weak", "password": password, "fullName": "Weak"})
    assert response.status_code == 422
    [error] = response.json()["fieldErrors"]
    assert error["field"] == "password"
    assert issue in error["issue"]


@pytest.mark.req("5.2.5")
def test_state_patch_changes_only_the_given_fields(client, auth, pet_id, system_categories):
    created = client.post(
        "/api/v1/states",
        json={"petId": pet_id, "categoryId": system_categories["appetite"], "value": 3, "time": 1780000000.0},
        headers=auth,
    ).json()
    url = f"/api/v1/states/{created['id']}"

    assert client.patch(url, json={}, headers=auth).json() == created
    assert client.patch(url, json={"value": 5}, headers=auth).json()["value"] == 5
    assert client.patch(url, json={"time": 1780003600.0}, headers=auth).json()["time"] == 1780003600.0
    final = client.patch(url, json={"note": "Съел всё"}, headers=auth).json()
    assert (final["value"], final["time"], final["note"]) == (5, 1780003600.0, "Съел всё")
    out_of_scale = client.patch(url, json={"value": 9}, headers=auth)
    assert out_of_scale.status_code == 422
    assert out_of_scale.json()["code"] == "INVALID_VALUE"


@pytest.mark.req("5.4.6", "P.ACCESS")
def test_upcoming_can_be_narrowed_to_one_pet(client, auth, pet_id):
    other_pet = client.post("/api/v1/pets", json={"name": "Шарик", "breedId": DOG_BREED_ID}, headers=auth).json()["id"]
    soon = (datetime.now(UTC) + timedelta(days=2)).timestamp()
    for pet in (pet_id, other_pet):
        client.post("/api/v1/events", json={"petId": pet, "name": "Прививка", "schedule": soon}, headers=auth)

    everything = client.get("/api/v1/events/upcoming", headers=auth).json()
    only_barsik = client.get("/api/v1/events/upcoming", params={"petId": pet_id}, headers=auth).json()
    assert everything["total"] == 2
    assert [item["petId"] for item in only_barsik["items"]] == [pet_id]
