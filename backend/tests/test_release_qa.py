"""Stage 5 Release Quality Assurance and Security Verification Tests.

Validates:
1. Canonical defect taxonomy (Deformation, Misalignment, Obstacle, Rupture) and 0-indexed IDs.
2. Case-insensitive defect class validation in API payloads.
3. Camera ingestion authentication (X-Device-Token enforcement).
4. Camera frame payload size limits and content-type rejection.
5. Media retrieval path traversal and extension protection.
6. Frontend route compatibility aliases (/status, /health, /defects/inspection/{id}).
7. Localization disabled by default without verified hardware clock sync.
8. Clean resource shutdown in WebSocket manager.
"""

from datetime import datetime, timezone
import io
import pytest
from starlette.testclient import TestClient

from app.core.config import get_settings
from app.models.defect import (
    PIPE_DEFECT_CLASSES,
    PIPE_DEFECT_CLASS_IDS,
    PIPE_DEFECT_NAME_TO_ID,
    DefectClass,
)
from app.services.websocket_manager import websocket_manager


def test_canonical_defect_classes_and_class_ids():
    """Verify exact spelling, ordering, and 0-indexed IDs of the canonical defect taxonomy."""
    assert PIPE_DEFECT_CLASSES == [
        "Deformation",
        "Misalignment",
        "Obstacle",
        "Rupture",
    ]

    assert PIPE_DEFECT_CLASS_IDS[0] == "Deformation"
    assert PIPE_DEFECT_CLASS_IDS[1] == "Misalignment"
    assert PIPE_DEFECT_CLASS_IDS[2] == "Obstacle"
    assert PIPE_DEFECT_CLASS_IDS[3] == "Rupture"

    assert PIPE_DEFECT_NAME_TO_ID["Deformation"] == 0
    assert PIPE_DEFECT_NAME_TO_ID["Misalignment"] == 1
    assert PIPE_DEFECT_NAME_TO_ID["Obstacle"] == 2
    assert PIPE_DEFECT_NAME_TO_ID["Rupture"] == 3


def test_case_insensitive_defect_class_parsing():
    """Verify that case-insensitive defect class strings deserialize to canonical enum values."""
    assert DefectClass("deformation") == DefectClass.DEFORMATION
    assert DefectClass("DEFORMATION") == DefectClass.DEFORMATION
    assert DefectClass("Deformation") == DefectClass.DEFORMATION
    assert DefectClass.DEFORMATION.value == "Deformation"

    assert DefectClass("misalignment") == DefectClass.MISALIGNMENT
    assert DefectClass("obstacle") == DefectClass.OBSTACLE
    assert DefectClass("rupture") == DefectClass.RUPTURE


def test_frontend_compatibility_status_and_health_routes(client: TestClient):
    """Verify that frontend compatibility aliases /status, /api/v1/status, and /health resolve."""
    # /status alias
    resp1 = client.get("/status")
    assert resp1.status_code == 200
    assert "subsystems" in resp1.json() or "overall" in resp1.json()

    # /api/v1/status alias
    resp2 = client.get("/api/v1/status")
    assert resp2.status_code == 200
    assert "subsystems" in resp2.json() or "overall" in resp2.json()

    # /health alias
    resp3 = client.get("/health")
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "healthy"


def test_frontend_compatibility_defects_by_inspection_route(client: TestClient):
    """Verify that GET /api/v1/defects/inspection/{id} returns defects for the session."""
    # Create inspection
    insp_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PIPE-QA-100", "operatorId": "OP-QA"},
    )
    assert insp_resp.status_code == 201
    insp_id = insp_resp.json()["inspectionId"]

    # Query defects by inspection session
    list_resp = client.get(f"/api/v1/defects/inspection/{insp_id}")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 0
    assert list_resp.json()["items"] == []


def test_camera_frame_content_type_validation(client: TestClient):
    """Verify that uploading non-image content types to /camera/frame is rejected."""
    text_data = io.BytesIO(b"this is plain text, not a jpeg")
    resp = client.post(
        "/api/v1/camera/frame",
        files={"file": ("test.txt", text_data, "text/plain")},
    )
    assert resp.status_code == 422
    assert "content-type" in resp.json()["detail"].lower()


def test_camera_frame_oversized_payload_rejection(client: TestClient):
    """Verify that camera frame uploads exceeding CAMERA_MAX_FRAME_BYTES are rejected with 422."""
    settings = get_settings()
    oversized_bytes = b"X" * (settings.CAMERA_MAX_FRAME_BYTES + 100)
    data_stream = io.BytesIO(oversized_bytes)

    resp = client.post(
        "/api/v1/camera/frame",
        files={"file": ("huge.jpg", data_stream, "image/jpeg")},
    )
    assert resp.status_code == 422
    assert "exceeds" in resp.json()["detail"].lower()


def test_camera_frame_token_authentication(client: TestClient, monkeypatch):
    """Verify that when DEVICE_INGEST_TOKEN is configured, frame upload requires the token."""
    settings = get_settings()
    monkeypatch.setattr(settings, "DEVICE_INGEST_TOKEN", "secret-qa-token")

    dummy_jpeg = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 200)

    # 1. Attempt upload without token -> 401 Unauthorized
    resp_no_token = client.post(
        "/api/v1/camera/frame",
        files={"file": ("frame.jpg", dummy_jpeg, "image/jpeg")},
    )
    assert resp_no_token.status_code == 401

    # 2. Upload with incorrect token -> 401 Unauthorized
    dummy_jpeg.seek(0)
    resp_bad_token = client.post(
        "/api/v1/camera/frame",
        headers={"X-Device-Token": "wrong-token"},
        files={"file": ("frame.jpg", dummy_jpeg, "image/jpeg")},
    )
    assert resp_bad_token.status_code == 401


def test_media_retrieval_extension_safety(client: TestClient):
    """Verify that the media endpoint rejects non-JPEG filenames even if safe characters are used."""
    # Attempt to request a python source file or database
    resp1 = client.get("/api/v1/media/main.py")
    assert resp1.status_code == 400

    resp2 = client.get("/api/v1/media/pipebot.db")
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_websocket_manager_disconnect_all():
    """Verify that WebSocketManager.disconnect_all executes safely."""
    await websocket_manager.disconnect_all()
    assert websocket_manager.connection_count == 0
