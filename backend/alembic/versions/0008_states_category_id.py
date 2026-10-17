"""Rename states.cat_id to category_id, with its foreign key and index, keeping existing measurements.

Revision ID: 0008_states_category_id
Revises: 0007_jury_users
"""

import sqlalchemy as sa

from alembic import op

revision = "0008_states_category_id"
down_revision = "0007_jury_users"
branch_labels = None
depends_on = None


def _rename(old: str, new: str) -> None:
    op.alter_column("states", old, new_column_name=new, existing_type=sa.Uuid(), existing_nullable=False)
    op.execute(f"ALTER TABLE states RENAME CONSTRAINT fk_states_{old}_categories TO fk_states_{new}_categories")
    op.execute(f"ALTER INDEX idx_states_pet_id_{old}_time RENAME TO idx_states_pet_id_{new}_time")


def upgrade() -> None:
    _rename("cat_id", "category_id")


def downgrade() -> None:
    _rename("category_id", "cat_id")
