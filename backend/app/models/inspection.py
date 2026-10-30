"""Inspection Session SQLAlchemy Model.

Represents a single pipeline crawler inspection session, tracking pipe parameters,
lifecycle state transitions, archival status, and audit timestamps.
"""

from datetime import datetime
import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Float, Integer, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UtcDateTime

if TYPE_CHECKING:
    from app.models.defect import Defect


class InspectionStatus(str, enum.Enum):
    """Controlled lifecycle statuses for pipeline inspection sessions."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Inspection(Base, TimestampMixin):
    """SQLAlchemy model for pipeline inspection sessions."""

    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inspection_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Public unique inspection identifier (e.g. INSP-20261030-ABC123)",
    )
    pipe_identifier: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
        comment="Target conduit tag (e.g. PVC-MAIN-001)",
    )
    pipe_material: Mapped[str] = mapped_column(
        String(64),
        default="PVC",
        nullable=False,
        comment="Conduit composition: PVC, HDPE, Concrete",
    )
    pipe_diameter_mm: Mapped[int] = mapped_column(
        Integer,
        default=200,
        nullable=False,
        comment="Conduit inner diameter in millimeters (150mm to 300mm)",
    )
    operator_id: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
        comment="Identifier of operator or technician running the session",
    )
    status: Mapped[InspectionStatus] = mapped_column(
        Enum(
            InspectionStatus,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
            length=32,
        ),
        default=InspectionStatus.CREATED,
        nullable=False,
        index=True,
        comment="Current lifecycle status of inspection session",
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        UtcDateTime,
        nullable=True,
        comment="UTC timestamp when crawler began locomotion or recording",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        UtcDateTime,
        nullable=True,
        comment="UTC timestamp when inspection formally concluded",
    )
    total_distance_meters: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        default=None,
        comment="Final validated odometry penetration distance; nullable until computed from encoder data",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Field notes or operator remarks",
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Archival flag preserving inspection records for historical compliance without destroying defect evidence",
    )

    # Relationship to associated defects (audit-preserving: no cascade deletion)
    defects: Mapped[List["Defect"]] = relationship(
        "Defect",
        back_populates="inspection",
        order_by="Defect.id",
        lazy="selectin",
    )

    @property
    def defect_count(self) -> int:
        """Count of active non-deleted defects associated with this inspection."""
        return len([d for d in self.defects if not getattr(d, "is_deleted", False)])

    def __repr__(self) -> str:
        return f"<Inspection(id={self.id}, inspection_id='{self.inspection_id}', status='{self.status}', archived={self.is_archived})>"
