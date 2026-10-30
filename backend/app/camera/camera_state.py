"""Camera State and Health Monitoring Service.

Maintains real-time connection state, frame counters, rolling FPS metrics,
and error logs for the ESP32-CAM video pipeline.
"""

from datetime import datetime, timezone
import logging
import time
from typing import Optional

from app.core.config import get_settings
from app.schemas.frame import CameraStatusEnum, CameraStatusResponse

logger = logging.getLogger("pipebot.camera_state")


class CameraState:
    """Thread-safe state tracking for optical camera feed."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.camera_id = self.settings.CAMERA_ID
        self.status = CameraStatusEnum.DISCONNECTED
        self.stream_url = self.settings.CAMERA_STREAM_URL or None
        self.last_frame_timestamp: Optional[str] = None
        self.last_frame_monotonic: Optional[float] = None
        self.frames_received = 0
        self.frames_decoded = 0
        self.frames_rejected = 0
        self.frames_dropped = 0
        self.processing_errors = 0
        self.last_error: Optional[str] = None
        self._recent_frame_times = []

    def reset(self) -> None:
        """Reset internal metrics for isolated testing."""
        self.camera_id = self.settings.CAMERA_ID
        self.status = CameraStatusEnum.DISCONNECTED
        self.stream_url = self.settings.CAMERA_STREAM_URL or None
        self.last_frame_timestamp = None
        self.last_frame_monotonic = None
        self.frames_received = 0
        self.frames_decoded = 0
        self.frames_rejected = 0
        self.frames_dropped = 0
        self.processing_errors = 0
        self.last_error = None
        self._recent_frame_times.clear()

    async def update_status(self, new_status: CameraStatusEnum, error: Optional[str] = None) -> None:
        """Update connection status and broadcast transition via WebSocket."""
        changed = self.status != new_status or error != self.last_error
        self.status = new_status
        if error:
            self.last_error = error

        if changed:
            logger.info("Camera %s state transitioned to: %s", self.camera_id, new_status.value)
            from app.services.websocket_manager import websocket_manager

            status_data = self.get_status().model_dump(by_alias=True)
            await websocket_manager.broadcast_envelope(
                event_type="camera_status",
                payload=status_data,
            )

    def record_frame_received(self) -> None:
        """Increment raw frame counter."""
        self.frames_received += 1

    def record_frame_decoded(self) -> None:
        """Record a successfully decoded frame and update FPS calculation."""
        now_mono = time.monotonic()
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self.frames_decoded += 1
        self.last_frame_timestamp = now_utc
        self.last_frame_monotonic = now_mono

        # Maintain a 2.0-second rolling window for FPS computation
        self._recent_frame_times.append(now_mono)
        cutoff = now_mono - 2.0
        self._recent_frame_times = [t for t in self._recent_frame_times if t >= cutoff]

    def record_frame_rejected(self, reason: str) -> None:
        """Record invalid or corrupt frame rejection."""
        self.frames_rejected += 1
        self.last_error = f"Validation rejected: {reason}"
        logger.warning("Frame rejected: %s", reason)

    def record_frame_dropped(self) -> None:
        """Record frame dropped due to queue saturation."""
        self.frames_dropped += 1

    def record_processing_error(self, exc_str: str) -> None:
        """Record error encountered during downstream frame processing."""
        self.processing_errors += 1
        self.last_error = f"Processing error: {exc_str}"

    @property
    def current_fps(self) -> float:
        """Calculate current rolling frames per second."""
        if len(self._recent_frame_times) < 2:
            return 0.0
        duration = self._recent_frame_times[-1] - self._recent_frame_times[0]
        if duration <= 0:
            return 0.0
        return round((len(self._recent_frame_times) - 1) / duration, 1)

    def check_stale(self) -> bool:
        """Evaluate whether camera stream has gone stale based on elapsed time."""
        if self.status not in (CameraStatusEnum.STREAMING, CameraStatusEnum.CONNECTED):
            return False
        if self.last_frame_monotonic is None:
            return False
        elapsed = time.monotonic() - self.last_frame_monotonic
        if elapsed > self.settings.CAMERA_READ_TIMEOUT:
            return True
        return False

    def get_status(self) -> CameraStatusResponse:
        """Return a structured camera status report."""
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return CameraStatusResponse(
            camera_id=self.camera_id,
            status=self.status,
            stream_url=self.stream_url,
            last_frame_timestamp=self.last_frame_timestamp,
            frames_received=self.frames_received,
            frames_decoded=self.frames_decoded,
            frames_rejected=self.frames_rejected,
            frames_dropped=self.frames_dropped,
            processing_errors=self.processing_errors,
            last_error=self.last_error,
            fps=self.current_fps,
            timestamp=now_utc,
        )


# Global Camera State Singleton
camera_state = CameraState()
