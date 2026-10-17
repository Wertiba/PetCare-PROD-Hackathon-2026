"""pet photo key, generated avatar and avatar source

Revision ID: 0008_pet_avatars
Revises: 0007_jury_users
Create Date: 2026-10-17

"""

import sqlalchemy as sa

from alembic import op

revision = "0008_pet_avatars"
down_revision = "0007_jury_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "pets",
        "photo_url",
        new_column_name="photo_key",
        existing_type=sa.String(length=255),
        existing_nullable=True,
    )
    # Legacy local files were stored as /media/pets/<name> and served from that path.
    op.execute(
        "UPDATE pets SET photo_key = regexp_replace(photo_key, '^/media/', '') WHERE photo_key LIKE '/media/pets/%'"
    )
    op.add_column("pets", sa.Column("generated_avatar_key", sa.String(length=255), nullable=True))
    op.add_column(
        "pets",
        sa.Column("avatar_source", sa.String(length=20), nullable=False, server_default=sa.text("'photo'")),
    )
    op.create_check_constraint("ck_pets_avatar_source", "pets", "avatar_source IN ('photo', 'generated')")


def downgrade() -> None:
    op.drop_constraint("ck_pets_avatar_source", "pets", type_="check")
    op.drop_column("pets", "avatar_source")
    op.drop_column("pets", "generated_avatar_key")
    # The S3 gateway also stored raw object keys in photo_url before this migration.
    op.alter_column(
        "pets",
        "photo_key",
        new_column_name="photo_url",
        existing_type=sa.String(length=255),
        existing_nullable=True,
    )
