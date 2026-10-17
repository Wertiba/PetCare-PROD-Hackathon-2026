"""Store all instants as fractional Unix seconds.

Revision ID: 0004_epoch_timestamps
Revises: 0003_care_tracking
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0004_epoch_timestamps"
down_revision = "0003_care_tracking"
branch_labels = None
depends_on = None

_COLUMNS = {
    "users": ("created_at", "updated_at"),
    "refresh_tokens": ("expires_at", "created_at"),
    "pets": ("created_at", "updated_at"),
    "categories": ("created_at",),
    "states": ("time", "created_at"),
    "events": ("schedule", "done_at", "created_at", "updated_at"),
    "notifications": ("time", "created_at"),
}


def upgrade() -> None:
    for table, columns in _COLUMNS.items():
        for column in columns:
            op.alter_column(
                table,
                column,
                type_=sa.Double(),
                postgresql_using=f'EXTRACT(EPOCH FROM "{column}")',
            )
    op.alter_column(
        "pets",
        "birth_date",
        type_=sa.Double(),
        postgresql_using="EXTRACT(EPOCH FROM (\"birth_date\"::timestamp AT TIME ZONE 'UTC'))",
    )


def downgrade() -> None:
    op.alter_column(
        "pets",
        "birth_date",
        type_=sa.Date(),
        postgresql_using="(to_timestamp(\"birth_date\") AT TIME ZONE 'UTC')::date",
    )
    for table, columns in _COLUMNS.items():
        for column in columns:
            op.alter_column(
                table,
                column,
                type_=postgresql.TIMESTAMP(timezone=True, precision=6),
                postgresql_using=f'to_timestamp("{column}")',
            )
