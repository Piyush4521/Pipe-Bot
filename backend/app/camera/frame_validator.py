"""Frame Validation and OpenCV Decoding Utility.

Validates raw incoming frame payloads against size and dimension thresholds,
decodes JPEG bytes with OpenCV, and rejects malformed or corrupt payloads safely.
"""

import logging
from typing import Optional, Tuple
import cv2
import numpy as np

from app.core.config import get_settings

logger = logging.getLogger("pipebot.frame_validator")


class FrameValidator:
    """Validates raw image bytes and decodes into OpenCV BGR numpy arrays."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def validate_and_decode(
        self,
        raw_bytes: bytes,
        max_bytes: Optional[int] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> Tuple[bool, Optional[np.ndarray], Optional[str]]:
        """Validate and decode a raw JPEG byte buffer.

        Returns:
            Tuple of (is_valid, decoded_image_array, error_message)
        """
        limit_bytes = max_bytes or self.settings.CAMERA_MAX_FRAME_BYTES
        limit_w = max_width or self.settings.CAMERA_MAX_FRAME_WIDTH
        limit_h = max_height or self.settings.CAMERA_MAX_FRAME_HEIGHT

        # 1. Check for empty payload
        if not raw_bytes or len(raw_bytes) == 0:
            return False, None, "Frame payload is empty"

        # 2. Check maximum byte length
        if len(raw_bytes) > limit_bytes:
            return (
                False,
                None,
                f"Frame size ({len(raw_bytes)} bytes) exceeds maximum limit ({limit_bytes} bytes)",
            )

        # 3. Safe OpenCV decode
        try:
            np_buffer = np.frombuffer(raw_bytes, dtype=np.uint8)
            img = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

            if img is None:
                return False, None, "Failed to decode image: Corrupt or unsupported JPEG format"

            h, w = img.shape[:2]

            # 4. Check positive dimensions
            if w <= 0 or h <= 0:
                return False, None, f"Invalid image dimensions: {w}x{h}"

            # 5. Check maximum dimension limits
            if w > limit_w or h > limit_h:
                return (
                    False,
                    None,
                    f"Frame dimensions ({w}x{h}) exceed configured bounds ({limit_w}x{limit_h})",
                )

            return True, img, None

        except Exception as exc:
            logger.warning("Unexpected exception during frame decode: %s", exc)
            return False, None, f"Decode exception: {str(exc)}"


frame_validator = FrameValidator()

