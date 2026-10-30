"""API v1 Central Router.

Aggregates all version 1 endpoints into a unified modular router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.camera import router as camera_router
from app.api.v1.endpoints.defects import router as defects_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.inspections import router as inspections_router
from app.api.v1.endpoints.media import router as media_router
from app.api.v1.endpoints.system import router as system_router
from app.api.v1.endpoints.telemetry import router as telemetry_router
from app.api.v1.endpoints.vision import router as vision_router
from app.api.v1.endpoints.websocket import router as websocket_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(system_router)
api_v1_router.include_router(inspections_router)
api_v1_router.include_router(defects_router)
api_v1_router.include_router(telemetry_router)
api_v1_router.include_router(websocket_router)
api_v1_router.include_router(camera_router)
api_v1_router.include_router(vision_router)
api_v1_router.include_router(media_router)
