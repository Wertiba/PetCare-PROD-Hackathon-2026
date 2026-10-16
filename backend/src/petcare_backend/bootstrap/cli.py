# Copyright 2026 sazsu

import os
from pathlib import Path

import click
from alembic.config import Config as AlembicConfig

from petcare_backend.presentation.cli.migrations import (
    make_sql_migration,
    upgrade_sql_migration,
)
from petcare_backend.presentation.cli.server import start_uvicorn_server


@click.group()
@click.pass_context
def main(context: click.Context) -> None:
    config_path = Path(__file__).resolve().parents[1] / "infra" / "persistence" / "alembic.ini"
    config = AlembicConfig(str(config_path))
    if database_url := os.getenv("DATABASE_URL"): # TODO: change this to something else
        config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    context.obj = config


main.add_command(start_uvicorn_server, name="start-uvicorn-server")
main.add_command(make_sql_migration, name="make-sql-migration")
main.add_command(upgrade_sql_migration, name="upgrade-sql-migration")
