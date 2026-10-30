"""SQLAlchemy Declarative Base and UTC Timestamp TypeDecorator.

Ensures strict UTC normalization, consistent constraint naming, and timezone awareness
across SQLite and all database engines.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, MetaData, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Explicit naming conventions for SQLite batch operations and relational constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)


class UtcDateTime(TypeDecorator):
    """SQLAlchemy TypeDecorator guaranteeing UTC timezone awareness across SQLite.

    SQLite storage behavior:
    SQLite does not natively enforce or store timezone offsets in DateTime columns.
    This decorator guarantees:
    1. Bind Parameter: Any incoming datetime (offset-aware or naive) is converted to UTC.
       Naive timestamps are explicitly interpreted as UTC per documented system policy.
    2. Result Value: Any datetime retrieved from the database is returned as a
       timezone-aware Python datetime with tzinfo=timezone.utc.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: Optional[datetime], dialect) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                # Documented policy: naive datetimes are interpreted as UTC
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value

    def process_result_value(self, value: Optional[datetime], dialect) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value


class Base(DeclarativeBase):
    """Base class for all application database models with standardized constraint naming."""

    metadata = metadata


class TimestampMixin:
    """Reusable audit timestamp mixin providing strict UTC created_at and updated_at fields."""

    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
