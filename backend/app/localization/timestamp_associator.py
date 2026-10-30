"""Optical Frame to Odometry Spatial Localization Service.

Evaluates optical defect detections against rotary wheel encoder odometry samples
based strictly on frame capture timestamps, rather than server inference completion time.

Engineering Safety and Hardware Synchronization Policy:
1. The ESP32-CAM and ESP32-WROOM-32 are separate microcontrollers without automatic clock synchronization.
2. The server receipt time or inference completion time must never be used as physical location time.
3. Unless verified hardware shutter clock synchronization is confirmed, physical localization is
   strictly disabled by default (allow_unverified_sync=False).
4. Raw timestamps (capture_timestamp, backend_received_timestamp, inference_timestamp) are preserved.
5. In PVC conduits, wheel slippage, cable drag, and conduit slope introduce mechanical odometry error;
   encoder distance is an engineering estimate rather than geodetic ground truth.
"""

from datetime import datetime, timezone
import logging
from typing import Optional

from app.schemas.detection import InferenceResult
from app.schemas.frame import FrameMetadata
from app.services.telemetry_state import telemetry_state_service

logger = logging.getLogger("pipebot.localization")


class TimestampAssociator:
    """Evaluates optical frame capture events against recorded vehicle odometry.

    Enforces the non-extrapolation guarantee: distances are never inferred
    from inference latency or server arrival times.
    """

    def __init__(
        self,
        max_tolerance_seconds: float = 0.5,
        allow_unverified_sync: bool = False,
    ) -> None:
        self.max_tolerance_seconds = max_tolerance_seconds
        self.allow_unverified_sync = allow_unverified_sync

    def localize(
        self,
        detection: InferenceResult,
        metadata: FrameMetadata,
    ) -> InferenceResult:
        """Evaluate frame capture metadata and assign spatial location if verified.

        Rules:
        1. Distinguishes frame capture timestamp, device uptime, and backend received time.
        2. Never uses inference completion timestamp as the physical location timestamp.
        3. If no verified hardware clock synchronization mechanism exists, disables physical localization,
           sets estimated_distance_meters = None, and assigns an explicit unavailable reason.
        4. Preserves raw capture and inference timestamps unmodified.
        """
        # Preserve raw frame capture timestamp from optical sensor metadata
        detection.capture_timestamp = metadata.capture_timestamp

        # Case 1: Optical frame has no source capture timestamp
        if not metadata.capture_timestamp:
            detection.estimated_distance_meters = None
            detection.localization_status = "unavailable"
            detection.localization_reason = (
                "missing_capture_timestamp: Optical frame lacks frame capture timestamp"
            )
            return detection

        # Case 2: Unverified hardware clock synchronization boundary
        if not self.allow_unverified_sync:
            detection.estimated_distance_meters = None
            detection.localization_status = "unavailable"
            detection.localization_reason = (
                "unverified_clock_synchronization: ESP32-CAM and ESP32-WROOM-32 lack "
                "verified hardware shutter clock synchronization. Physical localization "
                "is suspended pending embedded clock synchronization validation."
            )
            return detection

        # Case 3: Parse frame capture timestamp when verified sync is enabled
        try:
            clean_ts = metadata.capture_timestamp.replace("Z", "+00:00")
            capture_dt = datetime.fromisoformat(clean_ts)
            if capture_dt.tzinfo is None:
                capture_dt = capture_dt.replace(tzinfo=timezone.utc)
            capture_utc = capture_dt.astimezone(timezone.utc)
        except Exception as exc:
            logger.warning("Unparseable capture timestamp '%s': %s", metadata.capture_timestamp, exc)
            detection.estimated_distance_meters = None
            detection.localization_status = "unavailable"
            detection.localization_reason = (
                f"unparseable_capture_timestamp: Failed parsing '{metadata.capture_timestamp}'"
            )
            return detection

        # Case 4: Query TelemetryStateService encoder history within max tolerance
        matched_encoder = telemetry_state_service.get_encoder_at_timestamp(
            target_dt=capture_utc,
            max_delta_seconds=self.max_tolerance_seconds,
        )

        if matched_encoder is not None and matched_encoder.estimated_distance_meters is not None:
            detection.estimated_distance_meters = matched_encoder.estimated_distance_meters
            detection.localization_status = "localized"
            detection.localization_reason = None
            logger.info(
                "Localized detection %s to distance %.2f m (encoder ticks: %s/%s)",
                detection.detection_id,
                matched_encoder.estimated_distance_meters,
                matched_encoder.left_ticks,
                matched_encoder.right_ticks,
            )
        else:
            detection.estimated_distance_meters = None
            detection.localization_status = "unavailable"
            detection.localization_reason = (
                f"clock_unsynchronized: No matching encoder sample found within "
                f"{self.max_tolerance_seconds}s tolerance for frame capture time"
            )

        return detection


# Global Timestamp Associator Singleton (default: physical localization disabled until hardware sync verified)
timestamp_associator = TimestampAssociator()
