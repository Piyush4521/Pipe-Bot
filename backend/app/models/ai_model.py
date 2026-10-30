"""AI Model Provenance and Metadata SQLAlchemy Model.

Manages deployed computer vision model configurations and weights file checksums.
Binary weights files are stored on disk, never in database BLOB columns.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, Float, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.defect import Defect


class AIModelVersion(Base):
    """Provenance tracking for neural network models deployed for defect detection."""

    __tablename__ = "ai_model_versions"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    model_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Human-readable model architecture (e.g. yolov8n-pipebot)",
    )
    model_version: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Semantic version identifier (e.g. v1.0.0-baseline)",
    )
    artifact_path: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Relative path to model weights file on disk",
    )
    artifact_checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Cryptographic SHA-256 hash of model weights file",
    )
    training_dataset_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="Reference to training dataset version",
    )
    class_mapping: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Canonical class ID to name dictionary",
    )
    input_dimensions: Mapped[str] = mapped_column(
        String(32),
        default="640x640",
        nullable=False,
        comment="Input image resolution expected by model",
    )
    confidence_threshold: Mapped[float] = mapped_column(
        Float,
        default=0.25,
        nullable=False,
        comment="Default minimum inference confidence threshold",
    )
    inference_backend: Mapped[str] = mapped_column(
        String(32),
        default="ULTRALYTICS",
        nullable=False,
        comment="Runtime provider: ULTRALYTICS, ONNX_RUNTIME, OPENVINO",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether model is active for live camera inference",
    )
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Model registration timestamp",
    )

    # Relationships
    defects: Mapped[List["Defect"]] = relationship(
        "Defect",
        back_populates="model_version",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AIModelVersion(id={self.id}, name='{self.model_name}', version='{self.model_version}')>"

