"""Database Initialization Routines.

Verifies connectivity and prepares the SQLite database storage directory on startup.
"""

import logging
from sqlalchemy import text
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger("pipebot.db")


def init_db() -> bool:
    """Initialize database directory and verify database connectivity."""
    settings = get_settings()
    logger.info("Verifying database configuration at: %s", settings.resolved_database_url)

    try:
        # Ensure tables defined in models are synchronized
        Base.metadata.create_all(bind=engine)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            if result == 1:
                logger.info("Database connectivity verified successfully.")
                return True
            logger.error("Unexpected database verification response: %s", result)
            return False
    except Exception as exc:
        logger.error("Failed to initialize or connect to database: %s", exc)
        return False

