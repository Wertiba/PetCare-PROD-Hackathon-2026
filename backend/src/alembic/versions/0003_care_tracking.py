# src/alembic/versions/0003_care_tracking.py
"""care tracking: categories, states, events, notifications; fish pet type

Revision ID: 0003_care_tracking
Revises: 0002_breeds_and_pets
Create Date: 2026-10-17

"""

import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0003_care_tracking"
down_revision = "0002_breeds_and_pets"
branch_labels = None
depends_on = None

_OLD_PET_TYPES = "('cat', 'dog', 'rodent', 'bird', 'reptile', 'other')"
_PET_TYPES = "('cat', 'dog', 'rodent', 'bird', 'fish', 'reptile', 'other')"
_CATEGORY_KINDS = "('sum', 'avg', 'last', 'count', 'min', 'max')"
_CATEGORY_TYPES = "('check', 'number', 'scale')"
_CATEGORY_UNITS = "('none', 'g', 'ml', 'min', 'm', 'times', 'rub', 'points')"
_EVENT_TYPES = "('vaccination', 'parasite_treatment', 'vet_visit', 'medication', 'grooming', 'other')"
_EVENT_STATUSES = "('planned', 'done', 'skipped', 'cancelled')"
_EVENT_PERIODS = "('none', 'daily', 'weekly', 'monthly', 'quarterly', 'half_year', 'yearly')"
_NOTIFICATION_TYPES = "('app', 'telegram', 'web_push')"
_NOTIFICATION_STATUSES = "('pending', 'sent', 'read', 'failed')"

# Built-in categories visible to every user (created_by IS NULL): name, kind, type, unit.
_SYSTEM_CATEGORIES = (
    ("Вес", "last", "number", "g"),
    ("Корм", "sum", "number", "g"),
    ("Вода", "sum", "number", "ml"),
    ("Прогулка", "sum", "number", "min"),
    ("Активность", "avg", "scale", "points"),
    ("Аппетит", "avg", "scale", "points"),
    ("Настроение", "avg", "scale", "points"),
    ("Корм понравился", "count", "check", "none"),
    ("Корм подошёл", "count", "check", "none"),
    ("Проблемы с ЖКТ", "count", "check", "none"),
    ("Аллергическая реакция", "count", "check", "none"),
    ("Лекарство дано", "count", "check", "none"),
    ("Расходы", "sum", "number", "rub"),
)


def _category_id(number: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-4000-9000-{number:012d}")


def _timestamp(name: str, nullable: bool = False) -> sa.Column:
    return sa.Column(name, postgresql.TIMESTAMP(timezone=True, precision=6), nullable=nullable)


def upgrade() -> None:
    for table in ("pets", "breeds"):
        op.drop_constraint(f"ck_{table}_type", table, type_="check")
        op.create_check_constraint(f"ck_{table}_type", table, f"type IN {_PET_TYPES}")

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        _timestamp("created_at"),
        sa.CheckConstraint(f"kind IN {_CATEGORY_KINDS}", name="ck_categories_kind"),
        sa.CheckConstraint(f"type IN {_CATEGORY_TYPES}", name="ck_categories_type"),
        sa.CheckConstraint(f"unit IN {_CATEGORY_UNITS}", name="ck_categories_unit"),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_categories_created_by_users", ondelete="CASCADE"
        ),
    )
    op.create_index("idx_categories_created_by", "categories", ["created_by"])

    op.create_table(
        "states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(length=1000), nullable=True),
        _timestamp("time"),
        _timestamp("created_at"),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"], name="fk_states_pet_id_pets", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["cat_id"], ["categories.id"], name="fk_states_cat_id_categories", ondelete="CASCADE"
        ),
    )
    op.create_index("idx_states_pet_id_cat_id_time", "states", ["pet_id", "cat_id", "time"])

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        _timestamp("schedule"),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        _timestamp("done_at", nullable=True),
        _timestamp("created_at"),
        _timestamp("updated_at"),
        sa.CheckConstraint(f"type IN {_EVENT_TYPES}", name="ck_events_type"),
        sa.CheckConstraint(f"status IN {_EVENT_STATUSES}", name="ck_events_status"),
        sa.CheckConstraint(f"period IN {_EVENT_PERIODS}", name="ck_events_period"),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"], name="fk_events_pet_id_pets", ondelete="CASCADE"),
    )
    op.create_index("idx_events_pet_id", "events", ["pet_id"])
    op.create_index("idx_events_status_schedule", "events", ["status", "schedule"])

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        _timestamp("time"),
        _timestamp("created_at"),
        sa.CheckConstraint(f"type IN {_NOTIFICATION_TYPES}", name="ck_notifications_type"),
        sa.CheckConstraint(f"status IN {_NOTIFICATION_STATUSES}", name="ck_notifications_status"),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], name="fk_notifications_event_id_events", ondelete="CASCADE"
        ),
    )
    op.create_index("idx_notifications_event_id", "notifications", ["event_id"])
    op.create_index("idx_notifications_status_time", "notifications", ["status", "time"])

    categories_table = sa.table(
        "categories",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("kind", sa.String),
        sa.column("type", sa.String),
        sa.column("unit", sa.String),
        sa.column("created_by", postgresql.UUID(as_uuid=True)),
        sa.column("created_at", postgresql.TIMESTAMP(timezone=True)),
    )
    now = datetime.now(UTC)
    op.bulk_insert(
        categories_table,
        [
            {
                "id": _category_id(index),
                "name": name,
                "kind": kind,
                "type": type_,
                "unit": unit,
                "created_by": None,
                "created_at": now,
            }
            for index, (name, kind, type_, unit) in enumerate(_SYSTEM_CATEGORIES, start=1)
        ],
    )


def downgrade() -> None:
    op.drop_index("idx_notifications_status_time", table_name="notifications")
    op.drop_index("idx_notifications_event_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("idx_events_status_schedule", table_name="events")
    op.drop_index("idx_events_pet_id", table_name="events")
    op.drop_table("events")
    op.drop_index("idx_states_pet_id_cat_id_time", table_name="states")
    op.drop_table("states")
    op.drop_index("idx_categories_created_by", table_name="categories")
    op.drop_table("categories")

    op.execute("DELETE FROM pets WHERE type = 'fish'")
    op.execute("DELETE FROM breeds WHERE type = 'fish'")
    for table in ("pets", "breeds"):
        op.drop_constraint(f"ck_{table}_type", table, type_="check")
        op.create_check_constraint(f"ck_{table}_type", table, f"type IN {_OLD_PET_TYPES}")
