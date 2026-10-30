"""Inspection Compliance and Engineering Report SQLAlchemy Model.

Tracks generated pipeline inspection summary reports and compliance certificates.
Report files are stored on disk, with metadata and SHA-256 checksums in the database.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.inspection import Inspection


class InspectionReport(Base):
    """Persisted registry of compiled compliance certificates and exported analysis documents."""

    __tablename__ = "inspection_reports"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    report_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Public unique report identifier (e.g. REP-20261030-001)",
    )
    inspection_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("inspections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent inspection session",
    )
    report_type: Mapped[str] = mapped_column(
        String(32),
        default="FULL_COMPLIANCE",
        nullable=False,
        comment="Report classification: EXECUTIVE_SUMMARY, FULL_COMPLIANCE, MAINTENANCE_WORKORDER",
    )
    report_format: Mapped[str] = mapped_column(
        String(16),
        default="PDF",
        nullable=False,
        comment="Document format: PDF, JSON, CSV",
    )
    file_path: Mapped[str] = mapped_column(
        String(512),
        unique=True,
        nullable=False,
        comment="Relative POSIX path to generated report document on disk",
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="On-disk report file size in bytes",
    )
    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Cryptographic SHA-256 hash of generated report file",
    )
    overall_rating: Mapped[str] = mapped_column(
        String(8),
        default="B",
        nullable=False,
        comment="Pipeline structural condition grade: A, B, C, D, FAIL",
    )
    generated_by: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Operator badge or user identifier who generated the report",
    )
    generated_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="UTC timestamp when report compilation finished",
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="reports",
    )

    def __repr__(self) -> str:
        return f"<InspectionReport(id={self.id}, report_id='{self.report_id}', type='{self.report_type}', rating='{self.overall_rating}')>"

