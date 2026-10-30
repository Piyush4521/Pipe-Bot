"""SQLAlchemy Repository for Real-Time Telemetry and Hardware State.

Manages persistence and time-range queries for rotary encoders, MPU6050 IMU,
hardware devices, boot sessions, heartbeats, and vehicle actuation states.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.device import Device, DeviceHeartbeat, DeviceSession, VehicleStatusEvent
from app.models.telemetry import EncoderSample, IMUSample


class TelemetryRepository:
    """Repository managing telemetry time-series and hardware state persistence."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # Device & Session Operations
    def get_or_create_device(
        self,
        device_id: str,
        device_type: str,
        mac_address: Optional[str] = None,
        firmware_version: Optional[str] = None,
    ) -> Device:
        """Fetch existing hardware device or register a new one."""
        device = self.db.execute(select(Device).where(Device.id == device_id)).scalar_one_or_none()
        if not device:
            device = Device(
                id=device_id,
                device_type=device_type,
                mac_address=mac_address,
                firmware_version=firmware_version,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(device)
            self.db.flush()
            self.db.refresh(device)
        return device

    def create_device_session(
        self,
        session_uuid: str,
        device_id: str,
        boot_id: str,
        inspection_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> DeviceSession:
        """Register a continuous hardware boot/connection session."""
        session_obj = DeviceSession(
            session_uuid=session_uuid,
            device_id=device_id,
            boot_id=boot_id,
            inspection_id=inspection_id,
            ip_address=ip_address,
            connected_at=datetime.now(timezone.utc),
        )
        self.db.add(session_obj)
        self.db.flush()
        self.db.refresh(session_obj)
        return session_obj

    def get_session_by_uuid(self, session_uuid: str) -> Optional[DeviceSession]:
        """Fetch device session by public session UUID."""
        stmt = select(DeviceSession).where(DeviceSession.session_uuid == session_uuid)
        return self.db.execute(stmt).scalar_one_or_none()

    def record_heartbeat(
        self,
        session_id: int,
        device_id: str,
        rssi_dbm: Optional[int] = None,
        battery_millivolts: Optional[int] = None,
        battery_percent: Optional[float] = None,
        free_heap_bytes: Optional[int] = None,
        uptime_seconds: Optional[float] = None,
        recorded_at: Optional[datetime] = None,
    ) -> DeviceHeartbeat:
        """Record a periodic microcontroller health and battery diagnostic pulse."""
        hb = DeviceHeartbeat(
            session_id=session_id,
            device_id=device_id,
            rssi_dbm=rssi_dbm,
            battery_millivolts=battery_millivolts,
            battery_percent=battery_percent,
            free_heap_bytes=free_heap_bytes,
            uptime_seconds=uptime_seconds,
            recorded_at=recorded_at or datetime.now(timezone.utc),
        )
        self.db.add(hb)
        self.db.flush()
        self.db.refresh(hb)
        return hb

    def record_vehicle_status(
        self,
        inspection_id: int,
        drive_mode: str = "manual",
        left_motor_state: str = "idle",
        right_motor_state: str = "idle",
        emergency_stop: bool = False,
        session_id: Optional[int] = None,
        recorded_at: Optional[datetime] = None,
    ) -> VehicleStatusEvent:
        """Record a discrete vehicle motor actuation or emergency stop event."""
        event_obj = VehicleStatusEvent(
            inspection_id=inspection_id,
            session_id=session_id,
            drive_mode=drive_mode,
            left_motor_state=left_motor_state,
            right_motor_state=right_motor_state,
            emergency_stop=emergency_stop,
            recorded_at=recorded_at or datetime.now(timezone.utc),
        )
        self.db.add(event_obj)
        self.db.flush()
        self.db.refresh(event_obj)
        return event_obj

    # Encoder Time-Series Operations
    def insert_encoder_samples_batch(self, samples: List[EncoderSample]) -> int:
        """Insert a batch of rotary encoder telemetry samples."""
        if not samples:
            return 0
        self.db.add_all(samples)
        self.db.flush()
        return len(samples)

    def get_encoder_samples_range(
        self,
        inspection_id: int,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[EncoderSample]:
        """Fetch encoder samples within a bounded UTC time slice."""
        stmt = (
            select(EncoderSample)
            .where(
                EncoderSample.inspection_id == inspection_id,
                EncoderSample.recorded_at >= start_time,
                EncoderSample.recorded_at <= end_time,
            )
            .order_by(EncoderSample.recorded_at.asc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_latest_encoder_sample(self, inspection_id: int) -> Optional[EncoderSample]:
        """Retrieve the most recent encoder telemetry sample for an inspection."""
        stmt = (
            select(EncoderSample)
            .where(EncoderSample.inspection_id == inspection_id)
            .order_by(EncoderSample.recorded_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # IMU Time-Series Operations
    def insert_imu_samples_batch(self, samples: List[IMUSample]) -> int:
        """Insert a batch of MPU6050 6-axis inertial motion samples."""
        if not samples:
            return 0
        self.db.add_all(samples)
        self.db.flush()
        return len(samples)

    def get_imu_samples_range(
        self,
        inspection_id: int,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[IMUSample]:
        """Fetch IMU motion telemetry samples within a bounded UTC time slice."""
        stmt = (
            select(IMUSample)
            .where(
                IMUSample.inspection_id == inspection_id,
                IMUSample.recorded_at >= start_time,
                IMUSample.recorded_at <= end_time,
            )
            .order_by(IMUSample.recorded_at.asc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_latest_imu_sample(self, inspection_id: int) -> Optional[IMUSample]:
        """Retrieve the most recent IMU sample for an inspection."""
        stmt = (
            select(IMUSample)
            .where(IMUSample.inspection_id == inspection_id)
            .order_by(IMUSample.recorded_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

