"""SQLAlchemy Repository for Camera Frames and Defect Evidence Media.

Provides persistence and query access for optical frame captures and
localized defect evidence images.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.media import CameraFrame, EvidenceMedia


class MediaRepository:
    """Repository managing camera capture metadata and defect evidence records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def record_camera_frame(
        self,
        frame_id: str,
        inspection_id: int,
        frame_width: int,
        frame_height: int,
        frame_bytes: int,
        camera_id: str = "esp32-cam-front",
        frame_sequence: int = 0,
        encoding: str = "jpeg",
        capture_timestamp: Optional[datetime] = None,
        processing_status: str = "pending",
        has_defect: bool = False,
    ) -> CameraFrame:
        """Persist frame capture metadata."""
        frame = CameraFrame(
            frame_id=frame_id,
            inspection_id=inspection_id,
            camera_id=camera_id,
            frame_sequence=frame_sequence,
            frame_width=frame_width,
            frame_height=frame_height,
            encoding=encoding,
            frame_bytes=frame_bytes,
            capture_timestamp=capture_timestamp,
            recorded_at=datetime.now(timezone.utc),
            processing_status=processing_status,
            has_defect=has_defect,
        )
        self.db.add(frame)
        self.db.flush()
        self.db.refresh(frame)
        return frame

    def get_frame_by_id(self, frame_id: str) -> Optional[CameraFrame]:
        """Fetch frame metadata by public frame UUID."""
        stmt = select(CameraFrame).where(CameraFrame.frame_id == frame_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_frames_by_inspection(
        self, inspection_id: int, limit: int = 100, offset: int = 0
    ) -> List[CameraFrame]:
        """Retrieve paginated camera frames for an inspection session."""
        stmt = (
            select(CameraFrame)
            .where(CameraFrame.inspection_id == inspection_id)
            .order_by(CameraFrame.frame_sequence.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def update_frame_status(
        self, frame_id: str, status: str, has_defect: bool = False
    ) -> Optional[CameraFrame]:
        """Update inference processing status and defect flag for a frame."""
        frame = self.get_frame_by_id(frame_id)
        if frame:
            frame.processing_status = status
            frame.has_defect = has_defect
            self.db.flush()
            self.db.refresh(frame)
        return frame

    def record_evidence(
        self,
        media_uuid: str,
        defect_id: int,
        file_path: str,
        mime_type: str,
        file_size_bytes: int,
        checksum_sha256: str,
        storage_backend: str = "LOCAL_FS",
    ) -> EvidenceMedia:
        """Persist localized defect crop evidence metadata."""
        evidence = EvidenceMedia(
            media_uuid=media_uuid,
            defect_id=defect_id,
            file_path=file_path,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            checksum_sha256=checksum_sha256,
            storage_backend=storage_backend,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(evidence)
        self.db.flush()
        self.db.refresh(evidence)
        return evidence

    def get_evidence_by_uuid(self, media_uuid: str) -> Optional[EvidenceMedia]:
        """Fetch evidence media by public UUID."""
        stmt = select(EvidenceMedia).where(EvidenceMedia.media_uuid == media_uuid)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_evidence_by_defect_id(self, defect_id: int) -> List[EvidenceMedia]:
        """List all evidence crops linked to a specific defect."""
        stmt = (
            select(EvidenceMedia)
            .where(EvidenceMedia.defect_id == defect_id)
            .order_by(EvidenceMedia.created_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

