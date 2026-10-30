"""System Administration Audit Event SQLAlchemy Model.

Provides an append-only, non-repudiation audit trail for security-critical operations
and regulatory compliance. Intentionally decoupled from foreign keys to guarantee
audit durability.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigIntId, UtcDateTime


class AuditEvent(Base):
    """Immutable audit event log tracking state changes and administrative actions."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Affected domain entity: INSPECTION, DEFECT, MODEL_CONFIG, SYSTEM_SETTING",
    )
    entity_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Surrogate or public ID of affected record",
    )
    action: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="Action performed: CREATE, UPDATE, ARCHIVE, DELETE, REVIEW_OVERRIDE",
    )
    performed_by: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Authenticated operator badge, username, or client identifier",
    )
    before_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Prior entity state snapshot serialized as JSON",
    )
    after_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Updated entity state snapshot serialized as JSON",
    )
    client_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Network client IP address issuing the request",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="UTC timestamp of audit entry creation",
    )

    def __repr__(self) -> str:
        return f"<AuditEvent(id={self.id}, action='{self.action}', entity='{self.entity_type}:{self.entity_id}', by='{self.performed_by}')>"

