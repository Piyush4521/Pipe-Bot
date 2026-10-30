"""SQLAlchemy Repository for Append-Only System Audit Events.

Provides immutable logging and querying of administrative, security,
and operational actions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


class AuditRepository:
    """Repository managing audit event persistence and security log retrieval."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def log_event(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        performed_by: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        client_ip: Optional[str] = None,
    ) -> AuditEvent:
        """Create and persist an immutable audit event."""
        event = AuditEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            performed_by=performed_by,
            before_state=before_state,
            after_state=after_state,
            client_ip=client_ip,
            recorded_at=datetime.now(timezone.utc),
        )
        self.db.add(event)
        self.db.flush()
        self.db.refresh(event)
        return event

    def get_event_by_id(self, event_id: int) -> Optional[AuditEvent]:
        """Fetch single audit event by surrogate key."""
        stmt = select(AuditEvent).where(AuditEvent.id == event_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_events_by_entity(
        self, entity_type: str, entity_id: str, limit: int = 100
    ) -> List[AuditEvent]:
        """List audit history for a specific domain entity."""
        stmt = (
            select(AuditEvent)
            .where(
                AuditEvent.entity_type == entity_type,
                AuditEvent.entity_id == entity_id,
            )
            .order_by(AuditEvent.recorded_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_recent_events(
        self, limit: int = 100, offset: int = 0
    ) -> List[AuditEvent]:
        """List recent audit events across the platform with pagination."""
        stmt = (
            select(AuditEvent)
            .order_by(AuditEvent.recorded_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

