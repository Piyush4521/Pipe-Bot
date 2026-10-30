"""Pydantic Schemas for Health, Readiness, and System Status Endpoints."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """General service identification and operational health schema."""

    name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application semantic version")
    status: str = Field("healthy", description="Current overall operational status")
    environment: str = Field(..., description="Runtime environment: development | staging | production")
    timestamp: str = Field(..., description="Current server UTC timestamp in ISO 8601 format")


class ReadinessResponse(BaseModel):
    """Readiness probe schema verifying backend readiness to serve operator traffic."""

    status: str = Field(..., description="Readiness state: ready | not_ready")
    database: bool = Field(..., description="Database connection health boolean")
    timestamp: str = Field(..., description="Evaluation timestamp in ISO 8601 format")
    details: Optional[str] = Field(None, description="Diagnostic details or error reason")


class DatabaseHealthResponse(BaseModel):
    """Database connectivity and roundtrip verification schema."""

    status: str = Field(..., description="Connection status: connected | disconnected")
    database_type: str = Field("sqlite", description="Underlying database engine")
    response_time_ms: float = Field(..., description="Ping latency in milliseconds")
    timestamp: str = Field(..., description="Evaluation timestamp in ISO 8601 format")


class SubsystemDetail(BaseModel):
    """Granular state report for an individual hardware or software subsystem."""

    state: str = Field(..., description="Subsystem connection state: connected | disconnected | not_initialized | error")
    message: str = Field(..., description="Descriptive status note")


class SystemStatusResponse(BaseModel):
    """Subsystem connectivity matrix directly compatible with PipeBot frontend contract."""

    # Top-level properties corresponding directly to frontend SystemConnectionStatus
    backend: str = Field("connected", description="Backend service connection state")
    database: str = Field("connected", description="Database service connection state")
    hardware: str = Field("disconnected", description="Robotic vehicle microcontroller state")
    camera: str = Field("disconnected", description="Camera stream connection state")
    aiProcessing: str = Field("not_initialized", description="AI defect detection engine state")
    lastHeartbeatTimestamp: str = Field(..., description="Last verified heartbeat timestamp (ISO 8601 UTC)")

    # Detailed subsystems mapping
    subsystems: Dict[str, SubsystemDetail] = Field(
        ...,
        description="Comprehensive subsystem status breakdown for hardware and services",
    )

