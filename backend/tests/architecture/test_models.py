import pytest
from sqlalchemy import create_engine, inspect
from app.domain.users.enums import UserRole
from app.infra.database.mappings import metadata, RefreshToken, User

pytestmark = pytest.mark.req("P.ARCH")


def test_tables_have_expected_columns():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == {
        "users",
        "refresh_tokens",
        "animals",
        "breeds",
        "pets",
        "categories",
        "states",
        "events",
        "notifications",
        "notification_settings",
        "web_push_subscriptions",
        "notes",
        "food",
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
    assert breed_columns == {"id", "animal_id", "name", "created_by", "created_at"}
    assert {c["name"] for c in inspector.get_columns("animals")} == {"id", "name", "created_by", "created_at"}
    pet_columns = {c["name"] for c in inspector.get_columns("pets")}
    assert pet_columns == {
        "id",
        "user_id",
        "breed_id",
        "name",
        "birth_date",
        "photo_key",
        "generated_avatar_key",
        "avatar_source",
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
        "category_id",
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
        "delivered_at",
    }
    assert {c["name"] for c in inspector.get_columns("notification_settings")} == {
        "user_id",
        "web_push_enabled",
    }
    assert {c["name"] for c in inspector.get_columns("web_push_subscriptions")} == {
        "id",
        "user_id",
        "endpoint",
        "p256dh",
        "auth",
        "created_at",
    }
    assert {c["name"] for c in inspector.get_columns("notes")} == {
        "id",
        "pet_id",
        "content",
        "created_at",
        "updated_at",
    }
    assert {c["name"] for c in inspector.get_columns("food")} == {
        "id",
        "pet_id",
        "name",
        "weight",
        "ingredients",
        "is_approach",
        "is_tolerability",
        "consequences",
        "created_at",
        "updated_at",
    }


def test_user_role_enum_values():
    assert {member.value for member in UserRole} == {"USER", "ADMIN"}


def test_avatar_source_enum_values():
    from app.domain.pets.enums import AvatarSource

    assert {member.value for member in AvatarSource} == {"photo", "generated"}


def test_pet_avatar_migration_converts_legacy_photo_url_and_reverts():
    import io
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    output = io.StringIO()
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"), output_buffer=output)
    command.upgrade(config, "0007_jury_users:0008_pet_avatars", sql=True)
    sql = output.getvalue()
    assert "RENAME photo_url TO photo_key" in sql
    assert "regexp_replace(photo_key, '^/media/', '')" in sql
    assert "photo_key LIKE '/media/pets/%'" in sql
    assert "generated_avatar_key" in sql
    assert "avatar_source" in sql
    assert "ck_pets_avatar_source" in sql
    assert "avatar_source IN ('photo', 'generated')" in sql
    output = io.StringIO()
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"), output_buffer=output)
    command.downgrade(config, "0008_pet_avatars:0007_jury_users", sql=True)
    sql = output.getvalue()
    assert "DROP CONSTRAINT ck_pets_avatar_source" in sql
    assert "DROP COLUMN generated_avatar_key" in sql
    assert "DROP COLUMN avatar_source" in sql
    assert "'/media/' || photo_key" not in sql
    assert "RENAME photo_key TO photo_url" in sql


def test_seed_admin_migration_creates_admin_and_owns_seeded_catalog(monkeypatch):
    import io
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    monkeypatch.setenv("ADMIN_LOGIN", "seed-admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "seed-admin-password")
    output = io.StringIO()
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"), output_buffer=output)
    command.upgrade(config, "0010_notification_delivery:0011_seed_admin", sql=True)
    sql = output.getvalue()
    assert "'seed-admin'" in sql
    assert "'ADMIN'" in sql
    assert "seed-admin-password" not in sql
    assert "ON CONFLICT (login) DO NOTHING" in sql
    for table in ("animals", "breeds"):
        assert f"UPDATE {table} SET created_by = (SELECT id FROM users WHERE login = 'seed-admin')" in sql
    output = io.StringIO()
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"), output_buffer=output)
    command.downgrade(config, "0011_seed_admin:0010_notification_delivery", sql=True)
    sql = output.getvalue()
    assert "UPDATE animals SET created_by = NULL" in sql
    assert "DELETE FROM users WHERE id = '00000000-0000-4000-c000-000000000001'" in sql


def test_schemas_user_role_is_the_canonical_enum():
    from app.presentation.http.schemas.user import UserRole as SchemaUserRole

    assert SchemaUserRole is UserRole


def _migration_sql(revisions: str, *, downgrade: bool = False) -> str:
    import io
    from pathlib import Path
    from alembic import command
    from alembic.config import Config

    output = io.StringIO()
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"), output_buffer=output)
    (command.downgrade if downgrade else command.upgrade)(config, revisions, sql=True)
    return output.getvalue()


def test_alembic_revision_chain_has_a_single_head():
    from pathlib import Path

    from alembic.config import Config
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config(str(Path(__file__).parents[2] / "alembic.ini")))
    assert script.get_heads() == ["0011_seed_admin"]


def test_notification_delivery_migration_adds_channel_storage_and_reverts():
    sql = _migration_sql("0009_jury_demo_data:0010_notification_delivery")
    assert "delivered_at" in sql
    assert "notification_settings" in sql
    assert "web_push_enabled" in sql
    assert "web_push_subscriptions" in sql
    assert "uq_web_push_subscriptions_endpoint" in sql
    back = _migration_sql("0010_notification_delivery:0009_jury_demo_data", downgrade=True)
    assert "DROP TABLE web_push_subscriptions" in back
    assert "DROP TABLE notification_settings" in back
    assert "DROP COLUMN delivered_at" in back


def test_category_id_migration_renames_column_constraint_and_index_in_place():
    sql = _migration_sql("0008_pet_avatars:0008_states_category_id")
    assert "ALTER TABLE states RENAME cat_id TO category_id" in sql
    assert "RENAME CONSTRAINT fk_states_cat_id_categories TO fk_states_category_id_categories" in sql
    assert "ALTER INDEX idx_states_pet_id_cat_id_time RENAME TO idx_states_pet_id_category_id_time" in sql
    assert "DROP COLUMN" not in sql
    back = _migration_sql("0008_states_category_id:0008_pet_avatars", downgrade=True)
    assert "ALTER TABLE states RENAME category_id TO cat_id" in back
    assert "RENAME TO idx_states_pet_id_cat_id_time" in back
