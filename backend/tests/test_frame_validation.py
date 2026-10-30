"""Unit Tests for Optical Frame Validation and Queue Backpressure.

Tests valid JPEG decoding, empty buffer rejection, malformed byte handling,
oversized frames, dimension boundaries, queue capacity limits, and dropped frame metrics.
"""

import io
from PIL import Image
import pytest

from app.camera.camera_state import camera_state
from app.camera.frame_reader import MJPEGFrameReader
from app.camera.frame_validator import FrameValidator


def make_test_jpeg(width: int = 320, height: int = 240, color: tuple = (120, 180, 240)) -> bytes:
    """Generate in-memory synthetic JPEG byte buffer."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def test_valid_jpeg_decoding() -> None:
    """Verify that a valid synthetic JPEG image decodes correctly into OpenCV BGR array."""
    validator = FrameValidator()
    raw_bytes = make_test_jpeg(width=640, height=480)

    is_valid, img, err = validator.validate_and_decode(raw_bytes)
    assert is_valid is True
    assert img is not None
    assert err is None
    assert img.shape == (480, 640, 3)


def test_empty_frame_rejection() -> None:
    """Verify that empty or zero-byte buffers are rejected with descriptive error."""
    validator = FrameValidator()
    is_valid, img, err = validator.validate_and_decode(b"")
    assert is_valid is False
    assert img is None
    assert "empty" in (err or "").lower()


def test_malformed_jpeg_rejection() -> None:
    """Verify that corrupt or random non-JPEG bytes fail decode safely without server crashes."""
    validator = FrameValidator()
    garbage = b"\xff\xd8\xff\xe0" + b"\x00\x11\x22\x33" * 50
    is_valid, img, err = validator.validate_and_decode(garbage)
    assert is_valid is False
    assert img is None
    assert "failed to decode" in (err or "").lower()


def test_oversized_frame_byte_rejection() -> None:
    """Verify that frames exceeding max_bytes limit are rejected."""
    validator = FrameValidator()
    raw_bytes = make_test_jpeg(width=320, height=240)

    # Enforce a tiny maximum threshold to test limit
    is_valid, img, err = validator.validate_and_decode(raw_bytes, max_bytes=100)
    assert is_valid is False
    assert img is None
    assert "exceeds maximum limit" in (err or "")


def test_oversized_dimensions_rejection() -> None:
    """Verify that images exceeding maximum width or height bounds are rejected."""
    validator = FrameValidator()
    raw_bytes = make_test_jpeg(width=800, height=600)

    is_valid, img, err = validator.validate_and_decode(raw_bytes, max_width=640, max_height=480)
    assert is_valid is False
    assert img is None
    assert "exceed configured bounds" in (err or "")


@pytest.mark.asyncio
async def test_frame_queue_bounded_capacity_and_drop_accounting() -> None:
    """Verify that bounded queue drops oldest frame when full and increments drop counter."""
    camera_state.reset()
    reader = MJPEGFrameReader()
    # Queue size is configured to 10
    queue_limit = reader.settings.CAMERA_QUEUE_SIZE
    test_jpeg = make_test_jpeg(width=160, height=120)

    # Fill queue to capacity
    for i in range(queue_limit):
        success = await reader.enqueue_frame(test_jpeg)
        assert success is True

    assert reader.queue.qsize() == queue_limit
    assert camera_state.frames_dropped == 0

    # Enqueue 3 additional frames beyond capacity
    for _ in range(3):
        success = await reader.enqueue_frame(test_jpeg)
        assert success is True

    # Queue length must not exceed queue_limit
    assert reader.queue.qsize() == queue_limit
    # Dropped frame counter must reflect the 3 dropped frames
    assert camera_state.frames_dropped == 3

