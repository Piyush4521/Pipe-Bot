"""Defect Domain Service.

Coordinates business rules, AI detection validation, operator review workflows,
and persistence for pipeline anomaly detections.
"""

from datetime import datetime, timezone
import secrets
from typing import List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ResourceNotFoundError
from app.models.defect import Defect, DefectClass, DefectReviewStatus
from app.repositories.defect_repository import DefectRepository
from app.repositories.inspection_repository import InspectionRepository
from app.schemas.defect import DefectCreate, DefectReviewUpdate


class DefectService:
    """Service orchestrating defect detection business logic and review workflows."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DefectRepository(db)
        self.inspection_repo = InspectionRepository(db)

    def _generate_defect_id(self) -> str:
        """Generate a random human-readable unique defect identifier."""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        random_suffix = secrets.token_hex(3).upper()
        return f"DEF-{date_str}-{random_suffix}"

    def create_defect(self, payload: DefectCreate) -> Defect:
        """Create a new defect detection record linked to an existing inspection."""
        inspection = self.inspection_repo.get_by_any_id(payload.inspection_id)
        if not inspection:
            raise ResourceNotFoundError("Inspection", payload.inspection_id)

        defect_id = payload.defect_id
        if not defect_id:
            defect_id = self._generate_defect_id()
            while self.repo.exists_by_defect_id(defect_id):
                defect_id = self._generate_defect_id()
        else:
            if self.repo.exists_by_defect_id(defect_id):
                raise ConflictError(
                    f"A defect with identifier '{defect_id}' already exists."
                )

        bounding_box_dict = (
            payload.bounding_box.model_dump() if payload.bounding_box else None
        )

        defect = Defect(
            defect_id=defect_id,
            inspection_id=inspection.id,
            frame_id=payload.frame_id,
            defect_class=payload.defect_class,
            confidence=payload.confidence,
            bounding_box=bounding_box_dict,
            capture_timestamp=payload.capture_timestamp,
            inference_timestamp=payload.inference_timestamp,
            estimated_distance_meters=payload.estimated_distance_meters,
            review_status=DefectReviewStatus.PENDING,
            snapshot_path=payload.snapshot_path,
            notes=payload.notes,
        )

        created = self.repo.create(defect)
        self.db.commit()
        return created

    def get_defect(self, identifier: Union[int, str]) -> Defect:
        """Retrieve a defect or raise ResourceNotFoundError if not found."""
        defect = self.repo.get_by_any_id(identifier)
        if not defect:
            raise ResourceNotFoundError("Defect", identifier)
        return defect

    def list_defects(
        self,
        limit: int = 50,
        offset: int = 0,
        inspection_id: Optional[Union[int, str]] = None,
        defect_class: Optional[DefectClass] = None,
        review_status: Optional[DefectReviewStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Defect], int]:
        """List paginated defects with multi-criteria filtering."""
        resolved_inspection_id: Optional[int] = None
        if inspection_id is not None:
            inspection = self.inspection_repo.get_by_any_id(inspection_id)
            if not inspection:
                raise ResourceNotFoundError("Inspection", inspection_id)
            resolved_inspection_id = inspection.id

        return self.repo.list_defects(
            limit=limit,
            offset=offset,
            inspection_id=resolved_inspection_id,
            defect_class=defect_class,
            review_status=review_status,
            search=search,
        )

    def update_review_status(
        self, identifier: Union[int, str], payload: DefectReviewUpdate
    ) -> Defect:
        """Update operator verification status on an existing defect."""
        defect = self.get_defect(identifier)

        defect.review_status = payload.status
        if payload.notes:
            review_note = f"Review note ({payload.status.value}): {payload.notes}"
            defect.notes = (
                f"{defect.notes}\n{review_note}".strip()
                if defect.notes
                else review_note
            )

        updated = self.repo.update(defect)
        self.db.commit()
        return updated

    def soft_delete_defect(self, identifier: Union[int, str]) -> Defect:
        """Soft-delete a defect record to preserve regulatory compliance and audit history."""
        defect = self.get_defect(identifier)
        deleted = self.repo.soft_delete(defect)
        self.db.commit()
        return deleted

