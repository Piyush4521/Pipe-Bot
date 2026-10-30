"""Inspection Event SQLAlchemy Model.

Tracks granular state transitions and operational milestone events
during pipeline inspection runs.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.inspection import Inspection


class InspectionEvent(Base):
    """SQLAlchemy model for pipeline inspection operational events."""

    __tablename__ = "inspection_events"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    inspection_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("inspections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent inspection session",
    )
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Event identifier: STATE_CHANGE, OBSTACLE_ENCOUNTERED, NOTE_LOGGED",
    )
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Contextual metadata snapshot for the event",
    )
    occurred_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="UTC timestamp of event occurrence",
    )

    # Relationship to parent inspection
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="events",
    )

    def __repr__(self) -> str:
        return f"<InspectionEvent(id={self.id}, type='{self.event_type}', inspection_id={self.inspection_id})>"

