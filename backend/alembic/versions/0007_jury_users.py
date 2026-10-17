"""demo accounts for the jury: жюри1..жюри10 with the password from the frontend quick-login buttons

Revision ID: 0007_jury_users
Revises: 0006_animals_notes_food
Create Date: 2026-10-17

"""

import uuid
from time import time

import sqlalchemy as sa
from passlib.context import CryptContext

from alembic import op

revision = "0007_jury_users"
down_revision = "0006_animals_notes_food"
branch_labels = None
depends_on = None

# Must match frontend/src/shared/config/demo-users.ts.
_PASSWORD = "qwerty12345"
_COUNT = 10


def _user_id(number: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-4000-b000-{number:012d}")


def upgrade() -> None:
    # Same scheme as settings.token.SCHEMA; each account gets its own salt.
    context = CryptContext(schemes=["argon2"])
    now = time()
    insert = sa.text(
        "INSERT INTO users (id, login, password, full_name, role, is_active, created_by, created_at, updated_at) "
        "VALUES (:id, :login, :password, :full_name, 'USER', true, :id, :now, :now) "
        "ON CONFLICT (login) DO NOTHING"
    )
    for number in range(1, _COUNT + 1):
        op.execute(
            insert.bindparams(
                id=_user_id(number),
                login=f"жюри{number}",
                password=context.hash(_PASSWORD),
                full_name=f"Жюри {number}",
                now=now,
            )
        )


def downgrade() -> None:
    ids = ", ".join(f"'{_user_id(number)}'" for number in range(1, _COUNT + 1))
    op.execute(f"DELETE FROM refresh_tokens WHERE user_id IN ({ids})")
    op.execute(f"DELETE FROM users WHERE id IN ({ids})")
