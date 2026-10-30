"""Camera Client Service Lifecycle Manager.

Supervises camera stream connection, background task lifecycle,
reconnection policies, and frame queue management.
"""

import asyncio
import logging
from typing import Optional

from app.camera.camera_state import camera_state
from app.camera.frame_reader import MJPEGFrameReader
from app.core.config import get_settings
from app.schemas.frame import CameraStatusEnum

logger = logging.getLogger("pipebot.camera_client")


class CameraClient:
    """Manages the background ingestion loop for the ESP32-CAM stream."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.frame_reader = MJPEGFrameReader()
        self._task: Optional[asyncio.Task] = None

    @property
    def is_active(self) -> bool:
        """Whether the camera client background task is currently active."""
        return self._task is not None and not self._task.done()

    async def start(self, custom_url: Optional[str] = None) -> bool:
        """Start the background camera streaming task."""
        stream_url = custom_url or self.settings.CAMERA_STREAM_URL

        if not stream_url or stream_url.strip() == "":
            logger.info("Camera stream URL is not configured. Optical feed remains disconnected.")
            await camera_state.update_status(CameraStatusEnum.DISCONNECTED)
            return False

        if self.is_active:
            logger.warning("Camera stream worker task is already running.")
            return True

        self.frame_reader.reset_queue()
        camera_state.stream_url = stream_url

        self._task = asyncio.create_task(
            self.frame_reader.stream_from_url(stream_url),
            name="pipebot-camera-stream-worker",
        )
        logger.info("Started camera streaming worker task for URL: %s", stream_url)
        return True

    async def stop(self) -> None:
        """Gracefully stop the camera streaming worker task."""
        if not self.is_active and not self.frame_reader.is_running:
            await camera_state.update_status(CameraStatusEnum.DISCONNECTED)
            return

        logger.info("Stopping camera streaming worker task...")
        self.frame_reader.is_running = False

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=3.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            self._task = None

        self.frame_reader.reset_queue()
        await camera_state.update_status(CameraStatusEnum.DISCONNECTED)
        logger.info("Camera client stopped cleanly.")


# Global Camera Client Singleton
camera_client = CameraClient()

