import os
from contextlib import asynccontextmanager

for _key, _value in {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "petcare_test",
    "DB_USER": "postgres",
    "DB_PASSWORD": "postgres",
    "APP_SECURITY_JWT_SECRET": "test-secret-not-for-production-0123456789",
    "APP_SECURITY_ACCESS_TOKEN_EXPIRATION": "15m",
    "APP_SECURITY_REFRESH_TOKEN_EXPIRATION": "30d",
    "APP_COOKIE_SECURE": "true",
}.items():
    os.environ.setdefault(_key, _value)
import pytest
from sqlalchemy import event
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app.infra.database.db_helper import db_helper
from app.infra.database.mappings import metadata
from app.main import app


@pytest.fixture
async def db_session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@asynccontextmanager
async def _client_bound_to(session_factory):
    original_session_factory = db_helper.session_factory
    db_helper.session_factory = session_factory
    try:
        with TestClient(app, base_url="https://testserver") as test_client:
            yield test_client
    finally:
        db_helper.session_factory = original_session_factory


# Ids need hex letters: SQLite gives a UUID column numeric affinity, and all-digit ids collapse into equal floats.
CAT_ID = "c0000000-0000-4000-a000-00000000000a"
DOG_ID = "d0000000-0000-4000-a000-00000000000b"
CAT_BREED_ID = "c0000000-0000-4000-8000-0000000000c1"
DOG_BREED_ID = "d0000000-0000-4000-8000-0000000000d1"


@pytest.fixture
async def catalog(db_session_factory):
    """Animals and breeds the migration seeds in Postgres, trimmed to what tests need."""
    import uuid
    from app.infra.database.mappings import Animal, Breed

    async with db_session_factory() as session:
        session.add_all([Animal(id=uuid.UUID(CAT_ID), name="Кошка"), Animal(id=uuid.UUID(DOG_ID), name="Собака")])
        await session.flush()
        session.add_all(
            [
                Breed(id=uuid.UUID(CAT_BREED_ID), animal_id=uuid.UUID(CAT_ID), name="Британская короткошерстная"),
                Breed(id=uuid.UUID(DOG_BREED_ID), animal_id=uuid.UUID(DOG_ID), name="Лабрадор-ретривер"),
            ]
        )
        await session.commit()


@pytest.fixture
async def client(db_session_factory, catalog):
    async with _client_bound_to(db_session_factory) as test_client:
        yield test_client


def register_user(client, login="user", password="password1", full_name="Test User"):
    response = client.post("/api/v1/auth/register", json={"login": login, "password": password, "fullName": full_name})
    assert response.status_code == 201, response.text
    body = response.json()
    return (body["user"]["id"], {"Authorization": f"Bearer {body['accessToken']}"})


async def make_admin(db_session_factory, user_id: str) -> None:
    import uuid
    from sqlalchemy import update
    from app.domain.users.enums import UserRole
    from app.infra.database.mappings import users

    async with db_session_factory() as session:
        await session.execute(update(users).where(users.c.id == uuid.UUID(user_id)).values(role=UserRole.ADMIN))
        await session.commit()


@pytest.fixture
async def admin(client, db_session_factory):
    """Headers of a registered user promoted to admin."""
    user_id, headers = register_user(client, login="admin")
    await make_admin(db_session_factory, user_id)
    return headers


@pytest.fixture
def auth(client):
    """Headers of a freshly registered user."""
    _, headers = register_user(client)
    return headers


@pytest.fixture
def pet_id(client, auth):
    response = client.post("/api/v1/pets", json={"name": "Барсик", "breedId": CAT_BREED_ID}, headers=auth)
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
async def system_categories(db_session_factory):
    """Built-in categories the migration seeds in Postgres."""
    import uuid
    from app.domain.categories.enums import CategoryKind
    from app.domain.categories.enums import CategoryType
    from app.domain.categories.enums import CategoryUnit
    from app.infra.database.mappings import Category

    rows = {
        "weight": Category(
            id=uuid.uuid4(), name="Вес", kind=CategoryKind.LAST, type=CategoryType.NUMBER, unit=CategoryUnit.G
        ),
        "food": Category(
            id=uuid.uuid4(), name="Корм", kind=CategoryKind.SUM, type=CategoryType.NUMBER, unit=CategoryUnit.G
        ),
        "appetite": Category(
            id=uuid.uuid4(), name="Аппетит", kind=CategoryKind.AVG, type=CategoryType.SCALE, unit=CategoryUnit.POINTS
        ),
        "liked": Category(
            id=uuid.uuid4(),
            name="Корм понравился",
            kind=CategoryKind.COUNT,
            type=CategoryType.CHECK,
            unit=CategoryUnit.NONE,
        ),
    }
    async with db_session_factory() as session:
        session.add_all(rows.values())
        await session.commit()
    return {key: str(row.id) for key, row in rows.items()}
