"""Camera Frame Metadata and Evidence Media SQLAlchemy Models.

Manages optical frame capture metadata and defect crop evidence stored on disk.
Raw video frames are never stored as database BLOBs.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.defect import Defect
    from app.models.inspection import Inspection


class CameraFrame(Base):
    """Metadata record for individual optical capture frames received from camera module."""

    __tablename__ = "camera_frames"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    frame_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Public unique frame UUID string matching frontend contract",
    )
    inspection_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("inspections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing active inspection session",
    )
    camera_id: Mapped[str] = mapped_column(
        String(64),
        default="esp32-cam-front",
        nullable=False,
        comment="Hardware camera identifier",
    )
    frame_sequence: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        default=0,
        nullable=False,
        comment="Sequence counter from camera firmware stream",
    )
    frame_width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Horizontal image dimension in pixels",
    )
    frame_height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Vertical image dimension in pixels",
    )
    encoding: Mapped[str] = mapped_column(
        String(16),
        default="jpeg",
        nullable=False,
        comment="Compression format: jpeg, png",
    )
    frame_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Raw frame payload size in bytes",
    )
    capture_timestamp: Mapped[Optional[datetime]] = mapped_column(
        UtcDateTime,
        nullable=True,
        index=True,
        comment="Optical exposure timestamp if provided by camera clock",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Server UTC arrival timestamp",
    )
    processing_status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
        comment="Inference queue status: pending, inferred, dropped, error",
    )
    has_defect: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether AI inference identified an anomaly in this frame",
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="camera_frames",
    )

    def __repr__(self) -> str:
        return f"<CameraFrame(id={self.id}, frame_id='{self.frame_id}', res={self.frame_width}x{self.frame_height})>"


class EvidenceMedia(Base):
    """File registry tracking localized defect crop images stored on filesystem."""

    __tablename__ = "evidence_media"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    media_uuid: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Public unique media UUID string",
    )
    defect_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("defects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent defect record",
    )
    file_path: Mapped[str] = mapped_column(
        String(512),
        unique=True,
        nullable=False,
        comment="Relative POSIX path from media root (e.g. crops/insp_1/def_42.jpg)",
    )
    mime_type: Mapped[str] = mapped_column(
        String(64),
        default="image/jpeg",
        nullable=False,
        comment="MIME type string",
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="On-disk file size in bytes",
    )
    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Cryptographic SHA-256 hash of evidence image file",
    )
    storage_backend: Mapped[str] = mapped_column(
        String(32),
        default="LOCAL_FS",
        nullable=False,
        comment="Storage backend: LOCAL_FS, S3, MINIO",
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
        back_populates="evidence_media",
    )

    def __repr__(self) -> str:
        return f"<EvidenceMedia(id={self.id}, path='{self.file_path}', size={self.file_size_bytes})>"

