"""Pydantic Schemas for Defect Detections.

Defines input validation, review updates, bounding box models, and serialized responses
for pipeline anomaly detections with strict UTC timestamp handling.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator
from pydantic.alias_generators import to_camel

from app.models.defect import DefectClass, DefectReviewStatus


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
    return utc_dt.isoformat().replace("+00:00", "Z")


class BoundingBoxSchema(BaseModel):
    """Bounding box coordinates for detected defect anomalies.

    Coordinate Convention:
    - Origin (x, y) represents top-left bounding box corner.
    - Coordinates are stored as floats representing either normalized fraction (0.0 to 1.0)
      relative to frame resolution or absolute pixel dimensions.
    """

    x: float = Field(..., description="Top-left origin X coordinate")
    y: float = Field(..., description="Top-left origin Y coordinate")
    width: float = Field(..., gt=0.0, description="Bounding box horizontal width")
    height: float = Field(..., gt=0.0, description="Bounding box vertical height")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def convert_min_max_box(cls, data: Any) -> Any:
        """Support frontend BoundingBox2D format {xMin, yMin, xMax, yMax} seamlessly."""
        if isinstance(data, dict):
            if "xMin" in data and "xMax" in data and "yMin" in data and "yMax" in data:
                x_min = float(data["xMin"])
                x_max = float(data["xMax"])
                y_min = float(data["yMin"])
                y_max = float(data["yMax"])
                return {
                    "x": x_min,
                    "y": y_min,
                    "width": max(0.001, x_max - x_min),
                    "height": max(0.001, y_max - y_min),
                }
        return data


class DefectBase(BaseModel):
    """Base schema for pipeline defect anomaly detections."""

    frame_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Camera optical frame identifier (e.g. FRAME-000412)",
        examples=["FRAME-000412"],
    )
    defect_class: DefectClass = Field(
        ...,
        description="Anomaly class: deformation, misalignment, obstacle, rupture",
        examples=["rupture"],
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Inference confidence score between 0.0 and 1.0 (statistical confidence, not severity)",
        examples=[0.92],
    )
    bounding_box: Optional[BoundingBoxSchema] = Field(
        default=None,
        description="Bounding box coordinates in frame",
    )
    capture_timestamp: datetime = Field(
        ...,
        validation_alias=AliasChoices(
            "capture_timestamp",
            "captureTimestamp",
            "frame_capture_timestamp",
            "frameCaptureTimestamp",
        ),
        description="Recorded frame capture timestamp from camera module (not a verified physical shutter synchronization signal)",
    )
    inference_timestamp: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp of YOLO neural network inference on server",
    )
    estimated_distance_meters: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Conduit penetration distance correlated at frame capture time; never inferred from AI timestamp",
        examples=[14.52],
    )
    snapshot_path: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "snapshot_path",
            "snapshotPath",
            "snapshot_url",
            "snapshotUrl",
        ),
        max_length=512,
        description="Relative file path or URI to stored frame snapshot",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Operator notes or review annotations",
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @field_validator("capture_timestamp", "inference_timestamp", mode="before")
    @classmethod
    def validate_utc_timestamps(cls, v: Any) -> Any:
        return normalize_datetime_to_utc(v)

    @field_validator("defect_class", mode="before")
    @classmethod
    def normalize_defect_class(cls, v: Any) -> Any:
        """Normalize defect class case-insensitively."""
        if isinstance(v, str):
            v_lower = v.strip().lower()
            return v_lower
        return v


class DefectCreate(DefectBase):
    """Schema for recording a new defect detection."""

    inspection_id: Union[int, str] = Field(
        ...,
        description="Parent inspection reference (either integer database ID or public inspection_id string)",
        examples=["INSP-20261030-001"],
    )
    defect_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Optional explicit public defect identifier. If omitted, a unique ID is generated.",
        examples=["DEF-20261030-001"],
    )


class DefectReviewUpdate(BaseModel):
    """Schema for updating operator verification review status."""

    status: DefectReviewStatus = Field(
        ...,
        description="Review status: pending, confirmed, rejected",
        examples=["confirmed"],
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Optional justification notes from operator review",
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @field_validator("status", mode="before")
    @classmethod
    def normalize_review_status(cls, v: Any) -> Any:
        """Map frontend review aliases ('verified' -> 'confirmed', 'unreviewed' -> 'pending', 'dismissed' -> 'rejected')."""
        if isinstance(v, str):
            v_clean = v.strip().lower()
            alias_map = {
                "unreviewed": "pending",
                "verified": "confirmed",
                "dismissed": "rejected",
            }
            return alias_map.get(v_clean, v_clean)
        return v


class DefectResponse(DefectBase):
    """Schema for serialized defect response."""

    id: int = Field(..., description="Internal relational database primary key")
    defect_id: str = Field(..., description="Public unique defect identifier")
    inspection_id: int = Field(..., description="Parent inspection internal ID")
    inspection_public_id: Optional[str] = Field(
        default=None,
        description="Parent inspection public identifier (e.g. INSP-20261030-001)",
    )
    review_status: DefectReviewStatus = Field(
        ...,
        description="Verification review status",
    )
    created_at: datetime = Field(..., description="Record creation timestamp in UTC")
    updated_at: datetime = Field(..., description="Record last modification timestamp in UTC")

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @field_serializer("capture_timestamp", "inference_timestamp", "created_at", "updated_at", when_used="always")
    def serialize_utc_datetime(self, v: Optional[datetime]) -> Optional[str]:
        return format_datetime_iso_utc(v)

    @model_validator(mode="before")
    @classmethod
    def populate_inspection_public_id(cls, data: Any) -> Any:
        """Extract public inspection ID from relationship if available."""
        if hasattr(data, "inspection") and data.inspection is not None:
            if hasattr(data, "__dict__"):
                data.__dict__["inspection_public_id"] = data.inspection.inspection_id
        return data


class DefectListResponse(BaseModel):
    """Paginated list response schema for defect detections."""

    items: List[DefectResponse] = Field(..., description="List of defect detections")
    total: int = Field(..., ge=0, description="Total matching detections count")
    limit: int = Field(..., ge=1, description="Page limit applied")
    offset: int = Field(..., ge=0, description="Page offset applied")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
