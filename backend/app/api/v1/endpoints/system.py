"""System and Subsystem Status API Endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.health import SystemStatusResponse
from app.services.health_service import HealthService

router = APIRouter(prefix="/system", tags=["System Status"])


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Subsystem Link Status Matrix",
    description=(
        "Returns verified subsystem connection states matching the PipeBot frontend contract. "
        "Hardware and AI components report authentic disconnected states until integrated."
    ),
)
def get_system_status(db: Session = Depends(get_db)) -> SystemStatusResponse:
    """Return explicit subsystem connection states."""
    return HealthService.get_system_status(db)

