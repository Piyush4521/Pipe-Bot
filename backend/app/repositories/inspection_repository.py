"""SQLAlchemy Repository for Inspection Sessions.

Encapsulates all database operations, queries, filtering, pagination, and archival
for the Inspection entity.
"""

from typing import List, Optional, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.inspection import Inspection, InspectionStatus


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
