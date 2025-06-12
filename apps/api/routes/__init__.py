from fastapi import APIRouter
from apps.api.routes.healthcheck import router as health_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["Health"])
