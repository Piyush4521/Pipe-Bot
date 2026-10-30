"""SQLAlchemy Repository for Defect Detections.

Encapsulates all database operations, queries, filtering, and pagination
for the Defect entity, evidence media attachments, and localization correlations.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.defect import Defect, DefectClass, DefectReviewStatus
from app.models.localization import LocalizationRecord
from app.models.media import EvidenceMedia


class DefectRepository:
    """Repository managing persistence and queries for Defect entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, defect: Defect) -> Defect:
        """Persist a new defect detection record."""
        self.db.add(defect)
        self.db.flush()
        self.db.refresh(defect)
        return defect

    def get_by_id(self, internal_id: int, include_deleted: bool = False) -> Optional[Defect]:
        """Fetch a defect by its internal primary key."""
        stmt = (
            select(Defect)
            .options(
                selectinload(Defect.inspection),
                selectinload(Defect.evidence_media),
                selectinload(Defect.localization_record),
            )
            .where(Defect.id == internal_id)
        )
        if not include_deleted:
            stmt = stmt.where(Defect.is_deleted.is_(False))
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_defect_id(self, public_id: str, include_deleted: bool = False) -> Optional[Defect]:
        """Fetch a defect by its public unique identifier (e.g. DEF-20261030-XYZ123)."""
        stmt = (
            select(Defect)
            .options(
                selectinload(Defect.inspection),
                selectinload(Defect.evidence_media),
                selectinload(Defect.localization_record),
            )
            .where(Defect.defect_id == public_id)
        )
        if not include_deleted:
            stmt = stmt.where(Defect.is_deleted.is_(False))
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_any_id(self, identifier: Union[int, str], include_deleted: bool = False) -> Optional[Defect]:
        """Lookup defect by either public identifier string or numeric ID."""
        if isinstance(identifier, int):
            return self.get_by_id(identifier, include_deleted=include_deleted)
        if isinstance(identifier, str):
            defect = self.get_by_defect_id(identifier, include_deleted=include_deleted)
            if defect:
                return defect
            if identifier.isdigit():
                return self.get_by_id(int(identifier), include_deleted=include_deleted)
        return None

    def exists_by_defect_id(self, public_id: str) -> bool:
        """Check whether a defect public ID is already registered."""
        stmt = select(func.count(Defect.id)).where(Defect.defect_id == public_id)
        return bool(self.db.execute(stmt).scalar() or 0)

    def list_defects(
        self,
        limit: int = 50,
        offset: int = 0,
        inspection_id: Optional[int] = None,
        defect_class: Optional[DefectClass] = None,
        review_status: Optional[DefectReviewStatus] = None,
        search: Optional[str] = None,
        include_deleted: bool = False,
    ) -> Tuple[List[Defect], int]:
        """Retrieve paginated defect records with multi-criteria filtering."""
        query = select(Defect).options(
            selectinload(Defect.inspection),
            selectinload(Defect.evidence_media),
            selectinload(Defect.localization_record),
        )
        count_query = select(func.count(Defect.id))

        if not include_deleted:
            query = query.where(Defect.is_deleted.is_(False))
            count_query = count_query.where(Defect.is_deleted.is_(False))

        if inspection_id is not None:
            query = query.where(Defect.inspection_id == inspection_id)
            count_query = count_query.where(Defect.inspection_id == inspection_id)

        if defect_class is not None:
            query = query.where(Defect.defect_class == defect_class)
            count_query = count_query.where(Defect.defect_class == defect_class)

        if review_status is not None:
            query = query.where(Defect.review_status == review_status)
            count_query = count_query.where(Defect.review_status == review_status)

        if search:
            search_pattern = f"%{search.strip()}%"
            condition = or_(
                Defect.frame_id.ilike(search_pattern),
                Defect.defect_id.ilike(search_pattern),
                Defect.notes.ilike(search_pattern),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)

        total = self.db.execute(count_query).scalar() or 0
        query = query.order_by(Defect.created_at.desc()).limit(limit).offset(offset)
        items = list(self.db.execute(query).scalars().all())

        return items, total

    def list_defects_by_distance(
        self,
        inspection_id: int,
        limit: int = 50,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> List[Defect]:
        """Retrieve localized defects ordered monotonically by forward pipeline distance."""
        query = (
            select(Defect)
            .options(
                selectinload(Defect.inspection),
                selectinload(Defect.evidence_media),
                selectinload(Defect.localization_record),
            )
            .where(
                Defect.inspection_id == inspection_id,
                Defect.estimated_distance_meters.is_not(None),
            )
        )
        if not include_deleted:
            query = query.where(Defect.is_deleted.is_(False))

        query = query.order_by(Defect.estimated_distance_meters.asc()).limit(limit).offset(offset)
        return list(self.db.execute(query).scalars().all())

    def count_by_inspection(self, inspection_id: int, include_deleted: bool = False) -> int:
        """Count total defects recorded for an inspection session."""
        stmt = select(func.count(Defect.id)).where(Defect.inspection_id == inspection_id)
        if not include_deleted:
            stmt = stmt.where(Defect.is_deleted.is_(False))
        return self.db.execute(stmt).scalar() or 0

    def update(self, defect: Defect) -> Defect:
        """Commit updates to an existing defect entity."""
        self.db.add(defect)
        self.db.flush()
        self.db.refresh(defect)
        return defect

    def soft_delete(self, defect: Defect) -> Defect:
        """Soft-delete a defect record to preserve inspection regulatory audit trails."""
        defect.is_deleted = True
        return self.update(defect)

    def attach_evidence(
        self,
        defect_id: int,
        media_uuid: str,
        file_path: str,
        file_size_bytes: int,
        checksum_sha256: str,
        mime_type: str = "image/jpeg",
        storage_backend: str = "LOCAL_FS",
    ) -> EvidenceMedia:
        """Attach an on-disk evidence media reference to a defect record."""
        evidence = EvidenceMedia(
            media_uuid=media_uuid,
            defect_id=defect_id,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            checksum_sha256=checksum_sha256,
            mime_type=mime_type,
            storage_backend=storage_backend,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(evidence)
        self.db.flush()
        self.db.refresh(evidence)
        return evidence

    def attach_localization(
        self,
        defect_id: int,
        frame_capture_timestamp: datetime,
        encoder_sample_timestamp: datetime,
        temporal_delta_ms: float,
        clock_sync_status: str = "UNVERIFIED_SYNC",
        frame_id: Optional[str] = None,
        sync_notes: Optional[str] = None,
        left_encoder_ticks: Optional[int] = None,
        right_encoder_ticks: Optional[int] = None,
        computed_distance_meters: Optional[float] = None,
    ) -> LocalizationRecord:
        """Attach a spatial localization correlation record to a defect detection."""
        loc = LocalizationRecord(
            defect_id=defect_id,
            frame_id=frame_id,
            frame_capture_timestamp=frame_capture_timestamp,
            encoder_sample_timestamp=encoder_sample_timestamp,
            temporal_delta_ms=temporal_delta_ms,
            clock_sync_status=clock_sync_status,
            sync_notes=sync_notes,
            left_encoder_ticks=left_encoder_ticks,
            right_encoder_ticks=right_encoder_ticks,
            computed_distance_meters=computed_distance_meters,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(loc)
        self.db.flush()
        self.db.refresh(loc)
        return loc
