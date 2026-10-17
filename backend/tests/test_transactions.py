import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from conftest import register_user
from app.domain.events.entity import Event
from app.domain.pets.entity import Pet
from app.domain.refresh_tokens.entity import RefreshToken
from app.domain.users.entity import User
from app.domain.events.enums import EventStatus
from app.infra.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infra.gateways.pet import SqlAlchemyPetGateway
from app.infra.gateways.user import SqlAlchemyUserGateway
from app.infra.metrics import DOMAIN_EVENTS_TOTAL

pytestmark = pytest.mark.req("P.TX")


async def fail_after_flush(session):
    await session.flush()
    raise SQLAlchemyError("Simulated commit failure")


def test_commit_time_duplicate_login_keeps_the_existing_error_contract(client, monkeypatch):
    payload = {"login": "race", "password": "password1", "fullName": "Race User"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    monkeypatch.setattr(SqlAlchemyUserGateway, "get_by_login", AsyncMock(return_value=None))
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["code"] == "LOGIN_ALREADY_EXISTS"
    assert response.json()["details"] == {"field": "login", "value": payload["login"]}
    assert "set-cookie" not in response.headers


async def test_failed_registration_rolls_back_user_and_token(client, db_session_factory, monkeypatch):
    counter = DOMAIN_EVENTS_TOTAL.labels(entity="user", action="registered")
    before = counter._value.get()
    monkeypatch.setattr(AsyncSession, "commit", fail_after_flush)
    response = client.post(
        "/api/v1/auth/register", json={"login": "fail", "password": "password1", "fullName": "Test User"}
    )
    assert response.status_code == 500
    assert "set-cookie" not in response.headers
    assert counter._value.get() == before
    async with db_session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(User)) == 0
        assert await session.scalar(select(func.count()).select_from(RefreshToken)) == 0


async def test_failed_rotation_preserves_original_refresh_token(client, db_session_factory, monkeypatch):
    register_user(client)
    original = client.cookies["refreshToken"]
    with monkeypatch.context() as patch:
        patch.setattr(AsyncSession, "commit", fail_after_flush)
        response = client.post("/api/v1/auth/refresh")
        assert response.status_code == 500
        assert "set-cookie" not in response.headers
    assert client.cookies["refreshToken"] == original
    assert client.post("/api/v1/auth/refresh").status_code == 200
    async with db_session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(RefreshToken)) == 1


@pytest.mark.req("5.4.1")
async def test_failed_completion_rolls_back_both_events(client, auth, pet_id, db_session_factory, monkeypatch):
    created = client.post(
        "/api/v1/events",
        headers=auth,
        json={"petId": pet_id, "name": "Vaccination", "schedule": datetime.now(UTC).timestamp(), "period": "yearly"},
    )
    event_id = created.json()["id"]
    counter = DOMAIN_EVENTS_TOTAL.labels(entity="event", action="completed")
    before = counter._value.get()
    monkeypatch.setattr(AsyncSession, "commit", fail_after_flush)
    assert client.post(f"/api/v1/events/{event_id}/complete", headers=auth).status_code == 500
    assert counter._value.get() == before
    async with db_session_factory() as session:
        events = (await session.scalars(select(Event))).all()
        assert len(events) == 1
        assert events[0].status == EventStatus.PLANNED
        assert events[0].done_at is None


@pytest.mark.req("5.1.3")
async def test_failed_photo_update_keeps_old_file_and_removes_new_file(
    client, auth, pet_id, db_session_factory, tmp_path, monkeypatch
):
    monkeypatch.setattr("app.infra.photos.di.get_media_dir", lambda: tmp_path)
    url = f"/api/v1/pets/{pet_id}/photo"
    first = client.put(url, headers=auth, files={"file": ("pet.png", b"old photo", "image/png")})
    old_url = first.json()["photoUrl"]
    original = list((tmp_path / "pets").iterdir())
    monkeypatch.setattr(AsyncSession, "commit", fail_after_flush)
    assert client.put(url, headers=auth, files={"file": ("pet.png", b"new photo", "image/png")}).status_code == 500
    assert list((tmp_path / "pets").iterdir()) == original
    async with db_session_factory() as session:
        assert (await session.get(Pet, UUID(pet_id))).photo_url == old_url


def test_authentication_gateway_and_uow_share_one_session(client, auth, pet_id, monkeypatch):
    calls = []
    original_user = SqlAlchemyUserGateway.get_by_id
    original_pet = SqlAlchemyPetGateway.get_by_id
    original_commit = SqlAlchemyUnitOfWork.commit
    original_close = AsyncSession.close

    async def user(gateway, user_id):
        calls.append(("auth", gateway.session))
        return await original_user(gateway, user_id)

    async def pet(gateway, *args, **kwargs):
        calls.append(("pet", gateway.session))
        return await original_pet(gateway, *args, **kwargs)

    async def commit(uow):
        calls.append(("commit", uow.session))
        return await original_commit(uow)

    async def close(session):
        calls.append(("close", session))
        await original_close(session)

    monkeypatch.setattr(SqlAlchemyUserGateway, "get_by_id", user)
    monkeypatch.setattr(SqlAlchemyPetGateway, "get_by_id", pet)
    monkeypatch.setattr(SqlAlchemyUnitOfWork, "commit", commit)
    monkeypatch.setattr(AsyncSession, "close", close)
    assert client.patch(f"/api/v1/pets/{pet_id}", headers=auth, json={"name": "Updated"}).status_code == 200
    assert [name for name, _ in calls] == ["auth", "pet", "commit", "close"]
    assert all((session is calls[0][1] for _, session in calls))


def test_read_only_request_never_commits(client, auth, monkeypatch):
    commit = AsyncMock()
    monkeypatch.setattr(SqlAlchemyUnitOfWork, "commit", commit)
    assert client.get("/api/v1/users/me", headers=auth).status_code == 200
    commit.assert_not_awaited()
