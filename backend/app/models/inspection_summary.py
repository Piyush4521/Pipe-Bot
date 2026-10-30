"""Inspection Summary Snapshot SQLAlchemy Model.

Stores denormalized aggregate metrics compiled upon inspection completion
to optimize dashboard loading without expensive runtime joins.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.inspection import Inspection


class InspectionSummary(Base):
    """SQLAlchemy model for pre-aggregated inspection summary snapshots."""

    __tablename__ = "inspection_summaries"

    inspection_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("inspections.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Primary key and foreign key referencing parent inspection session",
    )
    total_defects_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total verified defect count",
    )
    deformation_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Count of Deformation anomalies",
    )
    misalignment_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Count of Misalignment anomalies",
    )
    obstacle_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Count of Obstacle anomalies",
    )
    rupture_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Count of Rupture anomalies",
    )
    overall_pipe_grade: Mapped[str] = mapped_column(
        String(16),
        default="PENDING",
        nullable=False,
        comment="Pipe compliance grade: A, B, C, D, FAIL, PENDING",
    )
    total_runtime_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Elapsed active inspection duration in seconds",
    )
    compiled_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="UTC timestamp when summary snapshot was computed",
    )

    # 1-to-1 relationship with parent inspection
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="summary",
    )

    def __repr__(self) -> str:
        return f"<InspectionSummary(inspection_id={self.inspection_id}, defects={self.total_defects_count}, grade='{self.overall_pipe_grade}')>"

