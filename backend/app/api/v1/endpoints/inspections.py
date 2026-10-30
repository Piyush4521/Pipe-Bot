"""Inspection Session API Endpoints.

Provides RESTful operations for inspection session lifecycle, status transitions,
archival preservation, and defect correlation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.inspection import InspectionStatus
from app.schemas.defect import DefectListResponse, DefectResponse
from app.schemas.inspection import (
    InspectionCreate,
    InspectionListResponse,
    InspectionResponse,
    InspectionStatusUpdate,
    InspectionUpdate,
)
from app.services.inspection_service import InspectionService

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.post(
    "",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Inspection Session",
    description="Initializes a new pipeline inspection session in CREATED status.",
)
def create_inspection(
    payload: InspectionCreate,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Create a new inspection session."""
    service = InspectionService(db)
    inspection = service.create_inspection(payload)
    return InspectionResponse.model_validate(inspection)


@router.get(
    "",
    response_model=InspectionListResponse,
    summary="List Inspection Sessions",
    description="Returns a paginated list of inspection sessions with optional lifecycle status and archival filtering.",
)
def list_inspections(
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Items to skip"),
    status: Optional[InspectionStatus] = Query(default=None, description="Filter by status"),
    include_archived: bool = Query(default=False, description="Include archived sessions in query results"),
    db: Session = Depends(get_db),
) -> InspectionListResponse:
    """Retrieve paginated inspection sessions."""
    service = InspectionService(db)
    items, total = service.list_inspections(
        limit=limit,
        offset=offset,
        status=status,
        include_archived=include_archived,
    )
    return InspectionListResponse(
        items=[InspectionResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
    summary="Retrieve Inspection Session",
    description="Fetches a single inspection session by internal ID or public inspection identifier.",
)
def get_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Retrieve an inspection session."""
    service = InspectionService(db)
    inspection = service.get_inspection(inspection_id)
    return InspectionResponse.model_validate(inspection)


@router.patch(
    "/{inspection_id}",
    response_model=InspectionResponse,
    summary="Update Inspection Metadata",
    description="Updates safe descriptive metadata for an inspection session.",
)
def update_inspection(
    inspection_id: str,
    payload: InspectionUpdate,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Update inspection metadata."""
    service = InspectionService(db)
    inspection = service.update_inspection(inspection_id, payload)
    return InspectionResponse.model_validate(inspection)


@router.post(
    "/{inspection_id}/start",
    response_model=InspectionResponse,
    summary="Start Inspection Session",
    description="Transitions an inspection from CREATED to IN_PROGRESS and records start timestamp.",
)
def start_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Start an inspection session."""
    service = InspectionService(db)
    inspection = service.start_inspection(inspection_id)
    return InspectionResponse.model_validate(inspection)


@router.post(
    "/{inspection_id}/pause",
    response_model=InspectionResponse,
    summary="Pause Inspection Session",
    description="Transitions an active inspection from IN_PROGRESS to PAUSED.",
)
def pause_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Pause an inspection session."""
    service = InspectionService(db)
    inspection = service.pause_inspection(inspection_id)
    return InspectionResponse.model_validate(inspection)


@router.post(
    "/{inspection_id}/complete",
    response_model=InspectionResponse,
    summary="Complete Inspection Session",
    description="Concludes an active inspection session and records completion timestamp.",
)
def complete_inspection(
    inspection_id: str,
    payload: Optional[InspectionStatusUpdate] = None,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Complete an inspection session."""
    service = InspectionService(db)
    inspection = service.complete_inspection(inspection_id, payload)
    return InspectionResponse.model_validate(inspection)


@router.post(
    "/{inspection_id}/cancel",
    response_model=InspectionResponse,
    summary="Cancel Inspection Session",
    description="Cancels an inspection session before completion.",
)
def cancel_inspection(
    inspection_id: str,
    payload: Optional[InspectionStatusUpdate] = None,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Cancel an inspection session."""
    service = InspectionService(db)
    notes = payload.notes if payload else None
    inspection = service.cancel_inspection(inspection_id, notes=notes)
    return InspectionResponse.model_validate(inspection)


@router.post(
    "/{inspection_id}/archive",
    response_model=InspectionResponse,
    summary="Archive Inspection Session",
    description="Safely archives an inspection session without deleting associated defect evidence.",
)
def archive_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    """Archive an inspection session."""
    service = InspectionService(db)
    inspection = service.archive_inspection(inspection_id)
    return InspectionResponse.model_validate(inspection)


@router.delete(
    "/{inspection_id}",
    summary="Reject Permanent Inspection Deletion",
    description="Permanent inspection deletion is prohibited to preserve regulatory defect evidence.",
)
def delete_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
) -> None:
    """Reject permanent deletion request."""
    service = InspectionService(db)
    service.delete_inspection(inspection_id)


@router.get(
    "/{inspection_id}/defects",
    response_model=DefectListResponse,
    summary="List Inspection Defects",
    description="Retrieves paginated defects registered under a specific inspection session.",
)
def get_inspection_defects(
    inspection_id: str,
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
) -> DefectListResponse:
    """Retrieve defects for an inspection session."""
    service = InspectionService(db)
    items, total = service.get_inspection_defects(inspection_id, limit=limit, offset=offset)
    return DefectListResponse(
        items=[DefectResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
