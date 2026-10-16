# Copyright 2026 sazsu

import click
import uvicorn


@click.command()
@click.option("--host", default="127.0.0.1", envvar="HOST", show_default=True)
@click.option(
    "--port", default=8000, type=click.IntRange(1, 65535), envvar="PORT", show_default=True
)
@click.option(
    "--target",
    default="petcare_backend.bootstrap.main:create_app",
    show_default=True,
    help="asgi application import path",
)
@click.option("--factory/--no-factory", default=True, show_default=True)
@click.option("--reload", is_flag=True, help="reload when source files change")
def start_uvicorn_server(
    host: str, port: int, target: str, factory: bool, reload: bool
) -> None:
    uvicorn.run(app=target, host=host, port=port, factory=factory, reload=reload)
