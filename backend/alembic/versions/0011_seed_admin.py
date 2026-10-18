"""admin account from ADMIN_LOGIN/ADMIN_PASSWORD; seeded animals and breeds now belong to it

Revision ID: 0011_seed_admin
Revises: 0010_notification_delivery
Create Date: 2026-10-18

"""

import os
import uuid
from time import time

import sqlalchemy as sa
from passlib.context import CryptContext

from alembic import op
from app.infra.config import SeedAdminConfig

revision = "0011_seed_admin"
down_revision = "0010_notification_delivery"
branch_labels = None
depends_on = None

_ADMIN_ID = uuid.UUID("00000000-0000-4000-c000-000000000001")
_SEEDED = ("animals", "breeds")


def upgrade() -> None:
    config = SeedAdminConfig(**os.environ)
    # Same scheme as settings.token.SCHEMA.
    password = CryptContext(schemes=["argon2"]).hash(config.password)
    op.execute(
        sa.text(
            "INSERT INTO users (id, login, password, full_name, role, is_active, created_by, created_at, updated_at) "
            "VALUES (:id, :login, :password, :full_name, 'ADMIN', true, :id, :now, :now) "
            "ON CONFLICT (login) DO NOTHING"
        ).bindparams(id=_ADMIN_ID, login=config.login, password=password, full_name=config.full_name, now=time())
    )
    # A subquery instead of _ADMIN_ID: the login may already have belonged to an existing account.
    for table in _SEEDED:
        op.execute(
            sa.text(
                f"UPDATE {table} SET created_by = (SELECT id FROM users WHERE login = :login) "  # noqa: S608
                "WHERE created_by IS NULL"
            ).bindparams(login=config.login)
        )


def downgrade() -> None:
    for table in _SEEDED:
        op.execute(f"UPDATE {table} SET created_by = NULL WHERE created_by = '{_ADMIN_ID}'")  # noqa: S608
    op.execute(f"DELETE FROM refresh_tokens WHERE user_id = '{_ADMIN_ID}'")
    op.execute(f"DELETE FROM users WHERE id = '{_ADMIN_ID}'")
