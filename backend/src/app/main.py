from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.bootstrap import build_container
from app.infra.config import get_media_dir, settings
from app.infra.database.mappings import start_mappers
from app.infra.logger import Logger
from app.presentation.http.api import ops_router, v1_router
from app.presentation.http.api.v1.exceptions.handlers import register_exception_handlers
from app.presentation.http.middleware.observability import ObservabilityMiddleware
from app.presentation.http.middleware.trace_id import TraceIdMiddleware

logger = Logger()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: RUF029
    get_media_dir().mkdir(parents=True, exist_ok=True)
    logger.get_logger().info("PetCare API started")
    start_mappers()
    container = app.state.dishka_container
    try:
        yield
    finally:
        await container.close()
    logger.get_logger().info("PetCare API stopped")


app = FastAPI(title=settings.app.name, version="1.0.0", lifespan=lifespan)
setup_dishka(build_container(), app)
register_exception_handlers(app)

_DEFAULT_CORS_ORIGINS = "http://localhost,http://localhost:8080"
origins = [
    origin.strip()
    for origin in settings.get("APP_CORS_ALLOWED_ORIGINS", _DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Last added runs first: the trace id is set before the access log and metrics see the request.
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(TraceIdMiddleware)

app.include_router(ops_router)
app.include_router(v1_router, prefix="/api")
app.mount("/media", StaticFiles(directory=get_media_dir(), check_dir=False), name="media")
