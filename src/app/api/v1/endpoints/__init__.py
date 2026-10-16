from fastapi import APIRouter

from .auth import router as auth_router
from .breeds import router as breed_router
from .pets import router as pet_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(breed_router)
router.include_router(pet_router)
