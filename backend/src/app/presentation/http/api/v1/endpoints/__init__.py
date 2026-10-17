from fastapi import APIRouter

from .auth import router as auth_router
from .breeds import router as breed_router
from .categories import router as category_router
from .events import router as event_router
from .notifications import router as notification_router
from .pets import router as pet_router
from .states import router as state_router
from .users import router as user_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(breed_router)
router.include_router(pet_router)
router.include_router(category_router)
router.include_router(state_router)
router.include_router(event_router)
router.include_router(notification_router)
