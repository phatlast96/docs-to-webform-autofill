from fastapi import APIRouter

from routes.autofill import router as autofill_router
from routes.health import router as health_router

router = APIRouter()
router.include_router(health_router)
router.include_router(autofill_router)
