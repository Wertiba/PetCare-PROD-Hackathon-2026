"""Replace the email identifier with a login, preserving existing accounts.

Revision ID: 0005_user_login
Revises: 0004_epoch_timestamps
"""

import sqlalchemy as sa

from alembic import op

revision = "0005_user_login"
down_revision = "0004_epoch_timestamps"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "email", new_column_name="login", existing_type=sa.String(255), existing_nullable=False)
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.create_unique_constraint("uq_users_login", "users", ["login"])


def downgrade() -> None:
    op.alter_column("users", "login", new_column_name="email", existing_type=sa.String(255), existing_nullable=False)
    op.drop_constraint("uq_users_login", "users", type_="unique")
    op.create_unique_constraint("uq_users_email", "users", ["email"])
