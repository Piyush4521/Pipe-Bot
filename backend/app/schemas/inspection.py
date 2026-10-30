"""Pydantic Schemas for Inspection Sessions.

Defines input validation, update models, archival controls, and response serialization contracts
for inspection session resources.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pydantic.alias_generators import to_camel

from app.models.inspection import InspectionStatus


def normalize_datetime_to_utc(v: Any) -> Optional[datetime]:
    """Normalize incoming datetime representations to timezone-aware UTC datetime.

    Documented Policy:
    1. Offset-aware datetimes are mathematically converted to UTC.
    2. Naive datetimes without timezone offset are explicitly interpreted as UTC
       (tzinfo=timezone.utc) to prevent silent misinterpretation as local server time.
    """
    if v is None:
        return None
    if isinstance(v, str):
        parsed = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    if isinstance(v, datetime):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    return v


def format_datetime_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """Serialize datetime to standardized ISO 8601 UTC string with trailing 'Z'."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    utc_dt = dt.astimezone(timezone.utc)
    # Output format: YYYY-MM-DDTHH:MM:SS.ffffffZ
    return utc_dt.isoformat().replace("+00:00", "Z")


class InspectionBase(BaseModel):
    """Base inspection schema containing shared conduit and operator attributes."""

    pipe_identifier: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Target conduit identifier tag (e.g. PVC-MAIN-001)",
        examples=["PVC-MAIN-001"],
    )
    pipe_material: str = Field(
        default="PVC",
        max_length=64,
        description="Conduit composition: PVC, HDPE, Concrete",
        examples=["PVC"],
    )
    pipe_diameter_mm: int = Field(
        default=200,
        ge=50,
        le=1200,
        description="Inner pipe diameter in millimeters (typically 150mm - 300mm)",
        examples=[200],
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Operator or technician identifier",
        examples=["OP-TECH-042"],
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Optional field notes or inspection remarks",
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class InspectionCreate(InspectionBase):
    """Schema for creating a new inspection session."""

    inspection_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Optional explicit public identifier. If omitted, a unique identifier is generated.",
        examples=["INSP-20261030-001"],
    )


class InspectionUpdate(BaseModel):
    """Schema for updating mutable inspection metadata. Status is modified via lifecycle actions."""

    pipe_identifier: Optional[str] = Field(default=None, min_length=1, max_length=128)
    pipe_material: Optional[str] = Field(default=None, max_length=64)
    pipe_diameter_mm: Optional[int] = Field(default=None, ge=50, le=1200)
    operator_id: Optional[str] = Field(default=None, min_length=1, max_length=128)
    notes: Optional[str] = Field(default=None, max_length=4000)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class InspectionStatusUpdate(BaseModel):
    """Schema for concluding an inspection session with optional validated distance."""

    total_distance_meters: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Final encoder-derived distance measurement in meters. Null if no encoder data available.",
    )
    notes: Optional[str] = Field(default=None, max_length=4000)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class InspectionResponse(InspectionBase):
    """Schema for serialized inspection response."""

    id: int = Field(..., description="Internal relational database primary key")
    inspection_id: str = Field(..., description="Public unique inspection identifier")
    status: InspectionStatus = Field(..., description="Current lifecycle status")
    started_at: Optional[datetime] = Field(default=None, description="UTC start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="UTC completion timestamp")
    total_distance_meters: Optional[float] = Field(
        default=None,
        description="Total penetration distance in meters; null until computed from encoder pulses",
    )
    defect_count: int = Field(default=0, description="Total defect detections recorded")
    is_archived: bool = Field(default=False, description="Whether the inspection session is archived for compliance")
    created_at: datetime = Field(..., description="Record creation timestamp in UTC")
    updated_at: datetime = Field(..., description="Record last modification timestamp in UTC")

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @field_serializer("started_at", "completed_at", "created_at", "updated_at", when_used="always")
    def serialize_utc_datetime(self, v: Optional[datetime]) -> Optional[str]:
        return format_datetime_iso_utc(v)


class InspectionListResponse(BaseModel):
    """Paginated list response schema for inspections."""

    items: List[InspectionResponse] = Field(..., description="List of inspection records")
    total: int = Field(..., ge=0, description="Total matching records count")
    limit: int = Field(..., ge=1, description="Page limit applied")
    offset: int = Field(..., ge=0, description="Page offset applied")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
