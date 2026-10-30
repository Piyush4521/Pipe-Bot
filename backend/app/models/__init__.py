"""SQLAlchemy Domain Models Package.

Registers and exports all database entities for Alembic discovery and metadata management.
"""

from app.db.base import Base
from app.models.inspection import Inspection, InspectionStatus
from app.models.defect import (
    PIPE_DEFECT_CLASSES,
    PIPE_DEFECT_CLASS_IDS,
    PIPE_DEFECT_NAME_TO_ID,
    Defect,
    DefectClass,
    DefectReviewStatus,
)

__all__ = [
    "Base",
    "Inspection",
    "InspectionStatus",
    "Defect",
    "DefectClass",
    "DefectReviewStatus",
    "PIPE_DEFECT_CLASSES",
    "PIPE_DEFECT_CLASS_IDS",
    "PIPE_DEFECT_NAME_TO_ID",
]
