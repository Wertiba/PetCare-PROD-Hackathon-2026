"""animals instead of the pet type enum; notes and food journal

Breeds now belong to an animal, and a pet's animal is its breed's animal, so pets.type goes away.
Pets of types without a seeded animal (rodent, bird, reptile, other) keep only their breed, if any.

Revision ID: 0006_animals_notes_food
Revises: 0005_user_login
Create Date: 2026-10-17

"""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006_animals_notes_food"
down_revision = "0005_user_login"
branch_labels = None
depends_on = None

_PET_TYPES = "('cat', 'dog', 'rodent', 'bird', 'fish', 'reptile', 'other')"
_NOW = sa.text("EXTRACT(EPOCH FROM now())")

# Old pet type -> seeded animal; cat and dog breeds already exist since 0002_breeds_and_pets.
_ANIMALS = (
    ("cat", "Кошка", 1),
    ("dog", "Собака", 2),
    ("fish", "Рыбка", 3),
)
_FISH_BREEDS = ("Золотая рыбка", "Гуппи", "Петушок")


def _animal_id(number: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-4000-a000-{number:012d}")


def _breed_id(number: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-4000-8000-{number:012d}")


def _created_by(table: str) -> sa.Column:
    return sa.Column(
        "created_by",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey("users.id", name=f"fk_{table}_created_by_users", ondelete="SET NULL"),
        nullable=True,
    )


def upgrade() -> None:
    op.create_table(
        "animals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        _created_by("animals"),
        sa.Column("created_at", sa.Double(), nullable=False, server_default=_NOW),
        sa.UniqueConstraint("name", name="uq_animals_name"),
    )
    animals_table = sa.table(
        "animals", sa.column("id", postgresql.UUID(as_uuid=True)), sa.column("name", sa.String)
    )
    op.bulk_insert(animals_table, [{"id": _animal_id(number), "name": name} for _, name, number in _ANIMALS])

    op.add_column("breeds", sa.Column("animal_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("breeds", _created_by("breeds"))
    op.add_column("breeds", sa.Column("created_at", sa.Double(), nullable=False, server_default=_NOW))
    for pet_type, _, number in _ANIMALS:
        op.execute(
            sa.text("UPDATE breeds SET animal_id = :animal_id WHERE type = :type").bindparams(
                animal_id=_animal_id(number), type=pet_type
            )
        )
    # Breeds of types without an animal; none were seeded, pets referencing them lose the breed.
    op.execute("DELETE FROM breeds WHERE animal_id IS NULL")
    op.alter_column("breeds", "animal_id", nullable=False)
    op.create_foreign_key(
        "fk_breeds_animal_id_animals", "breeds", "animals", ["animal_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_constraint("uq_breeds_type_name", "breeds", type_="unique")
    op.drop_constraint("ck_breeds_type", "breeds", type_="check")
    op.drop_column("breeds", "type")
    op.create_unique_constraint("uq_breeds_animal_id_name", "breeds", ["animal_id", "name"])

    breeds_table = sa.table(
        "breeds",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("animal_id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        breeds_table,
        [
            {"id": _breed_id(index), "animal_id": _animal_id(3), "name": name}
            for index, name in enumerate(_FISH_BREEDS, start=201)
        ],
    )

    op.drop_constraint("ck_pets_type", "pets", type_="check")
    op.drop_column("pets", "type")

    op.create_table(
        "notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.String(length=2000), nullable=False),
        sa.Column("created_at", sa.Double(), nullable=False),
        sa.Column("updated_at", sa.Double(), nullable=False),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"], name="fk_notes_pet_id_pets", ondelete="CASCADE"),
    )
    op.create_index("idx_notes_pet_id", "notes", ["pet_id"])

    op.create_table(
        "food",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.Column("ingredients", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_approach", sa.Boolean(), nullable=True),
        sa.Column("is_tolerability", sa.Boolean(), nullable=True),
        sa.Column("consequences", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.Double(), nullable=False),
        sa.Column("updated_at", sa.Double(), nullable=False),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"], name="fk_food_pet_id_pets", ondelete="CASCADE"),
    )
    op.create_index("idx_food_pet_id_created_at", "food", ["pet_id", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_food_pet_id_created_at", table_name="food")
    op.drop_table("food")
    op.drop_index("idx_notes_pet_id", table_name="notes")
    op.drop_table("notes")

    animal_to_type = " ".join(
        f"WHEN '{_animal_id(number)}' THEN '{pet_type}'" for pet_type, _, number in _ANIMALS
    )
    op.add_column("pets", sa.Column("type", sa.String(length=20), nullable=True))
    op.execute(
        "UPDATE pets SET type = COALESCE("
        f"(SELECT CASE breeds.animal_id::text {animal_to_type} END FROM breeds WHERE breeds.id = pets.breed_id),"
        " 'other')"
    )
    op.alter_column("pets", "type", nullable=False)
    op.create_check_constraint("ck_pets_type", "pets", f"type IN {_PET_TYPES}")

    fish_breed_ids = ", ".join(f"'{_breed_id(index)}'" for index in range(201, 201 + len(_FISH_BREEDS)))
    op.execute(f"DELETE FROM breeds WHERE id IN ({fish_breed_ids})")
    op.add_column("breeds", sa.Column("type", sa.String(length=20), nullable=True))
    op.execute(f"UPDATE breeds SET type = COALESCE(CASE animal_id::text {animal_to_type} END, 'other')")
    op.alter_column("breeds", "type", nullable=False)
    op.drop_constraint("uq_breeds_animal_id_name", "breeds", type_="unique")
    # Admin-added animals all map to 'other' and may now clash on (type, name): keep one breed of each pair.
    op.execute(
        "DELETE FROM breeds a USING breeds b WHERE a.type = b.type AND a.name = b.name AND a.id::text > b.id::text"
    )
    op.create_unique_constraint("uq_breeds_type_name", "breeds", ["type", "name"])
    op.create_check_constraint("ck_breeds_type", "breeds", f"type IN {_PET_TYPES}")
    op.drop_constraint("fk_breeds_animal_id_animals", "breeds", type_="foreignkey")
    op.drop_column("breeds", "created_at")
    op.drop_column("breeds", "created_by")
    op.drop_column("breeds", "animal_id")
    op.drop_table("animals")
