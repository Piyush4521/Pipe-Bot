"""Health and Subsystem Diagnostics Service.

Provides business logic for checking database connectivity, round-trip latency,
and evaluating system subsystem status without mocking hardware states.
"""

import time
from datetime import datetime, timezone
from typing import Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.camera.camera_state import camera_state
from app.core.config import get_settings
from app.schemas.health import (
    DatabaseHealthResponse,
    HealthResponse,
    ReadinessResponse,
    SubsystemDetail,
    SystemStatusResponse,
)
from app.services.telemetry_state import telemetry_state_service
from app.vision.model_registry import get_active_provider


class HealthService:
    """Service class encapsulating health and diagnostics checks."""

    @staticmethod
    def get_health() -> HealthResponse:
        """Return general application health details."""
        settings = get_settings()
        now_utc = datetime.now(timezone.utc).isoformat()
        return HealthResponse(
            name=settings.APP_NAME,
            version=settings.APP_VERSION,
            status="healthy",
            environment=settings.APP_ENV,
            timestamp=now_utc,
        )

    @staticmethod
    def check_database(db: Session) -> Tuple[bool, float, str]:
        """Execute a lightweight verification query against the active database session."""
        start_time = time.perf_counter()
        try:
            result = db.execute(text("SELECT 1")).scalar()
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if result == 1:
                return True, round(elapsed_ms, 2), "Database connection responsive"
            return False, round(elapsed_ms, 2), "Unexpected query response"
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return False, round(elapsed_ms, 2), str(exc)

    @classmethod
    def get_readiness(cls, db: Session) -> Tuple[ReadinessResponse, bool]:
        """Assess whether the service is ready to accept operator traffic."""
        is_db_connected, _, detail = cls.check_database(db)
        now_utc = datetime.now(timezone.utc).isoformat()

        if is_db_connected:
            return ReadinessResponse(
                status="ready",
                database=True,
                timestamp=now_utc,
                details=detail,
            ), True

        return ReadinessResponse(
            status="not_ready",
            database=False,
            timestamp=now_utc,
            details=f"Database check failed: {detail}",
        ), False

    @classmethod
    def get_database_health(cls, db: Session) -> DatabaseHealthResponse:
        """Return dedicated database health metrics."""
        is_db_connected, elapsed_ms, _ = cls.check_database(db)
        now_utc = datetime.now(timezone.utc).isoformat()

        return DatabaseHealthResponse(
            status="connected" if is_db_connected else "disconnected",
            database_type="sqlite",
            response_time_ms=elapsed_ms,
            timestamp=now_utc,
        )

    @classmethod
    def get_system_status(cls, db: Session) -> SystemStatusResponse:
        """Return subsystem link matrix matching frontend contract."""
        is_db_connected, _, _ = cls.check_database(db)
        now_utc = datetime.now(timezone.utc).isoformat()

        db_state = "connected" if is_db_connected else "disconnected"

        # Dynamically evaluate hardware state from active device telemetry
        hw_overall = telemetry_state_service.get_hardware_overall_status().value
        wroom_status = "disconnected"
        cam_status = "disconnected"

        for dev_id, record in telemetry_state_service._devices.items():
            st = telemetry_state_service.get_device_status(dev_id).value
            if "cam" in dev_id.lower() or record.device_type == "ESP32_CAM":
                cam_status = st
            else:
                wroom_status = st

        # Dynamically evaluate camera and AI processing states
        camera_stream_state = camera_state.status.value
        ai_provider = get_active_provider()
        ai_state = "ready" if ai_provider.is_available else "not_initialized"

        is_cam_online = cam_status == "connected" or camera_stream_state in ("streaming", "connected")

        subsystems = {
            "backend": SubsystemDetail(state="connected", message="FastAPI core service active"),
            "database": SubsystemDetail(
                state=db_state,
                message="SQLite operational" if is_db_connected else "Database offline",
            ),
            "esp32_wroom": SubsystemDetail(
                state=wroom_status,
                message="Microcontroller telemetry active" if wroom_status == "connected" else f"Microcontroller link {wroom_status}",
            ),
            "esp32_cam": SubsystemDetail(
                state=cam_status if cam_status != "disconnected" else (
                    "connected" if camera_stream_state in ("streaming", "connected") else "disconnected"
                ),
                message="Camera hardware link active" if is_cam_online else f"Camera link {cam_status}",
            ),
            "camera": SubsystemDetail(
                state=camera_stream_state,
                message="Video ingestion stream active" if camera_stream_state in ("streaming", "connected") else f"Video stream {camera_stream_state}",
            ),
            "ai_processing": SubsystemDetail(
                state=ai_state,
                message=f"YOLO vision pipeline active ({ai_provider.provider_name})" if ai_provider.is_available else "YOLO vision pipeline not initialized (no weights loaded)",
            ),
        }

        return SystemStatusResponse(
            backend="connected",
            database=db_state,
            hardware=hw_overall,
            camera="connected" if is_cam_online else "disconnected",
            aiProcessing=ai_state,
            lastHeartbeatTimestamp=now_utc,
            subsystems=subsystems,
        )

