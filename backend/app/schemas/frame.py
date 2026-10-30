"""Pydantic Schemas for Camera Ingestion and Frame Metadata.

Defines schemas for camera connection status, stream diagnostics,
and typed optical frame metadata.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CameraStatusEnum(str, Enum):
    """Camera hardware and video stream connection states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    STALE = "stale"
    ERROR = "error"


class CameraStatusResponse(BaseModel):
    """Subsystem status report for optical camera feed."""

    camera_id: str = Field(..., description="Unique camera device identifier")
    status: CameraStatusEnum = Field(..., description="Current camera connection state")
    stream_url: Optional[str] = Field(None, description="Configured camera stream endpoint")
    last_frame_timestamp: Optional[str] = Field(None, description="Timestamp of last successfully decoded frame")
    frames_received: int = Field(0, description="Total raw frames received from stream")
    frames_decoded: int = Field(0, description="Total valid JPEG frames successfully decoded")
    frames_rejected: int = Field(0, description="Corrupt or invalid frames rejected during validation")
    frames_dropped: int = Field(0, description="Frames dropped due to bounded queue capacity")
    processing_errors: int = Field(0, description="Pipeline processing errors encountered")
    last_error: Optional[str] = Field(None, description="Most recent error message if applicable")
    fps: float = Field(0.0, description="Rolling average frames processed per second")
    timestamp: str = Field(..., description="Evaluation timestamp in ISO 8601 UTC")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class FrameMetadata(BaseModel):
    """Typed metadata accompanying every optical capture frame."""

    frame_id: str = Field(..., description="Unique UUID identifier for the optical frame")
    inspection_id: Optional[str] = Field(None, description="Associated active inspection session identifier")
    camera_id: str = Field(..., description="Capturing camera hardware identifier")
    capture_timestamp: Optional[str] = Field(
        None, description="Source capture timestamp if provided by camera clock"
    )
    backend_received_timestamp: str = Field(
        ..., description="Server UTC timestamp when the frame entered backend ingestion"
    )
    frame_width: int = Field(..., gt=0, description="Horizontal pixel dimension")
    frame_height: int = Field(..., gt=0, description="Vertical pixel dimension")
    encoding: str = Field("jpeg", description="Frame image encoding format")
    sequence_number: int = Field(0, ge=0, description="Frame sequence counter")
    image_reference: Optional[str] = Field(None, description="Stored media path reference if saved")
    device_uptime_seconds: Optional[float] = Field(
        None, ge=0.0, description="Reported microcontroller uptime at capture"
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

