"""Unit and Integration Tests for Camera State, Reader, and Endpoints.

Verifies baseline disconnected state, camera client lifecycle, stream status reporting,
stale stream detection, and single-frame multipart upload ingestion.
"""

import io
import time
from fastapi.testclient import TestClient
from PIL import Image
import pytest

from app.camera.camera_client import camera_client
from app.camera.camera_state import camera_state
from app.schemas.frame import CameraStatusEnum


def make_test_jpeg(width: int = 320, height: int = 240) -> bytes:
    """Generate in-memory synthetic JPEG bytes."""
    img = Image.new("RGB", (width, height), color=(80, 160, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def test_camera_status_baseline_disconnected(client: TestClient) -> None:
    """Verify camera baseline status reports disconnected without fabricated metrics."""
    response = client.get("/api/v1/camera/status")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "disconnected"
    assert data["framesReceived"] == 0
    assert data["framesDecoded"] == 0
    assert data["framesDropped"] == 0
    assert data["fps"] == 0.0


def test_camera_start_with_no_url_stays_disconnected(client: TestClient) -> None:
    """Verify that starting camera with empty URL remains safely in disconnected state."""
    response = client.post("/api/v1/camera/start")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disconnected"


def test_camera_stop_endpoint(client: TestClient) -> None:
    """Verify that stopping camera client returns disconnected status."""
    response = client.post("/api/v1/camera/stop")
    assert response.status_code == 200
    assert response.json()["status"] == "disconnected"


def test_camera_stale_detection() -> None:
    """Verify that camera state evaluates to stale when no frames arrive within read timeout."""
    camera_state.reset()
    camera_state.status = CameraStatusEnum.STREAMING

    # Fresh frame arrived
    camera_state.record_frame_decoded()
    assert camera_state.check_stale() is False

    # Simulate 6.0 seconds elapsed (past CAMERA_READ_TIMEOUT = 5.0s)
    camera_state.last_frame_monotonic = time.monotonic() - 6.0
    assert camera_state.check_stale() is True


def test_ingest_single_frame_endpoint(client: TestClient) -> None:
    """Verify uploading a single optical JPEG frame via HTTP multipart."""
    raw_jpeg = make_test_jpeg(width=320, height=240)

    files = {
        "file": ("frame.jpg", raw_jpeg, "image/jpeg"),
    }
    data = {
        "captureTimestamp": "2026-10-30T16:15:00.100Z",
        "uptimeSeconds": 150.0,
    }

    response = client.post("/api/v1/camera/frame", files=files, data=data)
    assert response.status_code == 200
    meta = response.json()

    assert meta["frameWidth"] == 320
    assert meta["frameHeight"] == 240
    assert meta["encoding"] == "jpeg"
    assert meta["captureTimestamp"] == "2026-10-30T16:15:00.100Z"

    # Verify camera state counters updated
    status_resp = client.get("/api/v1/camera/status").json()
    assert status_resp["framesReceived"] == 1
    assert status_resp["framesDecoded"] == 1


def test_ingest_single_frame_empty_file_rejected(client: TestClient) -> None:
    """Verify that uploading empty bytes is rejected with HTTP 422."""
    files = {
        "file": ("empty.jpg", b"", "image/jpeg"),
    }
    response = client.post("/api/v1/camera/frame", files=files)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_camera_client_start_and_stop_lifecycle() -> None:
    """Verify camera client start and stop methods function cleanly."""
    camera_state.reset()
    assert camera_client.is_active is False

    # Stopping when inactive is a safe no-op
    await camera_client.stop()
    assert camera_client.is_active is False
    assert camera_state.status == CameraStatusEnum.DISCONNECTED

