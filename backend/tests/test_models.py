from sqlalchemy import create_engine, inspect
from app.domain.users.enums import UserRole
from app.infra.database.mappings import metadata, RefreshToken, User


def test_tables_have_expected_columns():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == {
        "users",
        "refresh_tokens",
        "breeds",
        "pets",
        "categories",
        "states",
        "events",
        "notifications",
    }
    user_columns = {c["name"] for c in inspector.get_columns("users")}
    assert user_columns == {
        "id",
        "login",
        "password",
        "full_name",
        "role",
        "is_active",
        "created_by",
        "created_at",
        "updated_at",
    }
    token_columns = {c["name"] for c in inspector.get_columns("refresh_tokens")}
    assert token_columns == {"id", "user_id", "hashed_token", "expires_at", "created_at"}
    breed_columns = {c["name"] for c in inspector.get_columns("breeds")}
    assert breed_columns == {"id", "type", "name"}
    pet_columns = {c["name"] for c in inspector.get_columns("pets")}
    assert pet_columns == {
        "id",
        "user_id",
        "type",
        "breed_id",
        "name",
        "birth_date",
        "photo_url",
        "created_at",
        "updated_at",
    }
    assert {c["name"] for c in inspector.get_columns("categories")} == {
        "id",
        "name",
        "kind",
        "type",
        "unit",
        "created_by",
        "created_at",
    }
    assert {c["name"] for c in inspector.get_columns("states")} == {
        "id",
        "pet_id",
        "cat_id",
        "value",
        "note",
        "time",
        "created_at",
    }
    assert {c["name"] for c in inspector.get_columns("events")} == {
        "id",
        "pet_id",
        "name",
        "type",
        "status",
        "schedule",
        "period",
        "description",
        "done_at",
        "created_at",
        "updated_at",
    }
    assert {c["name"] for c in inspector.get_columns("notifications")} == {
        "id",
        "event_id",
        "type",
        "status",
        "time",
        "created_at",
    }


def test_user_role_enum_values():
    assert {member.value for member in UserRole} == {"USER", "ADMIN"}


def test_schemas_user_role_is_the_canonical_enum():
    from app.presentation.http.schemas.user import UserRole as SchemaUserRole

    assert SchemaUserRole is UserRole
