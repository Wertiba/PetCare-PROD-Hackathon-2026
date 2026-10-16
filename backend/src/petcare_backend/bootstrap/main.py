# Copyright 2026 sazsu

import uvicorn
from fastapi import FastAPI

from petcare_backend.presentation.http.v1 import router


def create_app() -> FastAPI:
    app = FastAPI(
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.include_router(router, prefix="/api")
    return app


def main() -> None:
    uvicorn.run("petcare_backend.bootstrap.main:create_app", factory=True)
