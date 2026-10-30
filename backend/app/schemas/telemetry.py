"""Pydantic Schemas for Telemetry Ingestion and WebSocket Envelopes.

Defines validation models for rotary encoder odometry, MPU6050 IMU metrics,
vehicle health telemetry, heartbeat diagnostics, and WebSocket message envelopes.
Matches the PipeBot React frontend interface contracts.
"""

from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


def validate_finite_float(value: Optional[float], field_name: str) -> Optional[float]:
    """Ensure floating point values are finite numbers and not NaN or Infinity."""
    if value is not None:
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"{field_name} must be a finite numerical value.")
    return value


class DeviceType(str, Enum):
    """Supported hardware and subsystem device types."""

    ESP32_WROOM = "ESP32_WROOM"
    ESP32_CAM = "ESP32_CAM"
    PROCESSING_SERVER = "PROCESSING_SERVER"


class ConnectionStatus(str, Enum):
    """Subsystem link connectivity states."""

    CONNECTED = "connected"
    STALE = "stale"
    DISCONNECTED = "disconnected"


class IngestionBase(BaseModel):
    """Common telemetry header attributes for embedded devices."""

    device_id: str = Field(..., description="Unique device hardware identifier")
    boot_id: str = Field(..., description="Unique boot session identifier for reboot detection")
    sequence_number: int = Field(..., ge=0, description="Monotonically increasing sequence number")
    timestamp: Optional[str] = Field(None, description="Device capture timestamp in ISO 8601 format")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


# Alias for explicit metadata reference
DeviceMetadata = IngestionBase


class EncoderTelemetryIngest(IngestionBase):
    """Rotary encoder sensor packet from ESP32."""

    left_ticks: int = Field(..., description="Cumulative left motor encoder tick count")
    right_ticks: int = Field(..., description="Cumulative right motor encoder tick count")
    left_rpm: Optional[float] = Field(None, description="Calculated left wheel rotational speed in RPM")
    right_rpm: Optional[float] = Field(None, description="Calculated right wheel rotational speed in RPM")
    estimated_distance_meters: Optional[float] = Field(
        None, ge=0.0, description="Estimated forward penetration distance in meters"
    )
    speed_mps: Optional[float] = Field(None, description="Linear velocity in meters per second")
    direction: Optional[str] = Field("forward", description="Drive direction: forward | reverse | stopped")

    @field_validator("left_rpm", "right_rpm", "estimated_distance_meters", "speed_mps")
    @classmethod
    def validate_finite_numbers(cls, v: Optional[float], info) -> Optional[float]:
        return validate_finite_float(v, info.field_name)


class IMUTelemetryIngest(IngestionBase):
    """MPU6050 6-axis inertial measurement unit packet."""

    accel_x: Optional[float] = Field(None, description="Linear acceleration X-axis in m/s^2 or g")
    accel_y: Optional[float] = Field(None, description="Linear acceleration Y-axis in m/s^2 or g")
    accel_z: Optional[float] = Field(None, description="Linear acceleration Z-axis in m/s^2 or g")
    gyro_x: Optional[float] = Field(None, description="Angular rate X-axis in deg/s")
    gyro_y: Optional[float] = Field(None, description="Angular rate Y-axis in deg/s")
    gyro_z: Optional[float] = Field(None, description="Angular rate Z-axis in deg/s")
    pitch_deg: Optional[float] = Field(None, description="Calculated pitch inclination angle in degrees")
    roll_deg: Optional[float] = Field(None, description="Calculated roll angle in degrees")
    yaw_deg: Optional[float] = Field(None, description="Calculated yaw heading angle in degrees")
    temperature_c: Optional[float] = Field(None, description="Internal sensor die temperature in Celsius")

    @field_validator(
        "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z",
        "pitch_deg", "roll_deg", "yaw_deg", "temperature_c"
    )
    @classmethod
    def validate_finite_numbers(cls, v: Optional[float], info) -> Optional[float]:
        return validate_finite_float(v, info.field_name)


class VehicleStatusIngest(IngestionBase):
    """Vehicle power, actuator status and safety state packet. Read-only telemetry."""

    controller_state: str = Field("connected", description="Microcontroller link state")
    motor_driver_state: str = Field("connected", description="Motor driver bridge state")
    left_motor_state: str = Field("idle", description="Left motor state: idle | forward | reverse | offline")
    right_motor_state: str = Field("idle", description="Right motor state: idle | forward | reverse | offline")
    emergency_stop_engaged: bool = Field(False, description="Hardware or software emergency stop active flag")
    command_ack_state: str = Field("idle", description="Last vehicle command state: idle | acknowledged | rejected")
    battery_voltage: Optional[float] = Field(None, ge=0.0, description="LiPo battery bus voltage in volts")
    battery_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Estimated battery percentage (0-100)")
    current_draw_amperes: Optional[float] = Field(None, ge=0.0, description="Total system current draw in amperes")
    operating_state: Optional[str] = Field("normal", description="Vehicle operational mode: normal | warning | estop")
    temperatures: Optional[Dict[str, float]] = Field(None, description="Component temperature dictionary in Celsius")

    @field_validator("battery_voltage", "battery_percent", "current_draw_amperes")
    @classmethod
    def validate_finite_numbers(cls, v: Optional[float], info) -> Optional[float]:
        return validate_finite_float(v, info.field_name)


class HeartbeatIngest(IngestionBase):
    """Lightweight periodic heartbeat packet from embedded devices."""

    device_type: DeviceType = Field(..., description="Device classification: ESP32_WROOM | ESP32_CAM")
    uptime_seconds: Optional[float] = Field(None, ge=0.0, description="Seconds elapsed since device boot")
    wifi_rssi_dbm: Optional[int] = Field(None, description="Wi-Fi received signal strength in dBm")
    free_heap_bytes: Optional[int] = Field(None, ge=0, description="Free microcontroller RAM in bytes")
    battery_voltage: Optional[float] = Field(None, ge=0.0, description="Current battery voltage reading")
    firmware_version: Optional[str] = Field(None, description="Running firmware build identifier")
    status: str = Field("ok", description="Device internal health string: ok | degraded | error")


# Response Models matching Frontend Types

class EncoderTelemetryResponse(BaseModel):
    """Rotary encoder response matching frontend EncoderTelemetry interface."""

    left_ticks: Optional[int] = Field(None, description="Left wheel cumulative ticks")
    right_ticks: Optional[int] = Field(None, description="Right wheel cumulative ticks")
    left_rpm: Optional[float] = Field(None, description="Left wheel rotational speed in RPM")
    right_rpm: Optional[float] = Field(None, description="Right wheel rotational speed in RPM")
    estimated_distance_meters: Optional[float] = Field(None, description="Total distance traveled in meters")
    speed_mps: Optional[float] = Field(None, description="Linear vehicle speed in meters per second")
    direction: Optional[str] = Field(None, description="Drive direction")
    timestamp: Optional[str] = Field(None, description="Timestamp of telemetry reading")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class IMUTelemetryResponse(BaseModel):
    """IMU response matching frontend IMUTelemetry interface."""

    accel_x: Optional[float] = Field(None, description="Linear acceleration X-axis")
    accel_y: Optional[float] = Field(None, description="Linear acceleration Y-axis")
    accel_z: Optional[float] = Field(None, description="Linear acceleration Z-axis")
    gyro_x: Optional[float] = Field(None, description="Angular velocity X-axis")
    gyro_y: Optional[float] = Field(None, description="Angular velocity Y-axis")
    gyro_z: Optional[float] = Field(None, description="Angular velocity Z-axis")
    pitch_degrees: Optional[float] = Field(None, description="Pitch angle in degrees")
    roll_degrees: Optional[float] = Field(None, description="Roll angle in degrees")
    yaw_degrees: Optional[float] = Field(None, description="Yaw angle in degrees")
    temperature_c: Optional[float] = Field(None, description="Temperature in Celsius")
    timestamp: Optional[str] = Field(None, description="Timestamp of IMU reading")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class VehicleTelemetryResponse(BaseModel):
    """Vehicle status response matching frontend VehicleTelemetry interface."""

    controller_state: str = Field("disconnected", description="Controller connection state")
    motor_driver_state: str = Field("disconnected", description="Motor driver connection state")
    left_motor_state: str = Field("offline", description="Left motor state")
    right_motor_state: str = Field("offline", description="Right motor state")
    emergency_stop_engaged: bool = Field(False, description="Emergency stop status")
    command_ack_state: str = Field("idle", description="Command acknowledgement state")
    battery_voltage: Optional[float] = Field(None, description="Battery voltage in volts")
    battery_percent: Optional[float] = Field(None, description="Battery percentage (0-100)")
    current_draw_amperes: Optional[float] = Field(None, description="Current draw in amperes")
    last_command_timestamp: Optional[str] = Field(None, description="Timestamp of last acknowledged command")
    operating_state: Optional[str] = Field("offline", description="Vehicle operational mode")
    timestamp: Optional[str] = Field(None, description="Timestamp of status update")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class LatestTelemetryResponse(BaseModel):
    """Composite telemetry snapshot response matching frontend LatestTelemetryResponse."""

    encoder: EncoderTelemetryResponse = Field(default_factory=EncoderTelemetryResponse)
    imu: IMUTelemetryResponse = Field(default_factory=IMUTelemetryResponse)
    vehicle: VehicleTelemetryResponse = Field(default_factory=VehicleTelemetryResponse)
    timestamp: str = Field(..., description="Timestamp of the snapshot evaluation")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class DeviceStatusDetail(BaseModel):
    """Connection diagnostics detail for an individual hardware device."""

    device_id: str = Field(..., description="Device identifier")
    device_type: str = Field(..., description="Hardware model / type")
    connection_status: str = Field(..., description="Link state: connected | stale | disconnected")
    boot_id: Optional[str] = Field(None, description="Current boot session identifier")
    last_sequence_number: Optional[int] = Field(None, description="Last recorded sequence number")
    last_seen_seconds_ago: Optional[float] = Field(None, description="Seconds elapsed since last packet")
    uptime_seconds: Optional[float] = Field(None, description="Reported device uptime in seconds")
    wifi_rssi_dbm: Optional[int] = Field(None, description="Last reported Wi-Fi signal strength")
    firmware_version: Optional[str] = Field(None, description="Reported firmware version")
    reboot_count: int = Field(0, description="Detected device reboot count")
    duplicate_packets_count: int = Field(0, description="Detected duplicate or out of order packets")
    total_packets_count: int = Field(0, description="Total valid packets received")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TelemetryStatusResponse(BaseModel):
    """Aggregate hardware link diagnostics response."""

    overall_status: str = Field(..., description="Overall hardware connection state")
    devices: Dict[str, DeviceStatusDetail] = Field(..., description="Per-device diagnostics map")
    active_ws_connections: int = Field(0, description="Number of active operator WebSocket connections")
    timestamp: str = Field(..., description="Evaluation timestamp in ISO 8601 UTC")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class WebSocketMessageEnvelope(BaseModel):
    """Typed WebSocket envelope matching frontend WebSocketMessage interface."""

    type: str = Field(..., description="Event type: telemetry_encoder | telemetry_imu | vehicle_status | system_status")
    timestamp: str = Field(..., description="Event generation timestamp in ISO 8601 UTC")
    payload: Any = Field(..., description="Event payload data")
