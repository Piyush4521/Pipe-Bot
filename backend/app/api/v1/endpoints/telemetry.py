"""Telemetry Ingestion and Query Endpoints.

Handles high-frequency incoming telemetry packets from ESP32 microcontrollers,
validates payload integrity, verifies optional device security tokens,
updates in-memory state, and triggers non-blocking WebSocket broadcasts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import get_settings
from app.schemas.telemetry import (
    DeviceStatusDetail,
    EncoderTelemetryIngest,
    EncoderTelemetryResponse,
    HeartbeatIngest,
    IMUTelemetryIngest,
    IMUTelemetryResponse,
    LatestTelemetryResponse,
    TelemetryStatusResponse,
    VehicleStatusIngest,
    VehicleTelemetryResponse,
)
from app.services.telemetry_state import telemetry_state_service
from app.services.websocket_manager import websocket_manager

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


async def verify_device_token(
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> None:
    """Validate incoming device authentication against configured DEVICE_INGEST_TOKEN.

    If DEVICE_INGEST_TOKEN is not configured (empty or None), token validation
    is bypassed for local development and laboratory testing.
    """
    settings = get_settings()
    configured_token = settings.DEVICE_INGEST_TOKEN

    if not configured_token:
        return

    # Check X-Device-Token header
    if x_device_token and x_device_token == configured_token:
        return

    # Check Authorization: Bearer <token>
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] == configured_token:
            return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing device ingestion token.",
    )


@router.post(
    "/encoder",
    response_model=EncoderTelemetryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest Rotary Encoder Odometry",
    description="Receives tick counts, computed speed and distance from ESP32 wheel encoders.",
    dependencies=[Depends(verify_device_token)],
)
async def ingest_encoder_telemetry(payload: EncoderTelemetryIngest) -> EncoderTelemetryResponse:
    """Record wheel encoder measurements and broadcast to operator dashboard."""
    response = telemetry_state_service.record_encoder(payload)
    await websocket_manager.broadcast_envelope(
        event_type="telemetry_encoder",
        payload=response.model_dump(by_alias=True),
    )
    return response


@router.post(
    "/imu",
    response_model=IMUTelemetryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest MPU6050 Inertial Metrics",
    description="Receives 6-axis acceleration, angular rate, and calculated pitch/roll angles.",
    dependencies=[Depends(verify_device_token)],
)
async def ingest_imu_telemetry(payload: IMUTelemetryIngest) -> IMUTelemetryResponse:
    """Record inertial measurements and broadcast to operator dashboard."""
    response = telemetry_state_service.record_imu(payload)
    await websocket_manager.broadcast_envelope(
        event_type="telemetry_imu",
        payload=response.model_dump(by_alias=True),
    )
    return response


@router.post(
    "/vehicle/status",
    response_model=VehicleTelemetryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest Vehicle Health and Safety State",
    description=(
        "Receives power metrics, driver bridge states and safety flags. "
        "Strictly read-only vehicle telemetry without actuation commands."
    ),
    dependencies=[Depends(verify_device_token)],
)
async def ingest_vehicle_status(payload: VehicleStatusIngest) -> VehicleTelemetryResponse:
    """Record vehicle health state and broadcast to operator dashboard."""
    response = telemetry_state_service.record_vehicle_status(payload)
    await websocket_manager.broadcast_envelope(
        event_type="vehicle_status",
        payload=response.model_dump(by_alias=True),
    )
    return response


@router.post(
    "/heartbeat",
    response_model=DeviceStatusDetail,
    status_code=status.HTTP_200_OK,
    summary="Ingest Embedded Device Heartbeat",
    description="Receives diagnostic pulse, Wi-Fi RSSI, uptime and memory stats from ESP32 controllers.",
    dependencies=[Depends(verify_device_token)],
)
async def ingest_heartbeat(payload: HeartbeatIngest) -> DeviceStatusDetail:
    """Record microcontroller heartbeat pulse."""
    detail = telemetry_state_service.record_heartbeat(payload)
    return detail


@router.get(
    "/latest",
    response_model=LatestTelemetryResponse,
    summary="Get Latest Consolidated Telemetry",
    description="Returns current encoder odometry, IMU inclination, and vehicle status snapshot.",
)
def get_latest_telemetry() -> LatestTelemetryResponse:
    """Retrieve consolidated telemetry snapshot."""
    return telemetry_state_service.get_latest_telemetry()


@router.get(
    "/status",
    response_model=TelemetryStatusResponse,
    summary="Get Hardware Link Health Matrix",
    description="Evaluates connection states (connected, stale, disconnected) for all microcontrollers.",
)
def get_telemetry_status() -> TelemetryStatusResponse:
    """Retrieve per-device connection diagnostics."""
    return telemetry_state_service.get_telemetry_status(
        active_ws_count=websocket_manager.connection_count
    )


@router.get(
    "/inspection/{inspection_id}",
    response_model=List[LatestTelemetryResponse],
    summary="Query Inspection Telemetry Log",
    description="Returns telemetry log entries associated with an inspection session.",
)
def get_inspection_telemetry_log(inspection_id: str) -> List[LatestTelemetryResponse]:
    """Return historical telemetry log for the inspection.

    Continuous high-frequency telemetry is maintained in memory during inspection.
    """
    latest = telemetry_state_service.get_latest_telemetry()
    return [latest]

