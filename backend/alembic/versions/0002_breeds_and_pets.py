# alembic/versions/0002_breeds_and_pets.py
"""breeds and pets

Revision ID: 0002_breeds_and_pets
Revises: 0001_initial_schema
Create Date: 2026-10-16

"""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002_breeds_and_pets"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

_PET_TYPES = "('cat', 'dog', 'rodent', 'bird', 'reptile', 'other')"

_CAT_BREEDS = (
    "Британская короткошерстная",
    "Мейн-кун",
    "Сиамская",
    "Шотландская вислоухая",
    "Персидская",
    "Бенгальская",
    "Сфинкс",
    "Рэгдолл",
    "Абиссинская",
    "Русская голубая",
    "Невская маскарадная",
    "Ориентальная",
    "Бурманская",
    "Норвежская лесная",
    "Сибирская",
    "Метис",
)

_DOG_BREEDS = (
    "Лабрадор-ретривер",
    "Немецкая овчарка",
    "Шпиц",
    "Йоркширский терьер",
    "Французский бульдог",
    "Золотистый ретривер",
    "Такса",
    "Сибирский хаски",
    "Вельш-корги пемброк",
    "Бигль",
    "Пудель",
    "Чихуахуа",
    "Доберман",
    "Ротвейлер",
    "Мопс",
    "Метис",
)


def _breed_id(number: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-4000-8000-{number:012d}")


def upgrade() -> None:
    op.create_table(
        "breeds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.CheckConstraint(f"type IN {_PET_TYPES}", name="ck_breeds_type"),
        sa.UniqueConstraint("type", "name", name="uq_breeds_type_name"),
    )

    op.create_table(
        "pets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("breed_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("photo_url", sa.String(length=255), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True, precision=6), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True, precision=6), nullable=False),
        sa.CheckConstraint(f"type IN {_PET_TYPES}", name="ck_pets_type"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_pets_user_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["breed_id"], ["breeds.id"], name="fk_pets_breed_id_breeds", ondelete="SET NULL"),
    )
    op.create_index("idx_pets_user_id", "pets", ["user_id"])

    breeds_table = sa.table(
        "breeds",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("type", sa.String),
        sa.column("name", sa.String),
    )
    rows = [
        {"id": _breed_id(index), "type": "cat", "name": name} for index, name in enumerate(_CAT_BREEDS, start=1)
    ]
    rows.extend(
        {"id": _breed_id(index), "type": "dog", "name": name} for index, name in enumerate(_DOG_BREEDS, start=101)
    )
    op.bulk_insert(breeds_table, rows)


def downgrade() -> None:
    op.drop_index("idx_pets_user_id", table_name="pets")
    op.drop_table("pets")
    op.drop_table("breeds")
