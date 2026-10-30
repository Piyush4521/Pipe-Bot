"""SQLAlchemy Domain Models Package.

Registers and exports all database entities for Alembic discovery and metadata management.
"""

from app.db.base import Base, BigIntId, UtcDateTime
from app.models.inspection import Inspection, InspectionStatus
from app.models.defect import (
    PIPE_DEFECT_CLASSES,
    PIPE_DEFECT_CLASS_IDS,
    PIPE_DEFECT_NAME_TO_ID,
    Defect,
    DefectClass,
    DefectReviewStatus,
)
from app.models.inspection_event import InspectionEvent
from app.models.inspection_summary import InspectionSummary
from app.models.device import Device, DeviceSession, DeviceHeartbeat, VehicleStatusEvent
from app.models.telemetry import EncoderSample, IMUSample
from app.models.media import CameraFrame, EvidenceMedia
from app.models.ai_model import AIModelVersion
from app.models.localization import LocalizationRecord
from app.models.report import InspectionReport
from app.models.audit import AuditEvent

__all__ = [
    "Base",
    "BigIntId",
    "UtcDateTime",
    "Inspection",
    "InspectionStatus",
    "Defect",
    "DefectClass",
    "DefectReviewStatus",
    "PIPE_DEFECT_CLASSES",
    "PIPE_DEFECT_CLASS_IDS",
    "PIPE_DEFECT_NAME_TO_ID",
    "InspectionEvent",
    "InspectionSummary",
    "Device",
    "DeviceSession",
    "DeviceHeartbeat",
    "VehicleStatusEvent",
    "EncoderSample",
    "IMUSample",
    "CameraFrame",
    "EvidenceMedia",
    "AIModelVersion",
    "LocalizationRecord",
    "InspectionReport",
    "AuditEvent",
]
