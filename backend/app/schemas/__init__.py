"""Central Pydantic Schemas Registry."""

from app.schemas.health import (
    DatabaseHealthResponse,
    HealthResponse,
    ReadinessResponse,
    SubsystemDetail,
    SystemStatusResponse,
)
from app.schemas.inspection import (
    InspectionBase,
    InspectionCreate,
    InspectionListResponse,
    InspectionResponse,
    InspectionStatusUpdate,
    InspectionUpdate,
)
from app.schemas.defect import (
    BoundingBoxSchema,
    DefectBase,
    DefectCreate,
    DefectListResponse,
    DefectResponse,
    DefectReviewUpdate,
)
from app.schemas.telemetry import (
    ConnectionStatus,
    DeviceMetadata,
    DeviceStatusDetail,
    DeviceType,
    EncoderTelemetryIngest,
    EncoderTelemetryResponse,
    HeartbeatIngest,
    IMUTelemetryIngest,
    IMUTelemetryResponse,
    LatestTelemetryResponse,
    TelemetryStatusResponse,
    VehicleStatusIngest,
    VehicleTelemetryResponse,
    WebSocketMessageEnvelope,
)

from app.schemas.frame import (
    CameraStatusEnum,
    CameraStatusResponse,
    FrameMetadata,
)
from app.schemas.detection import (
    InferenceResult,
    InferenceStatusResponse,
)

__all__ = [
    "HealthResponse",
    "ReadinessResponse",
    "DatabaseHealthResponse",
    "SubsystemDetail",
    "SystemStatusResponse",
    "InspectionBase",
    "InspectionCreate",
    "InspectionUpdate",
    "InspectionStatusUpdate",
    "InspectionResponse",
    "InspectionListResponse",
    "BoundingBoxSchema",
    "DefectBase",
    "DefectCreate",
    "DefectReviewUpdate",
    "DefectResponse",
    "DefectListResponse",
    "DeviceType",
    "ConnectionStatus",
    "DeviceMetadata",
    "EncoderTelemetryIngest",
    "IMUTelemetryIngest",
    "VehicleStatusIngest",
    "HeartbeatIngest",
    "EncoderTelemetryResponse",
    "IMUTelemetryResponse",
    "VehicleTelemetryResponse",
    "LatestTelemetryResponse",
    "DeviceStatusDetail",
    "TelemetryStatusResponse",
    "WebSocketMessageEnvelope",
    "CameraStatusEnum",
    "CameraStatusResponse",
    "FrameMetadata",
    "InferenceResult",
    "InferenceStatusResponse",
]
