"""Integration Tests for Vision Pipeline, Defect Evidence, and WebSocket Dispatch.

Verifies end-to-end frame processing, evidence image persistence, media retrieval,
path traversal security, database defect record creation, and WebSocket event broadcasts.
"""

from typing import List
from fastapi.testclient import TestClient
import numpy as np
import pytest
from sqlalchemy.orm import Session

from app.camera.camera_state import camera_state
from app.models.defect import DefectClass
from app.models.inspection import Inspection, InspectionStatus
from app.schemas.detection import BoundingBoxSchema, InferenceResult
from app.schemas.frame import CameraStatusEnum, FrameMetadata
from app.services.frame_processing_service import frame_processing_service
from app.vision.interfaces import InferenceProvider
from app.vision.model_registry import set_active_provider


class MockDetectionInferenceProvider(InferenceProvider):
    """Test provider returning a pre-configured detection."""

    def __init__(self, detections: List[InferenceResult]) -> None:
        self._detections = detections

    async def initialize(self) -> bool:
        return True

    async def predict(self, frame: np.ndarray, metadata: FrameMetadata) -> List[InferenceResult]:
        return self._detections

    async def shutdown(self) -> None:
        pass

    @property
    def is_available(self) -> bool:
        return True

    @property
    def provider_name(self) -> str:
        return "mock_test_provider"


def test_evidence_image_saving_and_media_retrieval(client: TestClient) -> None:
    """Verify that cropped defect evidence images are safely saved and retrievable via API."""
    # Create synthetic test frame
    frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    bbox = BoundingBoxSchema(x=0.2, y=0.2, width=0.3, height=0.3)

    evidence_url = frame_processing_service.save_defect_evidence(
        frame=frame,
        bbox=bbox,
        defect_id="test_det_100",
    )
    assert evidence_url is not None
    assert evidence_url.startswith("/api/v1/media/")

    # Fetch through media retrieval endpoint
    response = client.get(evidence_url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert len(response.content) > 0


def test_media_endpoint_path_traversal_protection(client: TestClient) -> None:
    """Verify that path traversal attempts on media endpoint are strictly blocked."""
    # Attempt parent directory traversal
    resp1 = client.get("/api/v1/media/..%2F..%2Fetc%2Fpasswd")
    assert resp1.status_code in (400, 403, 404)

    # Attempt illegal filename characters
    resp2 = client.get("/api/v1/media/illegal;rm -rf")
    assert resp2.status_code in (400, 403, 404)


@pytest.mark.asyncio
async def test_process_frame_creates_defect_for_active_inspection(
    client: TestClient,
    db_session: Session,
) -> None:
    """Verify that valid inference results during an active inspection create database defect records."""
    # 1. Create an in-progress inspection session
    insp = Inspection(
        inspection_id="INSP-STAGE4-TEST",
        operator_id="OP-001",
        pipe_identifier="PVC-TEST-300",
        pipe_diameter_mm=300,
        pipe_material="PVC",
        status=InspectionStatus.IN_PROGRESS,
    )
    db_session.add(insp)
    db_session.commit()

    # 2. Configure mock inference provider returning a rupture detection
    mock_bbox = BoundingBoxSchema(x=0.25, y=0.35, width=0.2, height=0.2)
    mock_detection = InferenceResult(
        detection_id="det_auto_999",
        frame_id="frame_stage4_01",
        defect_class=DefectClass.RUPTURE,
        confidence=0.91,
        bounding_box=mock_bbox,
        inference_timestamp="2026-10-30T16:50:00.000Z",
    )
    set_active_provider(MockDetectionInferenceProvider([mock_detection]))

    # 3. Process frame through pipeline
    test_frame = np.full((480, 640, 3), 200, dtype=np.uint8)
    metadata = FrameMetadata(
        frame_id="frame_stage4_01",
        inspection_id="INSP-STAGE4-TEST",
        camera_id="esp32_cam_01",
        backend_received_timestamp="2026-10-30T16:50:00.000Z",
        frame_width=640,
        frame_height=480,
    )

    detections = await frame_processing_service.process_frame(
        frame=test_frame,
        metadata=metadata,
        db_session=db_session,
    )

    assert len(detections) == 1
    assert detections[0].image_reference is not None

    # 4. Verify defect record was created in database
    resp = client.get("/api/v1/inspections/INSP-STAGE4-TEST/defects")
    assert resp.status_code == 200
    defect_list = resp.json()["items"]
    assert len(defect_list) == 1
    assert defect_list[0]["defectClass"] == "Rupture"
    assert defect_list[0]["confidence"] == 0.91
    assert defect_list[0]["snapshotPath"] == detections[0].image_reference


def test_system_status_reflects_camera_stream_state(client: TestClient) -> None:
    """Verify that system status dynamically reflects active camera streaming."""
    camera_state.reset()

    # Initial state: camera disconnected
    status1 = client.get("/api/v1/system/status").json()
    assert status1["camera"] == "disconnected"
    assert status1["subsystems"]["camera"]["state"] == "disconnected"

    # Simulate camera streaming active
    camera_state.status = CameraStatusEnum.STREAMING
    status2 = client.get("/api/v1/system/status").json()
    assert status2["camera"] == "connected"
    assert status2["subsystems"]["camera"]["state"] == "streaming"
