"""SQLAlchemy Repository for AI Model Metadata and Provenance.

Provides persistence and query access for neural network versions,
inference thresholds, class mappings, and weights artifacts.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.ai_model import AIModelVersion


class AIModelRepository:
    """Repository managing AI model versions, active configurations, and provenance."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def register_model_version(
        self,
        model_name: str,
        model_version: str,
        artifact_path: str,
        artifact_checksum_sha256: str,
        class_mapping: Dict[str, Any],
        input_dimensions: str = "640x640",
        confidence_threshold: float = 0.25,
        inference_backend: str = "ULTRALYTICS",
        training_dataset_id: Optional[str] = None,
        is_active: bool = True,
    ) -> AIModelVersion:
        """Register a new AI model version and set active status."""
        if is_active:
            # Set other models of same name to inactive
            self.db.execute(
                update(AIModelVersion)
                .where(AIModelVersion.model_name == model_name)
                .values(is_active=False)
            )

        model = AIModelVersion(
            model_name=model_name,
            model_version=model_version,
            artifact_path=artifact_path,
            artifact_checksum_sha256=artifact_checksum_sha256,
            class_mapping=class_mapping,
            input_dimensions=input_dimensions,
            confidence_threshold=confidence_threshold,
            inference_backend=inference_backend,
            training_dataset_id=training_dataset_id,
            is_active=is_active,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model

    def get_by_version(self, model_version: str) -> Optional[AIModelVersion]:
        """Fetch model configuration by semantic version string."""
        stmt = select(AIModelVersion).where(AIModelVersion.model_version == model_version)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, model_id: int) -> Optional[AIModelVersion]:
        """Fetch model by surrogate key."""
        stmt = select(AIModelVersion).where(AIModelVersion.id == model_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active_model(self, model_name: Optional[str] = None) -> Optional[AIModelVersion]:
        """Fetch current active AI model."""
        stmt = select(AIModelVersion).where(AIModelVersion.is_active == True)  # noqa: E712
        if model_name:
            stmt = stmt.where(AIModelVersion.model_name == model_name)
        stmt = stmt.order_by(AIModelVersion.created_at.desc())
        return self.db.execute(stmt).scalars().first()

    def set_active_model(self, model_version: str) -> Optional[AIModelVersion]:
        """Activate specified model version and deactivate others with matching name."""
        target = self.get_by_version(model_version)
        if not target:
            return None

        self.db.execute(
            update(AIModelVersion)
            .where(AIModelVersion.model_name == target.model_name)
            .values(is_active=False)
        )
        target.is_active = True
        self.db.flush()
        self.db.refresh(target)
        return target

    def list_models(self) -> List[AIModelVersion]:
        """List all registered AI model versions."""
        stmt = select(AIModelVersion).order_by(AIModelVersion.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

