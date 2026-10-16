# Copyright 2026 sazsu

from fastapi import APIRouter

from petcare_backend.presentation.http.v1.ping import router as ping_router

router = APIRouter(prefix="/v1")
router.include_router(ping_router)
