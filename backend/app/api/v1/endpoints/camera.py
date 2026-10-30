"""Camera Control and Frame Ingestion Endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.v1.endpoints.telemetry import verify_device_token
from app.camera.camera_client import camera_client
from app.camera.camera_state import camera_state
from app.core.config import get_settings
from app.schemas.frame import CameraStatusResponse, FrameMetadata
from app.services.frame_processing_service import frame_processing_service

logger = logging.getLogger("pipebot.camera_endpoint")
router = APIRouter(prefix="/camera", tags=["Camera Ingestion"])


@router.get(
    "/status",
    response_model=CameraStatusResponse,
    summary="Get Camera Stream Status",
    description="Returns current link state, frame counters, decoding statistics, and rolling FPS.",
)
def get_camera_status() -> CameraStatusResponse:
    """Retrieve optical camera subsystem link status."""
    return camera_state.get_status()


@router.post(
    "/start",
    response_model=CameraStatusResponse,
    summary="Start Camera Stream Worker",
    description="Initiates background MJPEG stream consumption from the configured ESP32-CAM endpoint.",
)
async def start_camera_stream(stream_url: Optional[str] = None) -> CameraStatusResponse:
    """Start optical video stream ingestion."""
    await camera_client.start(custom_url=stream_url)
    return camera_state.get_status()


@router.post(
    "/stop",
    response_model=CameraStatusResponse,
    summary="Stop Camera Stream Worker",
    description="Gracefully terminates the background camera ingestion worker and drains queues.",
)
async def stop_camera_stream() -> CameraStatusResponse:
    """Stop optical video stream ingestion."""
    await camera_client.stop()
    return camera_state.get_status()


@router.post(
    "/frame",
    response_model=FrameMetadata,
    status_code=status.HTTP_200_OK,
    summary="Ingest Single Optical Frame",
    description="Directly uploads an optical JPEG frame for processing and defect inference.",
)
async def ingest_single_frame(
    file: UploadFile = File(..., description="JPEG frame image binary"),
    capture_timestamp: Optional[str] = Form(None, alias="captureTimestamp", description="Optical capture timestamp in ISO 8601 UTC"),
    inspection_id: Optional[str] = Form(None, alias="inspectionId", description="Associated inspection session identifier"),
    uptime_seconds: Optional[float] = Form(None, alias="uptimeSeconds", description="ESP32-CAM uptime in seconds"),
    _auth: None = Depends(verify_device_token),
) -> FrameMetadata:
    """Directly ingest, validate, and process a single optical frame."""
    settings = get_settings()

    # 1. Content-type validation
    if file.content_type and file.content_type not in [
        "image/jpeg",
        "image/jpg",
        "application/octet-stream",
    ]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid content-type '{file.content_type}'. Frame must be image/jpeg.",
        )

    # 2. Maximum payload size bounds check
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Empty frame file payload received.",
        )

    if len(raw_bytes) > settings.CAMERA_MAX_FRAME_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Frame payload size ({len(raw_bytes)} bytes) exceeds configured "
                f"maximum limit ({settings.CAMERA_MAX_FRAME_BYTES} bytes)."
            ),
        )

    # 3. Enqueue and decode frame
    success = await camera_client.frame_reader.enqueue_frame(
        raw_bytes=raw_bytes,
        capture_timestamp=capture_timestamp,
        inspection_id=inspection_id,
        uptime_seconds=uptime_seconds,
    )

    if not success or camera_client.frame_reader.queue.empty():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=camera_state.last_error or "Frame validation failed.",
        )

    img, metadata = await camera_client.frame_reader.queue.get()

    # 4. Process frame through inference pipeline
    await frame_processing_service.process_frame(img, metadata)

    return metadata
