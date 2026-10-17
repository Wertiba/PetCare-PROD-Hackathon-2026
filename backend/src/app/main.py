from contextlib import asynccontextmanager

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bootstrap import build_container
from app.infra.config import AppConfig, HttpConfig
from app.infra.database.mappings import start_mappers
from app.infra.logger import Logger
from app.presentation.http.api import ops_router, v1_router
from app.presentation.http.api.v1.exceptions.handlers import register_exception_handlers
from app.presentation.http.middleware.observability import ObservabilityMiddleware
from app.presentation.http.middleware.trace_id import TraceIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: RUF029
    container = app.state.dishka_container
    logger = await container.get(Logger)
    try:
        start_mappers()
        logger.get_logger().info("PetCare API started")
        yield
    finally:
        await container.close()
        logger.get_logger().info("PetCare API stopped")


def create_app(container: AsyncContainer | None = None) -> FastAPI:
    if container is None:
        container = build_container()
    app_config = container.get_sync(AppConfig)
    http_config = container.get_sync(HttpConfig)
    container.get_sync(Logger)

    app = FastAPI(title=app_config.name, version="1.0.0", lifespan=lifespan)
    setup_dishka(container, app)
    register_exception_handlers(app)

    origins = [origin.strip() for origin in http_config.cors_allowed_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(TraceIdMiddleware)

    app.include_router(ops_router)
    app.include_router(v1_router, prefix="/api")
    return app


app = create_app()
