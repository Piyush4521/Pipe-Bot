"""Defect Detection SQLAlchemy Model.

Represents an AI or operator detected pipeline anomaly associated with a specific
inspection session and recorded camera optical frame.
"""

from datetime import datetime
import enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UtcDateTime

if TYPE_CHECKING:
    from app.models.inspection import Inspection


PIPE_DEFECT_CLASSES = [
    "Deformation",
    "Misalignment",
    "Obstacle",
    "Rupture",
]

PIPE_DEFECT_CLASS_IDS = {
    0: "Deformation",
    1: "Misalignment",
    2: "Obstacle",
    3: "Rupture",
}

PIPE_DEFECT_NAME_TO_ID = {
    "Deformation": 0,
    "Misalignment": 1,
    "Obstacle": 2,
    "Rupture": 3,
}


class DefectClass(str, enum.Enum):
    """Canonical target PVC conduit anomaly classifications matching dataset and frontend."""

    DEFORMATION = "Deformation"
    MISALIGNMENT = "Misalignment"
    OBSTACLE = "Obstacle"
    RUPTURE = "Rupture"

    @classmethod
    def _missing_(cls, value: object):
        """Enable case-insensitive deserialization while enforcing canonical values."""
        if isinstance(value, str):
            val_lower = value.lower()
            for member in cls:
                if member.value.lower() == val_lower:
                    return member
        return None


class DefectReviewStatus(str, enum.Enum):
    """Operator review status for AI defect detections."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class Defect(Base, TimestampMixin):
    """SQLAlchemy model for pipeline defect anomaly detections."""

    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    defect_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Public unique defect identifier (e.g. DEF-20261030-XYZ123)",
    )
    inspection_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("inspections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent inspection session with restrictive deletion policy",
    )
    frame_id: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
        comment="Camera optical frame identifier associated with detection",
    )
    defect_class: Mapped[DefectClass] = mapped_column(
        Enum(
            DefectClass,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
            length=32,
        ),
        nullable=False,
        index=True,
        comment="Classified anomaly: deformation, misalignment, obstacle, rupture",
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="AI inference confidence score between 0.0 and 1.0 (statistical confidence, not severity)",
    )
    bounding_box: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Bounding box coordinates {x, y, width, height} normalized (0.0-1.0) or pixel",
    )
    capture_timestamp: Mapped[datetime] = mapped_column(
        UtcDateTime,
        nullable=False,
        comment="Recorded frame capture timestamp from camera module (not a physical shutter synchronization signal)",
    )
    inference_timestamp: Mapped[Optional[datetime]] = mapped_column(
        UtcDateTime,
        nullable=True,
        comment="UTC timestamp when YOLO neural network evaluated the frame on the server",
    )
    estimated_distance_meters: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Conduit penetration distance correlated at frame capture time; never inferred from AI timestamp",
    )
    review_status: Mapped[DefectReviewStatus] = mapped_column(
        Enum(
            DefectReviewStatus,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
            length=32,
        ),
        default=DefectReviewStatus.PENDING,
        nullable=False,
        index=True,
        comment="Operator verification status: pending, confirmed, rejected",
    )
    snapshot_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Relative file path or URI to saved JPEG frame snapshot",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Engineering comments or review remarks",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Soft-delete flag preserving regulatory compliance and audit history",
    )

    # Relationship to parent inspection
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="defects",
    )

    def __repr__(self) -> str:
        return f"<Defect(id={self.id}, defect_id='{self.defect_id}', class='{self.defect_class}', status='{self.review_status}')>"
