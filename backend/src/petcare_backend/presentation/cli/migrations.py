# Copyright 2026 sazsu

import click
from alembic import command
from alembic.config import Config as AlembicConfig

pass_alembic_config = click.make_pass_decorator(AlembicConfig)


@click.command()
@click.option("--message", required=True, help="Migration description.")
@click.option(
    "--autogenerate/--no-autogenerate",
    default=True,
    show_default=True,
    help="Compare configured SQLAlchemy metadata with the database.",
)
@pass_alembic_config
def make_sql_migration(
    alembic_config: AlembicConfig, message: str, autogenerate: bool
) -> None:
    """Create a SQL migration."""
    command.revision(config=alembic_config, autogenerate=autogenerate, message=message)


@click.command()
@click.option("--revision", default="head", show_default=True, help="Target Alembic revision.")
@pass_alembic_config
def upgrade_sql_migration(alembic_config: AlembicConfig, revision: str) -> None:
    """Apply SQL migrations."""
    command.upgrade(config=alembic_config, revision=revision)
