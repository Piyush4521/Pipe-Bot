"""In-Memory Telemetry State and Device Connection Management Service.

Provides thread-safe in-memory caching of high-frequency sensor streams,
monotonic sequence tracking, device reboot detection, and dynamic connection
state evaluation without persisting continuous telemetry to the database.
"""

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import time
from typing import Dict, Optional

from app.core.config import get_settings
from app.schemas.telemetry import (
    ConnectionStatus,
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
)

logger = logging.getLogger("pipebot.telemetry_state")


@dataclass
class DeviceRecord:
    """Internal device state tracking record."""

    device_id: str
    device_type: str
    boot_id: str
    last_sequence_number: int
    last_seen_monotonic: float
    last_seen_wall: float
    uptime_seconds: Optional[float] = None
    wifi_rssi_dbm: Optional[int] = None
    firmware_version: Optional[str] = None
    reboot_count: int = 0
    duplicate_packets_count: int = 0
    total_packets_count: int = 0


class TelemetryStateService:
    """Singleton service for in-memory telemetry state and connection tracking."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._devices: Dict[str, DeviceRecord] = {}
        self._latest_encoder: Optional[EncoderTelemetryResponse] = None
        self._latest_imu: Optional[IMUTelemetryResponse] = None
        self._latest_vehicle: Optional[VehicleTelemetryResponse] = None
        self._encoder_history: deque = deque(maxlen=500)

    def reset(self) -> None:
        """Reset internal telemetry state for isolated testing."""
        self._devices.clear()
        self._latest_encoder = None
        self._latest_imu = None
        self._latest_vehicle = None
        self._encoder_history.clear()

    def _update_device_tracking(
        self,
        device_id: str,
        device_type: str,
        boot_id: str,
        sequence_number: int,
        uptime_seconds: Optional[float] = None,
        wifi_rssi_dbm: Optional[int] = None,
        firmware_version: Optional[str] = None,
    ) -> bool:
        """Process monotonic sequence number and boot session continuity.

        Returns True if packet is accepted as normal sequence progression,
        False if detected as duplicate or out-of-order.
        """
        now_mono = time.monotonic()
        now_wall = time.time()
        is_normal_sequence = True

        if device_id not in self._devices:
            # First time seeing this device
            logger.info(
                "Registered new telemetry device: %s (%s, boot_id: %s, initial_seq: %d)",
                device_id,
                device_type,
                boot_id,
                sequence_number,
            )
            self._devices[device_id] = DeviceRecord(
                device_id=device_id,
                device_type=device_type,
                boot_id=boot_id,
                last_sequence_number=sequence_number,
                last_seen_monotonic=now_mono,
                last_seen_wall=now_wall,
                uptime_seconds=uptime_seconds,
                wifi_rssi_dbm=wifi_rssi_dbm,
                firmware_version=firmware_version,
                reboot_count=0,
                duplicate_packets_count=0,
                total_packets_count=1,
            )
            return True

        record = self._devices[device_id]

        # 1. Boot ID comparison for reboot detection
        if boot_id != record.boot_id:
            logger.warning(
                "Reboot detected for device %s (prior boot_id: %s, new boot_id: %s)",
                device_id,
                record.boot_id,
                boot_id,
            )
            record.boot_id = boot_id
            record.reboot_count += 1
            record.last_sequence_number = sequence_number
        else:
            # 2. Monotonic sequence check within same boot session
            if sequence_number <= record.last_sequence_number:
                logger.warning(
                    "Duplicate or out-of-order sequence %d <= %d for device %s",
                    sequence_number,
                    record.last_sequence_number,
                    device_id,
                )
                record.duplicate_packets_count += 1
                is_normal_sequence = False
            else:
                record.last_sequence_number = sequence_number

        record.last_seen_monotonic = now_mono
        record.last_seen_wall = now_wall
        record.total_packets_count += 1
        if uptime_seconds is not None:
            record.uptime_seconds = uptime_seconds
        if wifi_rssi_dbm is not None:
            record.wifi_rssi_dbm = wifi_rssi_dbm
        if firmware_version is not None:
            record.firmware_version = firmware_version

        return is_normal_sequence

    def get_device_status(self, device_id: str) -> ConnectionStatus:
        """Evaluate the connection status of an individual device based on elapsed time."""
        if device_id not in self._devices:
            return ConnectionStatus.DISCONNECTED

        record = self._devices[device_id]
        elapsed = time.monotonic() - record.last_seen_monotonic

        if elapsed <= self.settings.TELEMETRY_STALE_TIMEOUT_SECONDS:
            return ConnectionStatus.CONNECTED
        elif elapsed <= self.settings.HEARTBEAT_TIMEOUT_SECONDS:
            return ConnectionStatus.STALE
        return ConnectionStatus.DISCONNECTED

    def get_hardware_overall_status(self) -> ConnectionStatus:
        """Evaluate aggregate hardware link status across all known microcontrollers."""
        if not self._devices:
            return ConnectionStatus.DISCONNECTED

        has_connected = False
        has_stale = False

        for device_id in self._devices:
            status = self.get_device_status(device_id)
            if status == ConnectionStatus.CONNECTED:
                has_connected = True
                break
            elif status == ConnectionStatus.STALE:
                has_stale = True

        if has_connected:
            return ConnectionStatus.CONNECTED
        if has_stale:
            return ConnectionStatus.STALE
        return ConnectionStatus.DISCONNECTED

    def record_encoder(self, data: EncoderTelemetryIngest) -> EncoderTelemetryResponse:
        """Record rotary encoder telemetry from ESP32."""
        self._update_device_tracking(
            device_id=data.device_id,
            device_type=DeviceType.ESP32_WROOM.value,
            boot_id=data.boot_id,
            sequence_number=data.sequence_number,
        )

        ts = data.timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        response = EncoderTelemetryResponse(
            left_ticks=data.left_ticks,
            right_ticks=data.right_ticks,
            left_rpm=data.left_rpm,
            right_rpm=data.right_rpm,
            estimated_distance_meters=data.estimated_distance_meters,
            speed_mps=data.speed_mps,
            direction=data.direction,
            timestamp=ts,
        )
        self._latest_encoder = response

        # Record in bounded timestamped odometry history for optical localization
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            self._encoder_history.append((dt.astimezone(timezone.utc), response))
        except Exception:
            pass

        return response

    def get_encoder_at_timestamp(
        self, target_dt: datetime, max_delta_seconds: float = 0.5
    ) -> Optional[EncoderTelemetryResponse]:
        """Find nearest encoder odometry sample within max_delta_seconds tolerance."""
        if not self._encoder_history:
            return None

        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=timezone.utc)
        target_utc = target_dt.astimezone(timezone.utc)

        best_sample = None
        min_delta = float("inf")

        for sample_dt, encoder_resp in self._encoder_history:
            delta = abs((sample_dt - target_utc).total_seconds())
            if delta < min_delta:
                min_delta = delta
                best_sample = encoder_resp

        if min_delta <= max_delta_seconds:
            return best_sample
        return None

    def record_imu(self, data: IMUTelemetryIngest) -> IMUTelemetryResponse:
        """Record MPU6050 inertial telemetry from ESP32."""
        self._update_device_tracking(
            device_id=data.device_id,
            device_type=DeviceType.ESP32_WROOM.value,
            boot_id=data.boot_id,
            sequence_number=data.sequence_number,
        )

        ts = data.timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        response = IMUTelemetryResponse(
            accel_x=data.accel_x,
            accel_y=data.accel_y,
            accel_z=data.accel_z,
            gyro_x=data.gyro_x,
            gyro_y=data.gyro_y,
            gyro_z=data.gyro_z,
            pitch_degrees=data.pitch_deg,
            roll_degrees=data.roll_deg,
            yaw_degrees=data.yaw_deg,
            temperature_c=data.temperature_c,
            timestamp=ts,
        )
        self._latest_imu = response
        return response

    def record_vehicle_status(self, data: VehicleStatusIngest) -> VehicleTelemetryResponse:
        """Record vehicle power, actuator status and safety indicators."""
        self._update_device_tracking(
            device_id=data.device_id,
            device_type=DeviceType.ESP32_WROOM.value,
            boot_id=data.boot_id,
            sequence_number=data.sequence_number,
        )

        ts = data.timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        response = VehicleTelemetryResponse(
            controller_state=data.controller_state,
            motor_driver_state=data.motor_driver_state,
            left_motor_state=data.left_motor_state,
            right_motor_state=data.right_motor_state,
            emergency_stop_engaged=data.emergency_stop_engaged,
            command_ack_state=data.command_ack_state,
            battery_voltage=data.battery_voltage,
            battery_percent=data.battery_percent,
            current_draw_amperes=data.current_draw_amperes,
            last_command_timestamp=ts if data.command_ack_state != "idle" else None,
            operating_state=data.operating_state or "normal",
            timestamp=ts,
        )
        self._latest_vehicle = response
        return response

    def record_heartbeat(self, data: HeartbeatIngest) -> DeviceStatusDetail:
        """Record periodic device diagnostic heartbeat."""
        self._update_device_tracking(
            device_id=data.device_id,
            device_type=data.device_type.value,
            boot_id=data.boot_id,
            sequence_number=data.sequence_number,
            uptime_seconds=data.uptime_seconds,
            wifi_rssi_dbm=data.wifi_rssi_dbm,
            firmware_version=data.firmware_version,
        )

        record = self._devices[data.device_id]
        status = self.get_device_status(data.device_id)
        elapsed = time.monotonic() - record.last_seen_monotonic

        return DeviceStatusDetail(
            device_id=data.device_id,
            device_type=data.device_type.value,
            connection_status=status.value,
            boot_id=record.boot_id,
            last_sequence_number=record.last_sequence_number,
            last_seen_seconds_ago=round(elapsed, 2),
            uptime_seconds=record.uptime_seconds,
            wifi_rssi_dbm=record.wifi_rssi_dbm,
            firmware_version=record.firmware_version,
            reboot_count=record.reboot_count,
            duplicate_packets_count=record.duplicate_packets_count,
            total_packets_count=record.total_packets_count,
        )

    def get_latest_telemetry(self) -> LatestTelemetryResponse:
        """Return latest cached telemetry snapshot, or disconnected defaults if none."""
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        encoder = self._latest_encoder if self._latest_encoder is not None else EncoderTelemetryResponse()
        imu = self._latest_imu if self._latest_imu is not None else IMUTelemetryResponse()
        vehicle = (
            self._latest_vehicle
            if self._latest_vehicle is not None
            else VehicleTelemetryResponse(
                controller_state="disconnected",
                motor_driver_state="disconnected",
                left_motor_state="offline",
                right_motor_state="offline",
                operating_state="offline",
            )
        )

        return LatestTelemetryResponse(
            encoder=encoder,
            imu=imu,
            vehicle=vehicle,
            timestamp=now_utc,
        )

    def get_telemetry_status(self, active_ws_count: int = 0) -> TelemetryStatusResponse:
        """Return comprehensive connection status for all registered devices."""
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        now_mono = time.monotonic()
        overall = self.get_hardware_overall_status()

        devices_map: Dict[str, DeviceStatusDetail] = {}
        for dev_id, record in self._devices.items():
            status = self.get_device_status(dev_id)
            elapsed = now_mono - record.last_seen_monotonic
            devices_map[dev_id] = DeviceStatusDetail(
                device_id=dev_id,
                device_type=record.device_type,
                connection_status=status.value,
                boot_id=record.boot_id,
                last_sequence_number=record.last_sequence_number,
                last_seen_seconds_ago=round(elapsed, 2),
                uptime_seconds=record.uptime_seconds,
                wifi_rssi_dbm=record.wifi_rssi_dbm,
                firmware_version=record.firmware_version,
                reboot_count=record.reboot_count,
                duplicate_packets_count=record.duplicate_packets_count,
                total_packets_count=record.total_packets_count,
            )

        return TelemetryStatusResponse(
            overall_status=overall.value,
            devices=devices_map,
            active_ws_connections=active_ws_count,
            timestamp=now_utc,
        )


# Global Telemetry State Service Singleton
telemetry_state_service = TelemetryStateService()

