"""SQLAlchemy Repository for Inspection Reports and Compliance Documents.

Provides persistence and query access for compliance certificates,
engineering summaries, and work orders.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import InspectionReport


class ReportRepository:
    """Repository managing inspection report persistence and lookup."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_report(
        self,
        report_id: str,
        inspection_id: int,
        report_type: str,
        report_format: str,
        file_path: str,
        file_size_bytes: int,
        checksum_sha256: str,
        overall_rating: str,
        generated_by: str,
    ) -> InspectionReport:
        """Create and persist a new inspection report metadata record."""
        report = InspectionReport(
            report_id=report_id,
            inspection_id=inspection_id,
            report_type=report_type,
            report_format=report_format,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            checksum_sha256=checksum_sha256,
            overall_rating=overall_rating,
            generated_by=generated_by,
            generated_at=datetime.now(timezone.utc),
        )
        self.db.add(report)
        self.db.flush()
        self.db.refresh(report)
        return report

    def get_report_by_id(self, report_id: str) -> Optional[InspectionReport]:
        """Fetch report by public report identifier."""
        stmt = select(InspectionReport).where(InspectionReport.report_id == report_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_reports_by_inspection(self, inspection_id: int) -> List[InspectionReport]:
        """List all reports associated with a specific inspection session."""
        stmt = (
            select(InspectionReport)
            .where(InspectionReport.inspection_id == inspection_id)
            .order_by(InspectionReport.generated_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_reports(self, limit: int = 50, offset: int = 0) -> List[InspectionReport]:
        """List reports across all inspections with pagination."""
        stmt = (
            select(InspectionReport)
            .order_by(InspectionReport.generated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

