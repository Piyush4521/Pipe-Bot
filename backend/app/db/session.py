"""Database Engine and Session Management.

Configures SQLAlchemy 2.x engine, sessionmaker, and FastAPI dependency injection.
Enforces SQLite foreign-key constraints via connection event listeners.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite-specific connect args
connect_args = {}
if settings.resolved_database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.resolved_database_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce foreign key integrity constraints and busy timeout on SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a managed database session with guaranteed closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def transaction_scope(session: Session) -> Generator[Session, None, None]:
    """Execute a transaction block with automatic commit and rollback on exception."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise

