"""Application Lifespan Context Manager.

Handles graceful startup and shutdown lifecycle events without attempting hardware connections.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI

from app.camera.camera_client import camera_client
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.init_db import init_db
from app.services.websocket_manager import websocket_manager
from app.vision.model_registry import get_active_provider

logger = logging.getLogger("pipebot.lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager executed during application startup and shutdown."""
    # 1. Initialize logging
    setup_logging()
    settings = get_settings()

    logger.info("Starting %s v%s in %s mode...", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)

    # 2. Initialize database storage and verify connection
    db_ready = init_db()
    if not db_ready:
        logger.warning("Database initialized with warnings. Verify database configuration.")
    else:
        logger.info("Database initialized and verified.")

    # Note: Hardware and camera initialization are explicitly decoupled and not run on startup.
    logger.info("Backend service is ready to accept requests on prefix: %s", settings.API_V1_PREFIX)

    yield

    # 3. Shutdown cleanup
    logger.info("Shutting down %s...", settings.APP_NAME)
    await camera_client.stop()
    await get_active_provider().shutdown()
    await websocket_manager.disconnect_all()

