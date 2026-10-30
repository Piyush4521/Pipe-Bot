"""SQLAlchemy Repository for Inspection Sessions.

Encapsulates all database operations, queries, filtering, pagination, and archival
for the Inspection entity, events, and computed summaries.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.defect import Defect, DefectClass
from app.models.inspection import Inspection, InspectionStatus
from app.models.inspection_event import InspectionEvent
from app.models.inspection_summary import InspectionSummary


class InspectionRepository:
    """Repository managing persistence and queries for Inspection entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, inspection: Inspection) -> Inspection:
        """Persist a new inspection session record."""
        self.db.add(inspection)
        self.db.flush()
        self.db.refresh(inspection)
        return inspection

    def get_by_id(self, internal_id: int) -> Optional[Inspection]:
        """Fetch an inspection by its internal primary key (including archived records)."""
        stmt = (
            select(Inspection)
            .options(selectinload(Inspection.defects))
            .where(Inspection.id == internal_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_inspection_id(self, public_id: str) -> Optional[Inspection]:
        """Fetch an inspection by its public unique identifier (including archived records)."""
        stmt = (
            select(Inspection)
            .options(selectinload(Inspection.defects))
            .where(Inspection.inspection_id == public_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_any_id(self, identifier: Union[int, str]) -> Optional[Inspection]:
        """Lookup inspection by either public identifier string or numeric ID."""
        if isinstance(identifier, int):
            return self.get_by_id(identifier)
        if isinstance(identifier, str):
            inspection = self.get_by_inspection_id(identifier)
            if inspection:
                return inspection
            if identifier.isdigit():
                return self.get_by_id(int(identifier))
        return None

    def exists_by_inspection_id(self, public_id: str) -> bool:
        """Check whether an inspection public ID is already registered."""
        stmt = select(func.count(Inspection.id)).where(Inspection.inspection_id == public_id)
        return bool(self.db.execute(stmt).scalar() or 0)

    def list_inspections(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[InspectionStatus] = None,
        include_archived: bool = False,
    ) -> Tuple[List[Inspection], int]:
        """Retrieve paginated inspection sessions with optional status and archival filtering."""
        query = select(Inspection).options(selectinload(Inspection.defects))
        count_query = select(func.count(Inspection.id))

        if not include_archived:
            query = query.where(Inspection.is_archived.is_(False))
            count_query = count_query.where(Inspection.is_archived.is_(False))

        if status is not None:
            query = query.where(Inspection.status == status)
            count_query = count_query.where(Inspection.status == status)

        total = self.db.execute(count_query).scalar() or 0
        query = query.order_by(Inspection.created_at.desc()).limit(limit).offset(offset)
        items = list(self.db.execute(query).scalars().all())

        return items, total

    def update(self, inspection: Inspection) -> Inspection:
        """Commit updates to an existing inspection entity."""
        self.db.add(inspection)
        self.db.flush()
        self.db.refresh(inspection)
        return inspection

    def archive(self, inspection: Inspection) -> Inspection:
        """Safely archive an inspection session without deleting associated defect evidence."""
        inspection.is_archived = True
        return self.update(inspection)

    def record_event(
        self,
        inspection_id: int,
        event_type: str,
        payload: Optional[dict] = None,
        occurred_at: Optional[datetime] = None,
    ) -> InspectionEvent:
        """Record an operational milestone event for an inspection session."""
        event_obj = InspectionEvent(
            inspection_id=inspection_id,
            event_type=event_type,
            payload=payload,
            occurred_at=occurred_at or datetime.now(timezone.utc),
        )
        self.db.add(event_obj)
        self.db.flush()
        self.db.refresh(event_obj)
        return event_obj

    def get_timeline(self, inspection_id: int) -> List[InspectionEvent]:
        """Retrieve the operational event timeline for an inspection in chronological order."""
        stmt = (
            select(InspectionEvent)
            .where(InspectionEvent.inspection_id == inspection_id)
            .order_by(InspectionEvent.occurred_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_summary(self, inspection_id: int) -> Optional[InspectionSummary]:
        """Fetch the pre-aggregated summary snapshot for an inspection."""
        stmt = select(InspectionSummary).where(InspectionSummary.inspection_id == inspection_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def refresh_summary(self, inspection_id: int) -> InspectionSummary:
        """Calculate and upsert denormalized inspection summary metrics."""
        defects = list(
            self.db.execute(
                select(Defect).where(Defect.inspection_id == inspection_id, Defect.is_deleted.is_(False))
            ).scalars().all()
        )

        total_count = len(defects)
        deformation_cnt = sum(1 for d in defects if d.defect_class == DefectClass.DEFORMATION)
        misalignment_cnt = sum(1 for d in defects if d.defect_class == DefectClass.MISALIGNMENT)
        obstacle_cnt = sum(1 for d in defects if d.defect_class == DefectClass.OBSTACLE)
        rupture_cnt = sum(1 for d in defects if d.defect_class == DefectClass.RUPTURE)

        # Compliance grading logic based on defect severity
        if rupture_cnt >= 2 or total_count > 10:
            grade = "FAIL"
        elif rupture_cnt == 1 or total_count > 5:
            grade = "D"
        elif total_count > 2:
            grade = "C"
        elif total_count > 0:
            grade = "B"
        else:
            grade = "A"

        inspection = self.get_by_id(inspection_id)
        runtime_seconds = 0
        if inspection and inspection.started_at and inspection.completed_at:
            runtime_seconds = max(0, int((inspection.completed_at - inspection.started_at).total_seconds()))

        summary = self.get_summary(inspection_id)
        if not summary:
            summary = InspectionSummary(
                inspection_id=inspection_id,
                total_defects_count=total_count,
                deformation_count=deformation_cnt,
                misalignment_count=misalignment_cnt,
                obstacle_count=obstacle_cnt,
                rupture_count=rupture_cnt,
                overall_pipe_grade=grade,
                total_runtime_seconds=runtime_seconds,
                compiled_at=datetime.now(timezone.utc),
            )
            self.db.add(summary)
        else:
            summary.total_defects_count = total_count
            summary.deformation_count = deformation_cnt
            summary.misalignment_count = misalignment_cnt
            summary.obstacle_count = obstacle_cnt
            summary.rupture_count = rupture_cnt
            summary.overall_pipe_grade = grade
            summary.total_runtime_seconds = runtime_seconds
            summary.compiled_at = datetime.now(timezone.utc)
            self.db.add(summary)

        self.db.flush()
        return summary
