"""Defect Detection API Endpoints.

Provides RESTful operations for recording defect anomalies, multi-criteria filtering,
and operator review verification.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.defect import DefectClass, DefectReviewStatus
from app.schemas.defect import (
    DefectCreate,
    DefectListResponse,
    DefectResponse,
    DefectReviewUpdate,
)
from app.services.defect_service import DefectService

router = APIRouter(prefix="/defects", tags=["Defects"])


@router.post(
    "",
    response_model=DefectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record New Defect Detection",
    description="Registers an AI or operator anomaly detection linked to an existing inspection session.",
)
def create_defect(
    payload: DefectCreate,
    db: Session = Depends(get_db),
) -> DefectResponse:
    """Record a new defect detection."""
    service = DefectService(db)
    defect = service.create_defect(payload)
    return DefectResponse.model_validate(defect)


@router.get(
    "",
    response_model=DefectListResponse,
    summary="List Defect Detections",
    description="Returns a paginated list of defect detections with multi-criteria filtering.",
)
def list_defects(
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Items to skip"),
    inspection_id: Optional[str] = Query(default=None, description="Filter by inspection ID"),
    defect_class: Optional[DefectClass] = Query(default=None, alias="class", description="Filter by class"),
    review_status: Optional[DefectReviewStatus] = Query(default=None, alias="status", description="Filter by review status"),
    search: Optional[str] = Query(default=None, alias="q", description="Text search on frame, defect ID, notes"),
    db: Session = Depends(get_db),
) -> DefectListResponse:
    """Retrieve paginated defect detections."""
    service = DefectService(db)
    items, total = service.list_defects(
        limit=limit,
        offset=offset,
        inspection_id=inspection_id,
        defect_class=defect_class,
        review_status=review_status,
        search=search,
    )
    return DefectListResponse(
        items=[DefectResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{defect_id}",
    response_model=DefectResponse,
    summary="Retrieve Defect Detection",
    description="Fetches a single defect detection record by internal ID or public defect identifier.",
)
def get_defect(
    defect_id: str,
    db: Session = Depends(get_db),
) -> DefectResponse:
    """Retrieve a defect detection."""
    service = DefectService(db)
    defect = service.get_defect(defect_id)
    return DefectResponse.model_validate(defect)


@router.get(
    "/inspection/{inspection_id}",
    response_model=DefectListResponse,
    summary="List Defects by Inspection Session",
    description="Returns all defects recorded for a specified inspection session (frontend compatibility route).",
)
def list_defects_by_inspection(
    inspection_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> DefectListResponse:
    """Retrieve all defects linked to an inspection session."""
    service = DefectService(db)
    items, total = service.list_defects(limit=limit, offset=offset, inspection_id=inspection_id)
    return DefectListResponse(
        items=[DefectResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{defect_id}/review",
    response_model=DefectResponse,
    summary="Update Defect Review Status",
    description="Updates operator verification status (pending, confirmed, rejected) and optional notes.",
)
def update_defect_review(
    defect_id: str,
    payload: DefectReviewUpdate,
    db: Session = Depends(get_db),
) -> DefectResponse:
    """Update defect review verification status."""
    service = DefectService(db)
    defect = service.update_review_status(defect_id, payload)
    return DefectResponse.model_validate(defect)


@router.delete(
    "/{defect_id}",
    response_model=DefectResponse,
    summary="Soft-Delete Defect Detection",
    description="Soft-deletes a defect detection record to maintain regulatory compliance audit history.",
)
def delete_defect(
    defect_id: str,
    db: Session = Depends(get_db),
) -> DefectResponse:
    """Soft-delete a defect detection."""
    service = DefectService(db)
    defect = service.soft_delete_defect(defect_id)
    return DefectResponse.model_validate(defect)

