"""Unit Tests for Frame to Odometry Spatial Localization.

Verifies encoder timestamp correlation, clock synchronization unavailability handling,
separation of capture and inference timestamps, and strict non-extrapolation rules.
"""

from app.localization.timestamp_associator import TimestampAssociator
from app.models.defect import DefectClass
from app.schemas.detection import BoundingBoxSchema, InferenceResult
from app.schemas.frame import FrameMetadata
from app.schemas.telemetry import EncoderTelemetryIngest
from app.services.telemetry_state import telemetry_state_service


def make_dummy_detection() -> InferenceResult:
    """Helper creating a test detection."""
    return InferenceResult(
        detection_id="det_test_01",
        frame_id="frame_test_01",
        defect_class=DefectClass.RUPTURE,
        confidence=0.92,
        bounding_box=BoundingBoxSchema(x=0.2, y=0.3, width=0.4, height=0.4),
        inference_timestamp="2026-10-30T16:20:00.250Z",
    )


def test_localization_missing_capture_timestamp_remains_unavailable() -> None:
    """Verify that a frame with no capture timestamp produces null distance and unavailable status."""
    associator = TimestampAssociator()
    detection = make_dummy_detection()

    metadata = FrameMetadata(
        frame_id="frame_test_01",
        camera_id="esp32_cam_01",
        capture_timestamp=None,
        backend_received_timestamp="2026-10-30T16:20:00.100Z",
        frame_width=640,
        frame_height=480,
    )

    result = associator.localize(detection, metadata)

    assert result.estimated_distance_meters is None
    assert result.localization_status == "unavailable"
    assert "missing_capture_timestamp" in (result.localization_reason or "")
    assert result.capture_timestamp is None


def test_localization_disabled_by_default_without_verified_hardware_sync() -> None:
    """Verify that physical localization is strictly disabled by default pending verified hardware clock sync."""
    associator = TimestampAssociator()  # Default allow_unverified_sync=False
    detection = make_dummy_detection()

    metadata = FrameMetadata(
        frame_id="frame_test_default_safety",
        camera_id="esp32_cam_01",
        capture_timestamp="2026-10-30T16:22:00.000Z",
        backend_received_timestamp="2026-10-30T16:22:00.050Z",
        frame_width=640,
        frame_height=480,
    )

    result = associator.localize(detection, metadata)

    assert result.estimated_distance_meters is None
    assert result.localization_status == "unavailable"
    assert "unverified_clock_synchronization" in (result.localization_reason or "")
    assert result.capture_timestamp == "2026-10-30T16:22:00.000Z"


def test_localization_clock_unsynchronized_without_matching_encoder() -> None:
    """Verify that an optical frame without matching encoder history is marked unavailable when sync is simulated."""
    telemetry_state_service.reset()
    associator = TimestampAssociator(max_tolerance_seconds=0.5, allow_unverified_sync=True)
    detection = make_dummy_detection()

    # Frame capture timestamp with no recorded encoder history
    metadata = FrameMetadata(
        frame_id="frame_test_02",
        camera_id="esp32_cam_01",
        capture_timestamp="2026-10-30T16:25:00.000Z",
        backend_received_timestamp="2026-10-30T16:25:00.080Z",
        frame_width=640,
        frame_height=480,
    )

    result = associator.localize(detection, metadata)

    assert result.estimated_distance_meters is None
    assert result.localization_status == "unavailable"
    assert "clock_unsynchronized" in (result.localization_reason or "")


def test_localization_successful_correlation_with_encoder_sample() -> None:
    """Verify that when verified sync is active and a valid encoder reading exists, distance is localized."""
    telemetry_state_service.reset()
    associator = TimestampAssociator(max_tolerance_seconds=0.5, allow_unverified_sync=True)

    # 1. Record encoder sample at 16:30:00.000Z with 5.42 meters penetration
    telemetry_state_service.record_encoder(
        EncoderTelemetryIngest(
            device_id="esp32_wroom_01",
            boot_id="boot_01",
            sequence_number=100,
            left_ticks=3600,
            right_ticks=3590,
            estimated_distance_meters=5.42,
            timestamp="2026-10-30T16:30:00.000Z",
        )
    )

    # 2. Optical frame captured 0.1s later (within 0.5s tolerance)
    detection = make_dummy_detection()
    metadata = FrameMetadata(
        frame_id="frame_test_03",
        camera_id="esp32_cam_01",
        capture_timestamp="2026-10-30T16:30:00.100Z",
        backend_received_timestamp="2026-10-30T16:30:00.150Z",
        frame_width=640,
        frame_height=480,
    )

    result = associator.localize(detection, metadata)

    assert result.estimated_distance_meters == 5.42
    assert result.localization_status == "localized"
    assert result.localization_reason is None
    assert result.capture_timestamp == "2026-10-30T16:30:00.100Z"


def test_separation_of_capture_and_inference_timestamps() -> None:
    """Verify that source capture timestamp and server inference timestamp remain strictly separate."""
    detection = make_dummy_detection()
    detection.inference_timestamp = "2026-10-30T16:35:00.999Z"

    metadata = FrameMetadata(
        frame_id="frame_test_04",
        camera_id="esp32_cam_01",
        capture_timestamp="2026-10-30T16:34:59.100Z",
        backend_received_timestamp="2026-10-30T16:35:00.010Z",
        frame_width=640,
        frame_height=480,
    )

    associator = TimestampAssociator()
    result = associator.localize(detection, metadata)

    # Capture timestamp reflects camera sensor time
    assert result.capture_timestamp == "2026-10-30T16:34:59.100Z"
    # Inference timestamp remains unchanged at AI execution time
    assert result.inference_timestamp == "2026-10-30T16:35:00.999Z"
    # They must never be conflated
    assert result.capture_timestamp != result.inference_timestamp
