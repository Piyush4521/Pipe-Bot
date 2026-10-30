"""MJPEG Stream Reader and Bounded Frame Queue Manager.

Streams multipart JPEG data from the ESP32-CAM optical endpoint,
parses frame boundaries, performs input validation, and feeds a bounded queue.
"""

import asyncio
from datetime import datetime, timezone
import logging
import time
from typing import Optional, Tuple
import uuid
import httpx
import numpy as np

from app.camera.camera_state import camera_state
from app.camera.frame_validator import frame_validator
from app.core.config import get_settings
from app.schemas.frame import CameraStatusEnum, FrameMetadata

logger = logging.getLogger("pipebot.frame_reader")


class MJPEGFrameReader:
    """Reads and parses an HTTP MJPEG stream into validated frames."""

    def __init__(self, frame_queue: Optional[asyncio.Queue] = None) -> None:
        self.settings = get_settings()
        self.queue: asyncio.Queue[Tuple[np.ndarray, FrameMetadata]] = (
            frame_queue if frame_queue is not None else asyncio.Queue(maxsize=self.settings.CAMERA_QUEUE_SIZE)
        )
        self.is_running = False
        self._sequence_counter = 0

    def reset_queue(self) -> None:
        """Drain queue contents and reset sequence numbering."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        self._sequence_counter = 0

    async def enqueue_frame(
        self,
        raw_bytes: bytes,
        capture_timestamp: Optional[str] = None,
        inspection_id: Optional[str] = None,
        uptime_seconds: Optional[float] = None,
    ) -> bool:
        """Validate and enqueue an incoming raw JPEG frame with bounded queue backpressure."""
        camera_state.record_frame_received()

        is_valid, img, err = frame_validator.validate_and_decode(raw_bytes)
        if not is_valid or img is None:
            camera_state.record_frame_rejected(err or "Unknown validation error")
            return False

        camera_state.record_frame_decoded()

        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._sequence_counter += 1
        h, w = img.shape[:2]

        metadata = FrameMetadata(
            frame_id=str(uuid.uuid4()),
            inspection_id=inspection_id,
            camera_id=self.settings.CAMERA_ID,
            capture_timestamp=capture_timestamp,
            backend_received_timestamp=now_utc,
            frame_width=w,
            frame_height=h,
            encoding="jpeg",
            sequence_number=self._sequence_counter,
            device_uptime_seconds=uptime_seconds,
        )

        # Handle queue capacity with drop-oldest backpressure policy
        if self.queue.full():
            try:
                self.queue.get_nowait()
                camera_state.record_frame_dropped()
            except asyncio.QueueEmpty:
                pass

        try:
            self.queue.put_nowait((img, metadata))
            return True
        except asyncio.QueueFull:
            camera_state.record_frame_dropped()
            return False

    async def stream_from_url(self, stream_url: str) -> None:
        """Continuously consume an HTTP MJPEG stream from the ESP32-CAM."""
        if not stream_url or stream_url.strip() == "":
            await camera_state.update_status(CameraStatusEnum.DISCONNECTED)
            return

        self.is_running = True
        await camera_state.update_status(CameraStatusEnum.CONNECTING)

        timeout = httpx.Timeout(
            connect=self.settings.CAMERA_CONNECT_TIMEOUT,
            read=self.settings.CAMERA_READ_TIMEOUT,
            write=5.0,
            pool=5.0,
        )

        min_frame_interval = 1.0 / max(1.0, self.settings.CAMERA_MAX_FPS)

        while self.is_running:
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("GET", stream_url) as response:
                        if response.status_code != 200:
                            err_msg = f"HTTP {response.status_code} from camera stream endpoint"
                            await camera_state.update_status(CameraStatusEnum.ERROR, error=err_msg)
                            await asyncio.sleep(2.0)
                            continue

                        await camera_state.update_status(CameraStatusEnum.STREAMING)
                        buffer = bytearray()
                        last_frame_mono = time.monotonic()

                        async for chunk in response.aiter_bytes():
                            if not self.is_running:
                                break

                            buffer.extend(chunk)

                            # Find JPEG markers: Start Of Image (0xFF, 0xD8) and End Of Image (0xFF, 0xD9)
                            start_idx = buffer.find(b"\xff\xd8")
                            end_idx = buffer.find(b"\xff\xd9")

                            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                                raw_jpeg = bytes(buffer[start_idx : end_idx + 2])
                                buffer = buffer[end_idx + 2 :]

                                # Enforce rate limit ceiling
                                elapsed = time.monotonic() - last_frame_mono
                                if elapsed < min_frame_interval:
                                    await asyncio.sleep(min_frame_interval - elapsed)

                                await self.enqueue_frame(raw_jpeg)
                                last_frame_mono = time.monotonic()

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("Camera stream disconnected: %s", exc)
                await camera_state.update_status(
                    CameraStatusEnum.ERROR,
                    error=f"Connection error: {str(exc)}",
                )
                if not self.is_running:
                    break
                await asyncio.sleep(2.0)

        await camera_state.update_status(CameraStatusEnum.DISCONNECTED)

