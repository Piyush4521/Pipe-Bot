"""Hardware Device and Session SQLAlchemy Models.

Manages hardware registry, connection sessions per boot cycle, diagnostic heartbeats,
and vehicle actuation state events.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.inspection import Inspection


class Device(Base):
    """Master hardware registry of crawler microcontrollers and camera modules."""

    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="Unique hardware identifier string (e.g. esp32-crawler-wroom)",
    )
    device_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Hardware class: ESP32_WROOM, ESP32_CAM, PROCESSING_SERVER",
    )
    mac_address: Mapped[Optional[str]] = mapped_column(
        String(32),
        unique=True,
        nullable=True,
        comment="Physical MAC address of network interface",
    )
    firmware_version: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        comment="Semantic firmware version string",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether device is authorized for field operation",
    )
    created_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Device registration timestamp",
    )

    # Relationships
    sessions: Mapped[List["DeviceSession"]] = relationship(
        "DeviceSession",
        back_populates="device",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Device(id='{self.id}', type='{self.device_type}', active={self.is_active})>"


class DeviceSession(Base):
    """Tracks continuous connection sessions per device boot cycle."""

    __tablename__ = "device_sessions"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    session_uuid: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="Public session UUID identifier",
    )
    device_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("devices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing physical device",
    )
    inspection_id: Mapped[Optional[int]] = mapped_column(
        BigIntId,
        ForeignKey("inspections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Associated active inspection session (nullable if idle)",
    )
    boot_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Monotonic boot identifier from MCU startup",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Client IP address",
    )
    connected_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="UTC connection timestamp",
    )
    disconnected_at: Mapped[Optional[datetime]] = mapped_column(
        UtcDateTime,
        nullable=True,
        comment="UTC disconnect timestamp",
    )
    disconnect_reason: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        comment="Reason for session closure",
    )

    # Relationships
    device: Mapped["Device"] = relationship(
        "Device",
        back_populates="sessions",
    )
    inspection: Mapped[Optional["Inspection"]] = relationship(
        "Inspection",
        back_populates="device_sessions",
    )
    heartbeats: Mapped[List["DeviceHeartbeat"]] = relationship(
        "DeviceHeartbeat",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DeviceSession(id={self.id}, device='{self.device_id}', boot_id='{self.boot_id}')>"


class DeviceHeartbeat(Base):
    """Periodic diagnostic health pulse monitoring battery, signal strength, and heap memory."""

    __tablename__ = "device_heartbeats"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    session_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("device_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent device connection session",
    )
    device_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("devices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing physical device",
    )
    rssi_dbm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="WiFi received signal strength indication in dBm",
    )
    battery_millivolts: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="DC battery potential in millivolts",
    )
    battery_percent: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Computed battery percentage (0.0 to 100.0)",
    )
    free_heap_bytes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Free heap memory bytes on MCU",
    )
    uptime_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Reported device uptime in seconds",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="UTC server receipt timestamp",
    )

    # Relationships
    session: Mapped["DeviceSession"] = relationship(
        "DeviceSession",
        back_populates="heartbeats",
    )

    def __repr__(self) -> str:
        return f"<DeviceHeartbeat(id={self.id}, device='{self.device_id}', rssi={self.rssi_dbm})>"


class VehicleStatusEvent(Base):
    """Event log recording discrete motor actuation states, drive modes, and emergency stops."""

    __tablename__ = "vehicle_status_events"

    id: Mapped[int] = mapped_column(
        BigIntId,
        primary_key=True,
        autoincrement=True,
    )
    inspection_id: Mapped[int] = mapped_column(
        BigIntId,
        ForeignKey("inspections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign key referencing parent inspection session",
    )
    session_id: Mapped[Optional[int]] = mapped_column(
        BigIntId,
        ForeignKey("device_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Foreign key referencing active device session",
    )
    drive_mode: Mapped[str] = mapped_column(
        String(32),
        default="manual",
        nullable=False,
        comment="Operational mode: manual, autonomous, reverse, estop",
    )
    left_motor_state: Mapped[str] = mapped_column(
        String(32),
        default="idle",
        nullable=False,
        comment="Left motor actuation state: idle, forward, reverse, offline",
    )
    right_motor_state: Mapped[str] = mapped_column(
        String(32),
        default="idle",
        nullable=False,
        comment="Right motor actuation state: idle, forward, reverse, offline",
    )
    emergency_stop: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Emergency stop hardware status flag",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="UTC timestamp of event recording",
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="vehicle_events",
    )

    def __repr__(self) -> str:
        return f"<VehicleStatusEvent(id={self.id}, mode='{self.drive_mode}', estop={self.emergency_stop})>"

