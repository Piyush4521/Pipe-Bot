"""Automated Test Suite for UTC Timestamp Normalization, Serialization, and Semantics."""

from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.defect import Defect, DefectClass
from app.models.inspection import Inspection, InspectionStatus
from app.schemas.defect import normalize_datetime_to_utc, format_datetime_iso_utc


def test_offset_aware_timestamp_produces_exact_utc_instant():
    """Verify that an offset-aware timestamp (+05:30) is correctly normalized to UTC.

    Example: 2026-10-30T21:00:00+05:30 is identically 2026-10-30T15:30:00Z.
    """
    input_str = "2026-10-30T21:00:00+05:30"
    normalized = normalize_datetime_to_utc(input_str)

    assert normalized is not None
    assert normalized.tzinfo == timezone.utc
    assert normalized.year == 2026
    assert normalized.month == 10
    assert normalized.day == 30
    assert normalized.hour == 15
    assert normalized.minute == 30
    assert normalized.second == 0

    # Serialization must end with 'Z'
    serialized = format_datetime_iso_utc(normalized)
    assert serialized == "2026-10-30T15:30:00Z"


def test_naive_timestamp_policy_interprets_as_utc():
    """Verify documented policy: naive timestamps without offset are explicitly assigned UTC."""
    input_naive = "2026-10-30T14:15:30"
    normalized = normalize_datetime_to_utc(input_naive)

    assert normalized is not None
    assert normalized.tzinfo == timezone.utc
    assert normalized.hour == 14
    assert normalized.minute == 15
    assert normalized.second == 30

    serialized = format_datetime_iso_utc(normalized)
    assert serialized == "2026-10-30T14:15:30Z"


def test_utc_datetime_type_decorator_database_persistence(db_session: Session):
    """Verify that SQLite UtcDateTime TypeDecorator ensures tzinfo=timezone.utc on read."""
    inspection = Inspection(
        inspection_id="INSP-TZ-TEST-001",
        pipe_identifier="PVC-TZ",
        operator_id="TECH-TZ",
        status=InspectionStatus.CREATED,
        started_at=datetime(2026, 10, 30, 16, 45, 0, tzinfo=timezone.utc),
    )
    db_session.add(inspection)
    db_session.commit()
    db_session.refresh(inspection)

    # Reload from fresh query
    reloaded = db_session.query(Inspection).filter_by(inspection_id="INSP-TZ-TEST-001").first()
    assert reloaded is not None
    assert reloaded.started_at is not None
    assert reloaded.started_at.tzinfo == timezone.utc
    assert reloaded.started_at.hour == 16
    assert reloaded.created_at.tzinfo == timezone.utc
    assert reloaded.updated_at.tzinfo == timezone.utc


def test_api_timestamp_serialization_is_consistent_iso_utc(client: TestClient):
    """Verify that all API response timestamps serialize consistently with ISO 8601 'Z' suffix."""
    create_insp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-SERIALIZE-01", "operatorId": "TECH-SER"},
    )
    assert create_insp.status_code == 201
    insp_data = create_insp.json()
    insp_id = insp_data["inspectionId"]

    # Verify createdAt and updatedAt end with Z
    assert insp_data["createdAt"].endswith("Z")
    assert insp_data["updatedAt"].endswith("Z")

    # Start inspection to populate startedAt
    start_resp = client.post(f"/api/v1/inspections/{insp_id}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["startedAt"].endswith("Z")

    # Complete inspection to populate completedAt
    comp_resp = client.post(f"/api/v1/inspections/{insp_id}/complete")
    assert comp_resp.status_code == 200
    assert comp_resp.json()["completedAt"].endswith("Z")


def test_frame_capture_timestamp_alias_and_normalization_in_api(client: TestClient):
    """Verify that defect endpoint accepts frameCaptureTimestamp and normalizes offsets."""
    create_insp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-OFFSET-TEST", "operatorId": "TECH-OFFSET"},
    )
    insp_id = create_insp.json()["inspectionId"]

    # Supply frameCaptureTimestamp with +02:00 offset (e.g. 17:00:00+02:00 -> 15:00:00Z)
    defect_payload = {
        "inspectionId": insp_id,
        "frameId": "FRAME-TZ-001",
        "defectClass": "rupture",
        "confidence": 0.91,
        "frameCaptureTimestamp": "2026-10-30T17:00:00+02:00",
        "inferenceTimestamp": "2026-10-30T17:00:01+02:00",
    }
    resp = client.post("/api/v1/defects", json=defect_payload)
    assert resp.status_code == 201
    data = resp.json()

    # Capture timestamp must be normalized to 15:00:00Z
    assert data["captureTimestamp"] == "2026-10-30T15:00:00Z"
    assert data["inferenceTimestamp"] == "2026-10-30T15:00:01Z"


def test_separation_of_capture_inference_and_creation_timestamps(client: TestClient):
    """Verify that capture, inference, and record creation timestamps remain distinct entities."""
    create_insp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-SEPARATE-TEST", "operatorId": "TECH-SEP"},
    )
    insp_id = create_insp.json()["inspectionId"]

    capture_time = "2026-10-30T10:00:00Z"
    inference_time = "2026-10-30T10:00:02Z"

    resp = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-SEP-01",
            "defectClass": "misalignment",
            "captureTimestamp": capture_time,
            "inferenceTimestamp": inference_time,
        },
    )
    assert resp.status_code == 201
    data = resp.json()

    assert data["captureTimestamp"] == "2026-10-30T10:00:00Z"
    assert data["inferenceTimestamp"] == "2026-10-30T10:00:02Z"
    # createdAt is generated by backend at insertion time, so it is strictly later than 10:00:00Z
    assert data["createdAt"] != data["captureTimestamp"]
    assert data["createdAt"] != data["inferenceTimestamp"]

