"""Defect Localization Association SQLAlchemy Model.

Correlates optical capture timestamps with nearest wheel encoder pulses,
tracking clock synchronization status and temporal delta explicitly.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.defect import Defect


class LocalizationRecord(Base):
    """Spatial correlation record pairing optical frame capture with encoder odometry."""

    __tablename__ = "localization_records"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    defect_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("defects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent defect record",
    )
    frame_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="Associated camera optical frame identifier",
    )
    frame_capture_timestamp: Mapped[datetime] = mapped_column(
        UtcDateTime,
        nullable=False,
        comment="Optical frame exposure timestamp from camera clock",
    )
    encoder_sample_timestamp: Mapped[datetime] = mapped_column(
        UtcDateTime,
        nullable=False,
        comment="Microcontroller timestamp of nearest correlated encoder sample",
    )
    temporal_delta_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Absolute difference between optical capture and encoder sample in milliseconds",
    )
    clock_sync_status: Mapped[str] = mapped_column(
        String(32),
        default="UNVERIFIED_SYNC",
        nullable=False,
        comment="Synchronization state: UNVERIFIED_SYNC, SYNCHRONIZED, MANUAL_OVERRIDE",
    )
    sync_notes: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        comment="Diagnostic explanation if synchronization is unverified or degraded",
    )
    left_encoder_ticks: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=True,
        comment="Cumulative ticks of left motor encoder at correlated point",
    )
    right_encoder_ticks: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=True,
        comment="Cumulative ticks of right motor encoder at correlated point",
    )
    computed_distance_meters: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Calculated pipeline penetration distance (null if sync is unverified)",
    )
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Record creation timestamp",
    )

    # Relationships
    defect: Mapped["Defect"] = relationship(
        "Defect",
        back_populates="localization_record",
    )

    def __repr__(self) -> str:
        return f"<LocalizationRecord(id={self.id}, defect_id={self.defect_id}, status='{self.clock_sync_status}')>"

