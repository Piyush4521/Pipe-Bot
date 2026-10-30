"""Health, Readiness, and Database Verification API Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.health import (
    DatabaseHealthResponse,
    HealthResponse,
    ReadinessResponse,
)
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Application Health",
    description="Returns service identity, version, operational status, and server timestamp.",
)
def get_health() -> HealthResponse:
    """Return application identity and general operational health."""
    return HealthService.get_health()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
    description="Evaluates whether the backend is ready to accept requests (verifies database accessibility).",
)
def get_readiness(db: Session = Depends(get_db)) -> ReadinessResponse:
    """Check backend readiness to accept operator requests."""
    readiness, is_ready = HealthService.get_readiness(db)
    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=readiness.model_dump(),
        )
    return readiness


@router.get(
    "/database",
    response_model=DatabaseHealthResponse,
    summary="Database Connectivity Verification",
    description="Executes a test query against the database and returns latency metrics.",
)
def get_database_health(db: Session = Depends(get_db)) -> DatabaseHealthResponse:
    """Check database roundtrip response time and connection health."""
    db_health = HealthService.get_database_health(db)
    if db_health.status != "connected":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=db_health.model_dump(),
        )
    return db_health

