"""Frame Processing, Evidence Storage, and Defect Event Coordination Service.

Orchestrates frame validation, inference execution, spatial localization,
cropped defect image evidence persistence, and WebSocket event distribution.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
import re
import time
from typing import List, Optional
import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.localization.timestamp_associator import timestamp_associator
from app.models.defect import DefectClass
from app.repositories.inspection_repository import InspectionRepository
from app.schemas.defect import BoundingBoxSchema as DefectApiBBox, DefectCreate, DefectResponse
from app.schemas.detection import InferenceResult
from app.schemas.frame import FrameMetadata
from app.services.defect_service import DefectService
from app.services.websocket_manager import websocket_manager
from app.vision.model_registry import get_active_provider

logger = logging.getLogger("pipebot.frame_processing")

FILENAME_SAFE_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]+$")


class FrameProcessingService:
    """Coordinates computer vision pipeline, localization, and defect persistence."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def save_defect_evidence(
        self,
        frame: np.ndarray,
        bbox,
        defect_id: str,
    ) -> Optional[str]:
        """Save cropped anomaly evidence JPEG image safely to the media directory.

        Applies 10% bounding box padding, verifies filename safety,
        and returns the relative URL path reference.
        """
        try:
            media_dir = self.settings.media_dir
            h, w = frame.shape[:2]

            # Convert normalized bounding box to pixel coordinates with 10% context padding
            pad_x = int(bbox.width * w * 0.1)
            pad_y = int(bbox.height * h * 0.1)

            x1 = max(0, int(bbox.x * w) - pad_x)
            y1 = max(0, int(bbox.y * h) - pad_y)
            x2 = min(w, int((bbox.x + bbox.width) * w) + pad_x)
            y2 = min(h, int((bbox.y + bbox.height) * h) + pad_y)

            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                crop = frame

            # Generate safe unique filename and verify against path traversal
            safe_id = re.sub(r"[^a-zA-Z0-9_]", "", defect_id)
            timestamp_int = int(time.time() * 1000)
            filename = f"defect_{safe_id}_{timestamp_int}.jpg"

            if not FILENAME_SAFE_REGEX.match(filename):
                logger.error("Generated filename '%s' violates security regex.", filename)
                return None

            file_path = (media_dir / filename).resolve()
            if not str(file_path).startswith(str(media_dir.resolve())):
                logger.error("Path traversal detected for filename: %s", filename)
                return None

            # Prevent unintentional overwrites
            if file_path.exists():
                filename = f"defect_{safe_id}_{timestamp_int}_{uuid.uuid4().hex[:6]}.jpg"
                file_path = (media_dir / filename).resolve()

            # Encode and save with OpenCV
            write_success = cv2.imwrite(str(file_path), crop, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if not write_success or not file_path.exists():
                logger.error("OpenCV imwrite returned failure for: %s", file_path)
                return None

            # Verify saved file size within limits
            if file_path.stat().st_size > self.settings.CAMERA_MAX_FRAME_BYTES:
                file_path.unlink(missing_ok=True)
                logger.error("Saved evidence image exceeded max bytes limit: %s", filename)
                return None

            logger.info("Saved defect evidence image: %s (%dx%d)", filename, crop.shape[1], crop.shape[0])
            return f"/api/v1/media/{filename}"

        except Exception as exc:
            logger.error("Failed to save defect evidence image: %s", exc)
            return None

    async def process_frame(
        self,
        frame: np.ndarray,
        metadata: FrameMetadata,
        db_session: Optional[Session] = None,
    ) -> List[InferenceResult]:
        """Execute complete inference, localization, evidence storage, and defect persistence."""
        provider = get_active_provider()
        detections = await provider.predict(frame, metadata)

        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Process each detected anomaly
        for detection in detections:
            # 1. Spatially correlate frame with encoder odometry at capture time
            timestamp_associator.localize(detection, metadata)

            # 2. Persist cropped defect evidence image
            evidence_ref = self.save_defect_evidence(
                frame=frame,
                bbox=detection.bounding_box,
                defect_id=detection.detection_id,
            )
            detection.image_reference = evidence_ref

            # 3. If an inspection session is active, persist defect record to database
            active_inspection_id = metadata.inspection_id
            if not active_inspection_id:
                # Check database for currently active inspection session
                session = db_session or SessionLocal()
                try:
                    active = InspectionRepository.get_active(session)
                    if active:
                        active_inspection_id = active.inspection_id
                finally:
                    if db_session is None:
                        session.close()

            if active_inspection_id:
                session = db_session or SessionLocal()
                try:
                    # Convert bounding box to Defect schema representation
                    defect_api_bbox = DefectApiBBox(
                        x=detection.bounding_box.x,
                        y=detection.bounding_box.y,
                        width=detection.bounding_box.width,
                        height=detection.bounding_box.height,
                    )

                    capture_ts = metadata.capture_timestamp or metadata.backend_received_timestamp or now_utc

                    defect_create_payload = DefectCreate(
                        inspection_id=active_inspection_id,
                        defect_id=detection.detection_id,
                        defect_class=detection.defect_class,
                        confidence=detection.confidence,
                        frame_id=metadata.frame_id,
                        capture_timestamp=capture_ts,
                        inference_timestamp=detection.inference_timestamp,
                        estimated_distance_meters=detection.estimated_distance_meters,
                        bounding_box=defect_api_bbox,
                        snapshot_path=evidence_ref,
                        notes="Identified automatically by PipeBot YOLO vision pipeline.",
                    )

                    service = DefectService(session)
                    created_defect = service.create_defect(defect_create_payload)
                    logger.info(
                        "Created defect record %s for inspection %s",
                        created_defect.defect_id,
                        active_inspection_id,
                    )

                    # Broadcast defect_detected WebSocket event
                    defect_response = DefectResponse.model_validate(created_defect)
                    await websocket_manager.broadcast_envelope(
                        event_type="defect_detected",
                        payload=defect_response.model_dump(by_alias=True),
                    )

                except Exception as exc:
                    logger.error("Failed persisting defect to database: %s", exc)
                finally:
                    if db_session is None:
                        session.close()

            # 4. Broadcast localization unavailable warning if applicable
            if detection.localization_status == "unavailable":
                await websocket_manager.broadcast_envelope(
                    event_type="localization_unavailable",
                    payload={
                        "detectionId": detection.detection_id,
                        "frameId": metadata.frame_id,
                        "reason": detection.localization_reason,
                        "timestamp": now_utc,
                    },
                )

        # 5. Broadcast compact frame processing summary event
        await websocket_manager.broadcast_envelope(
            event_type="frame_processed",
            payload={
                "frameId": metadata.frame_id,
                "sequenceNumber": metadata.sequence_number,
                "width": metadata.frame_width,
                "height": metadata.frame_height,
                "detectionsCount": len(detections),
                "timestamp": now_utc,
            },
        )

        return detections


# Global Frame Processing Service Singleton
frame_processing_service = FrameProcessingService()
