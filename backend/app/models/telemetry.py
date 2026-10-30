"""Rotary Encoder and Inertial Measurement Telemetry SQLAlchemy Models.

Manages high-frequency time-series streams for wheel odometry and MPU6050 6-axis motion.
Raw sensor measurements are preserved as non-null requirements, while derived or calibrated
values remain strictly nullable.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigIntId, UtcDateTime

if TYPE_CHECKING:
    from app.models.inspection import Inspection


class EncoderSample(Base):
    """High-frequency dual-wheel rotary encoder telemetry sample."""

    __tablename__ = "encoder_samples"

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
    sequence_number: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=False,
        comment="Monotonic packet counter from microcontroller boot",
    )
    left_ticks: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=False,
        comment="Raw cumulative pulse count from left motor encoder",
    )
    right_ticks: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=False,
        comment="Raw cumulative pulse count from right motor encoder",
    )
    left_rpm: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Rotational velocity of left wheel in RPM (derived/uncalibrated)",
    )
    right_rpm: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Rotational velocity of right wheel in RPM (derived/uncalibrated)",
    )
    speed_mps: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Forward linear speed in meters per second (derived)",
    )
    direction: Mapped[Optional[str]] = mapped_column(
        String(16),
        default="forward",
        nullable=True,
        comment="Physical drive direction: forward, reverse, stopped",
    )
    device_uptime_ms: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=True,
        comment="Milliseconds since microcontroller boot",
    )
    device_timestamp: Mapped[Optional[datetime]] = mapped_column(
        UtcDateTime,
        nullable=True,
        comment="Microcontroller hardware RTC timestamp if configured",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="UTC server arrival timestamp",
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="encoder_samples",
    )

    def __repr__(self) -> str:
        return f"<EncoderSample(id={self.id}, seq={self.sequence_number}, left={self.left_ticks}, right={self.right_ticks})>"


class IMUSample(Base):
    """High-frequency 6-axis MPU6050 inertial measurement unit telemetry sample."""

    __tablename__ = "imu_samples"

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
    sequence_number: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=False,
        comment="Monotonic packet counter from microcontroller boot",
    )
    accel_x: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Linear acceleration X-axis (raw LSB or calibrated m/s^2)",
    )
    accel_y: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Linear acceleration Y-axis (raw LSB or calibrated m/s^2)",
    )
    accel_z: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Linear acceleration Z-axis (raw LSB or calibrated m/s^2)",
    )
    gyro_x: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Angular rate X-axis (raw LSB or calibrated deg/s)",
    )
    gyro_y: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Angular rate Y-axis (raw LSB or calibrated deg/s)",
    )
    gyro_z: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Angular rate Z-axis (raw LSB or calibrated deg/s)",
    )
    pitch_deg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Computed pitch inclination angle in degrees (derived)",
    )
    roll_deg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Computed roll inclination angle in degrees (derived)",
    )
    yaw_deg: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Computed heading angle in degrees (derived)",
    )
    temperature_c: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Internal sensor die temperature in Celsius",
    )
    sensor_units: Mapped[str] = mapped_column(
        String(32),
        default="raw_lsb",
        nullable=False,
        comment="Physical units format: raw_lsb, si_mps2_degs",
    )
    device_uptime_ms: Mapped[Optional[int]] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        nullable=True,
        comment="Milliseconds since microcontroller boot",
    )
    device_timestamp: Mapped[Optional[datetime]] = mapped_column(
        UtcDateTime,
        nullable=True,
        comment="Microcontroller hardware RTC timestamp if configured",
    )
    recorded_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="UTC server arrival timestamp",
    )

    # Relationships
    inspection: Mapped["Inspection"] = relationship(
        "Inspection",
        back_populates="imu_samples",
    )

    def __repr__(self) -> str:
        return f"<IMUSample(id={self.id}, seq={self.sequence_number}, units='{self.sensor_units}')>"

