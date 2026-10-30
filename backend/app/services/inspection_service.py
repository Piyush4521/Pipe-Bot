"""Inspection Domain Service.

Coordinates business rules, lifecycle status transitions, transaction handling,
archival preservation, and persistence for inspection sessions.
"""

from datetime import datetime, timezone
import secrets
from typing import List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, InvalidStateTransitionError, ResourceNotFoundError
from app.models.defect import Defect
from app.models.inspection import Inspection, InspectionStatus
from app.repositories.defect_repository import DefectRepository
from app.repositories.inspection_repository import InspectionRepository
from app.schemas.inspection import InspectionCreate, InspectionStatusUpdate, InspectionUpdate


class InspectionService:
    """Service orchestrating inspection session business logic, lifecycle rules, and archival."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = InspectionRepository(db)
        self.defect_repo = DefectRepository(db)

    def _generate_inspection_id(self) -> str:
        """Generate a random human-readable unique inspection identifier."""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        random_suffix = secrets.token_hex(3).upper()
        return f"INSP-{date_str}-{random_suffix}"

    def create_inspection(self, payload: InspectionCreate) -> Inspection:
        """Create a new inspection session with initial CREATED status."""
        inspection_id = payload.inspection_id
        if not inspection_id:
            inspection_id = self._generate_inspection_id()
            while self.repo.exists_by_inspection_id(inspection_id):
                inspection_id = self._generate_inspection_id()
        else:
            if self.repo.exists_by_inspection_id(inspection_id):
                raise ConflictError(
                    f"An inspection with identifier '{inspection_id}' already exists."
                )

        inspection = Inspection(
            inspection_id=inspection_id,
            pipe_identifier=payload.pipe_identifier,
            pipe_material=payload.pipe_material,
            pipe_diameter_mm=payload.pipe_diameter_mm,
            operator_id=payload.operator_id,
            status=InspectionStatus.CREATED,
            started_at=None,
            completed_at=None,
            total_distance_meters=None,
            notes=payload.notes,
            is_archived=False,
        )

        created = self.repo.create(inspection)
        self.db.commit()
        return created

    def get_inspection(self, identifier: Union[int, str]) -> Inspection:
        """Retrieve an inspection (including archived sessions) or raise ResourceNotFoundError."""
        inspection = self.repo.get_by_any_id(identifier)
        if not inspection:
            raise ResourceNotFoundError("Inspection", identifier)
        return inspection

    def list_inspections(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[InspectionStatus] = None,
        include_archived: bool = False,
    ) -> Tuple[List[Inspection], int]:
        """List paginated inspections with optional status and archival filtering."""
        return self.repo.list_inspections(
            limit=limit,
            offset=offset,
            status=status,
            include_archived=include_archived,
        )

    def update_inspection(
        self, identifier: Union[int, str], payload: InspectionUpdate
    ) -> Inspection:
        """Update mutable descriptive metadata on an inspection."""
        inspection = self.get_inspection(identifier)

        update_dict = payload.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(inspection, key) and value is not None:
                setattr(inspection, key, value)

        updated = self.repo.update(inspection)
        self.db.commit()
        return updated

    def start_inspection(self, identifier: Union[int, str]) -> Inspection:
        """Transition an inspection from CREATED to IN_PROGRESS and record start timestamp."""
        inspection = self.get_inspection(identifier)

        if inspection.status != InspectionStatus.CREATED:
            raise InvalidStateTransitionError(
                current_status=inspection.status.value,
                target_status=InspectionStatus.IN_PROGRESS.value,
            )

        inspection.status = InspectionStatus.IN_PROGRESS
        inspection.started_at = datetime.now(timezone.utc)

        updated = self.repo.update(inspection)
        self.db.commit()
        return updated

    def pause_inspection(self, identifier: Union[int, str]) -> Inspection:
        """Transition an inspection from IN_PROGRESS to PAUSED."""
        inspection = self.get_inspection(identifier)

        if inspection.status != InspectionStatus.IN_PROGRESS:
            raise InvalidStateTransitionError(
                current_status=inspection.status.value,
                target_status=InspectionStatus.PAUSED.value,
            )

        inspection.status = InspectionStatus.PAUSED

        updated = self.repo.update(inspection)
        self.db.commit()
        return updated

    def complete_inspection(
        self,
        identifier: Union[int, str],
        update_data: Optional[InspectionStatusUpdate] = None,
    ) -> Inspection:
        """Complete an inspection session from an active state (IN_PROGRESS or PAUSED)."""
        inspection = self.get_inspection(identifier)

        valid_source_states = {InspectionStatus.IN_PROGRESS, InspectionStatus.PAUSED}
        if inspection.status not in valid_source_states:
            raise InvalidStateTransitionError(
                current_status=inspection.status.value,
                target_status=InspectionStatus.COMPLETED.value,
            )

        inspection.status = InspectionStatus.COMPLETED
        inspection.completed_at = datetime.now(timezone.utc)

        if update_data:
            if update_data.total_distance_meters is not None:
                inspection.total_distance_meters = update_data.total_distance_meters
            if update_data.notes:
                inspection.notes = (
                    f"{inspection.notes}\n{update_data.notes}".strip()
                    if inspection.notes
                    else update_data.notes
                )

        updated = self.repo.update(inspection)
        self.db.commit()
        return updated

    def cancel_inspection(
        self,
        identifier: Union[int, str],
        notes: Optional[str] = None,
    ) -> Inspection:
        """Cancel an inspection session before completion."""
        inspection = self.get_inspection(identifier)

        cancellable_states = {
            InspectionStatus.CREATED,
            InspectionStatus.IN_PROGRESS,
            InspectionStatus.PAUSED,
        }
        if inspection.status not in cancellable_states:
            raise InvalidStateTransitionError(
                current_status=inspection.status.value,
                target_status=InspectionStatus.CANCELLED.value,
            )

        inspection.status = InspectionStatus.CANCELLED
        if notes:
            inspection.notes = (
                f"{inspection.notes}\n[CANCELLED] {notes}".strip()
                if inspection.notes
                else f"[CANCELLED] {notes}"
            )

        updated = self.repo.update(inspection)
        self.db.commit()
        return updated

    def archive_inspection(self, identifier: Union[int, str]) -> Inspection:
        """Safely archive an inspection session preserving all associated defect evidence."""
        inspection = self.get_inspection(identifier)
        archived = self.repo.archive(inspection)
        self.db.commit()
        return archived

    def delete_inspection(self, identifier: Union[int, str]) -> None:
        """Permanently deleting inspections is forbidden to protect audit trail and evidence."""
        raise ConflictError(
            "Permanent inspection deletion is strictly forbidden to preserve regulatory "
            "defect evidence and historical compliance audits. Use archival instead."
        )

    def get_inspection_defects(
        self,
        identifier: Union[int, str],
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Defect], int]:
        """Fetch paginated defects registered under a specific inspection."""
        inspection = self.get_inspection(identifier)
        return self.defect_repo.list_defects(
            limit=limit,
            offset=offset,
            inspection_id=inspection.id,
        )
