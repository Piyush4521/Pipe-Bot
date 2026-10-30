"""Unit Tests for Computer Vision Inference Providers and Model Registry.

Verifies unavailable provider fallback, missing model weights handling,
vision status endpoint reporting, defect class taxonomy enforcement,
and bounding box schema constraints.
"""

from fastapi.testclient import TestClient
import numpy as np
from pydantic import ValidationError
import pytest

from app.schemas.detection import BoundingBoxSchema, InferenceResult
from app.schemas.frame import FrameMetadata
from app.vision.model_registry import create_inference_provider
from app.vision.providers.ultralytics_provider import UltralyticsInferenceProvider
from app.vision.providers.unavailable_provider import UnavailableInferenceProvider


@pytest.mark.asyncio
async def test_unavailable_inference_provider_behavior() -> None:
    """Verify that UnavailableInferenceProvider reports is_available=False and returns empty detections."""
    provider = UnavailableInferenceProvider()
    init_res = await provider.initialize()
    assert init_res is True
    assert provider.is_available is False
    assert provider.provider_name == "unavailable"

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    dummy_meta = FrameMetadata(
        frame_id="frame-test-01",
        camera_id="esp32_cam_01",
        backend_received_timestamp="2026-10-30T16:00:00.000Z",
        frame_width=640,
        frame_height=480,
    )

    detections = await provider.predict(dummy_frame, dummy_meta)
    assert detections == []

    await provider.shutdown()
    assert provider.is_available is False


@pytest.mark.asyncio
async def test_ultralytics_provider_missing_weights_fails_cleanly() -> None:
    """Verify that Ultralytics provider fails initialization safely when weights are missing."""
    provider = UltralyticsInferenceProvider(model_path="/nonexistent/path/weights.pt")
    success = await provider.initialize()
    assert success is False
    assert provider.is_available is False


def test_vision_status_endpoint(client: TestClient) -> None:
    """Verify that vision status endpoint reports provider, device, and exact 4 defect classes."""
    response = client.get("/api/v1/vision/status")
    assert response.status_code == 200
    data = response.json()

    assert data["provider"] == "unavailable"
    assert data["isAvailable"] is False
    assert data["device"] == "cpu"
    assert set(data["expectedClasses"]) == {
        "Deformation",
        "Misalignment",
        "Obstacle",
        "Rupture",
    }


def test_bounding_box_schema_bounds_validation() -> None:
    """Verify that bounding box coordinates outside [0.0, 1.0] raise ValidationError."""
    # Valid bounding box
    bbox = BoundingBoxSchema(x=0.1, y=0.2, width=0.3, height=0.4)
    assert bbox.x == 0.1

    # Invalid negative x coordinate
    with pytest.raises(ValidationError):
        BoundingBoxSchema(x=-0.05, y=0.2, width=0.3, height=0.4)

    # Invalid width exceeding 1.0
    with pytest.raises(ValidationError):
        BoundingBoxSchema(x=0.1, y=0.2, width=1.05, height=0.4)


def test_inference_result_confidence_bounds_validation() -> None:
    """Verify that confidence outside [0.0, 1.0] raises ValidationError."""
    bbox = BoundingBoxSchema(x=0.1, y=0.1, width=0.2, height=0.2)

    # Valid confidence 0.85
    result = InferenceResult(
        detection_id="det_01",
        frame_id="frame_01",
        defect_class="deformation",
        confidence=0.85,
        bounding_box=bbox,
        inference_timestamp="2026-10-30T16:00:00.000Z",
    )
    assert result.confidence == 0.85

    # Invalid confidence 1.25
    with pytest.raises(ValidationError):
        InferenceResult(
            detection_id="det_01",
            frame_id="frame_01",
            defect_class="deformation",
            confidence=1.25,
            bounding_box=bbox,
            inference_timestamp="2026-10-30T16:00:00.000Z",
        )


def test_model_registry_defaults_to_unavailable() -> None:
    """Verify that factory creates an UnavailableInferenceProvider under default configuration."""
    provider = create_inference_provider()
    assert isinstance(provider, UnavailableInferenceProvider)
    assert provider.is_available is False

