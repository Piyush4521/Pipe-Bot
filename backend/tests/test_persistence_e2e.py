"""End-to-End Persistence and Transactional Reliability Test Suite.

Verifies end-to-end multi-table persistence workflows: inspection lifecycle,
device registration, telemetry batch ingestion, camera frame tracking,
AI model provenance, defect localization, evidence media registration,
analytical summary generation, compliance reports, audit logging,
and transaction rollback atomicity. All tests run in isolated temporary SQLite databases.
"""

from datetime import datetime, timezone
from pathlib import Path
import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import transaction_scope
from app.models import (
    AIModelVersion,
    AuditEvent,
    CameraFrame,
    Defect,
    DefectClass,
    DefectReviewStatus,
    Device,
    DeviceHeartbeat,
    DeviceSession,
    EncoderSample,
    EvidenceMedia,
    IMUSample,
    Inspection,
    InspectionEvent,
    InspectionReport,
    InspectionStatus,
    InspectionSummary,
    LocalizationRecord,
    VehicleStatusEvent,
)
from app.repositories import (
    AIModelRepository,
    AuditRepository,
    DefectRepository,
    InspectionRepository,
    MediaRepository,
    ReportRepository,
    TelemetryRepository,
)


@pytest.fixture
def e2e_db(tmp_path: Path):
    """Fixture providing a fresh isolated database and repository suite."""
    db_file = tmp_path / "persistence_e2e.db"
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    with session_factory() as session:
        yield session

    engine.dispose()


def test_complete_inspection_lifecycle_and_telemetry_workflow(e2e_db: Session):
    """Test full multi-domain workflow from robot boot to compliance report generation."""
    insp_repo = InspectionRepository(e2e_db)
    defect_repo = DefectRepository(e2e_db)
    telem_repo = TelemetryRepository(e2e_db)
    media_repo = MediaRepository(e2e_db)
    model_repo = AIModelRepository(e2e_db)
    report_repo = ReportRepository(e2e_db)
    audit_repo = AuditRepository(e2e_db)

    # 1. Device Registration and Boot Session
    device = telem_repo.get_or_create_device(
        device_id="esp32-crawler-01",
        device_type="ESP32_WROOM",
        mac_address="24:6F:28:AB:CD:EF",
        firmware_version="1.2.0",
    )
    assert device.id == "esp32-crawler-01"

    session_record = telem_repo.create_device_session(
        session_uuid="sess-uuid-001",
        device_id=device.id,
        boot_id="boot-001",
    )
    assert session_record.device_id == "esp32-crawler-01"

    heartbeat = telem_repo.record_heartbeat(
        session_id=session_record.id,
        device_id=device.id,
        battery_millivolts=12400,
        battery_percent=95.0,
        rssi_dbm=-58,
    )
    assert heartbeat.battery_millivolts == 12400

    # 2. Inspection Initialization
    insp_obj = Inspection(
        inspection_id="INSP-E2E-20261030-01",
        pipe_identifier="PVC-MAIN-400",
        pipe_material="PVC",
        pipe_diameter_mm=400,
        operator_id="TECH-882",
        status=InspectionStatus.CREATED,
    )
    inspection = insp_repo.create(insp_obj)
    assert inspection.status == InspectionStatus.CREATED
    assert inspection.is_archived is False

    # Transition to in_progress
    inspection.status = InspectionStatus.IN_PROGRESS
    inspection.started_at = datetime.now(timezone.utc)
    inspection = insp_repo.update(inspection)
    assert inspection.status == InspectionStatus.IN_PROGRESS
    assert inspection.started_at is not None

    insp_repo.record_event(
        inspection_id=inspection.id,
        event_type="INSPECTION_STARTED",
        payload={"operator": "TECH-882", "target": "PVC-MAIN-400"},
    )

    # 3. Batch Telemetry Streaming
    encoder_samples = []
    imu_samples = []
    now_utc = datetime.now(timezone.utc)

    for i in range(25):
        encoder_samples.append(
            EncoderSample(
                inspection_id=inspection.id,
                session_id=session_record.id,
                sequence_number=i + 1,
                left_ticks=i * 10,
                right_ticks=i * 10,
                speed_mps=0.15,
                direction="forward",
                recorded_at=now_utc,
            )
        )
        imu_samples.append(
            IMUSample(
                inspection_id=inspection.id,
                session_id=session_record.id,
                sequence_number=i + 1,
                accel_x=0.01,
                accel_y=0.02,
                accel_z=9.81,
                gyro_x=0.0,
                gyro_y=0.0,
                gyro_z=0.1,
                pitch_deg=1.2,
                roll_deg=-0.5,
                yaw_deg=0.3,
                recorded_at=now_utc,
            )
        )

    inserted_enc = telem_repo.insert_encoder_samples_batch(encoder_samples)
    inserted_imu = telem_repo.insert_imu_samples_batch(imu_samples)
    assert inserted_enc == 25
    assert inserted_imu == 25

    # 4. Camera Frame Metadata and AI Model Registration
    model = model_repo.register_model_version(
        model_name="yolov8n-pipebot",
        model_version="v1.0.0-baseline",
        artifact_path="weights/yolov8n-pipebot-v1.0.0.pt",
        artifact_checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        class_mapping={"0": "Deformation", "1": "Misalignment", "2": "Obstacle", "3": "Rupture"},
        input_dimensions="640x640",
        confidence_threshold=0.25,
        is_active=True,
    )
    assert model.is_active is True

    frame = media_repo.record_camera_frame(
        frame_id="FRAME-E2E-001",
        inspection_id=inspection.id,
        frame_width=640,
        frame_height=480,
        frame_bytes=42500,
        camera_id="esp32-cam-front",
        frame_sequence=1,
        capture_timestamp=now_utc,
    )
    assert frame.id is not None

    # 5. Defect Detection with Localization and Evidence Media
    defect_obj = Defect(
        defect_id="DEF-E2E-001",
        inspection_id=inspection.id,
        frame_id=frame.frame_id,
        defect_class=DefectClass.RUPTURE,
        confidence=0.94,
        capture_timestamp=now_utc,
        estimated_distance_meters=2.4,
        review_status=DefectReviewStatus.CONFIRMED,
        bounding_box={"x": 120, "y": 80, "width": 150, "height": 90},
    )
    defect = defect_repo.create(defect_obj)
    assert defect.id is not None
    assert defect.defect_class == DefectClass.RUPTURE

    loc = defect_repo.attach_localization(
        defect_id=defect.id,
        frame_id=frame.frame_id,
        frame_capture_timestamp=now_utc,
        encoder_sample_timestamp=now_utc,
        temporal_delta_ms=12.5,
        clock_sync_status="UNVERIFIED_SYNC",
        left_encoder_ticks=240,
        right_encoder_ticks=240,
        computed_distance_meters=2.4,
    )
    assert loc.defect_id == defect.id
    assert loc.computed_distance_meters == 2.4
    assert loc.clock_sync_status == "UNVERIFIED_SYNC"

    evidence = media_repo.record_evidence(
        media_uuid="media-uuid-def-001",
        defect_id=defect.id,
        file_path="crops/insp_1/def_1.jpg",
        mime_type="image/jpeg",
        file_size_bytes=8192,
        checksum_sha256="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    )
    assert evidence.defect_id == defect.id

    # 6. Inspection Completion and Analytical Summary Refresh
    inspection.status = InspectionStatus.COMPLETED
    inspection.completed_at = datetime.now(timezone.utc)
    inspection.total_distance_meters = 2.5
    inspection = insp_repo.update(inspection)
    assert inspection.status == InspectionStatus.COMPLETED

    summary = insp_repo.refresh_summary(inspection.id)
    assert summary.inspection_id == inspection.id
    assert summary.total_defects_count == 1
    assert summary.rupture_count == 1
    assert summary.overall_pipe_grade in ["A", "B", "C", "D", "FAIL"]

    # 7. Compliance Report Generation
    report = report_repo.create_report(
        report_id="REP-20261030-001",
        inspection_id=inspection.id,
        report_type="FULL_COMPLIANCE",
        report_format="PDF",
        file_path="reports/insp_1/compliance_report.pdf",
        file_size_bytes=104800,
        checksum_sha256="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        overall_rating=summary.overall_pipe_grade,
        generated_by="TECH-882",
    )
    assert report.report_id == "REP-20261030-001"

    # 8. Append-Only Audit Logging
    audit_event = audit_repo.log_event(
        entity_type="INSPECTION",
        entity_id=inspection.inspection_id,
        action="COMPLETE",
        performed_by="TECH-882",
        before_state={"status": "in_progress"},
        after_state={"status": "completed", "total_defects": 1},
        client_ip="192.168.1.105",
    )
    assert audit_event.id is not None
    assert audit_event.action == "COMPLETE"


def test_transaction_rollback_preserves_atomicity(e2e_db: Session):
    """Verify that multi-step operations cleanly rollback on failure, leaving zero orphan rows."""
    insp_repo = InspectionRepository(e2e_db)

    # Pre-condition: count inspections
    initial_count = len(insp_repo.list_inspections(include_archived=True))

    with pytest.raises(RuntimeError, match="Simulated operational failure during transaction"):
        with transaction_scope(e2e_db):
            # Step 1: Create an inspection
            insp = Inspection(
                inspection_id="INSP-ROLLBACK-TEST",
                pipe_identifier="PVC-TEST-ROLLBACK",
                pipe_material="PVC",
                pipe_diameter_mm=200,
                operator_id="TECH-TEST",
                status=InspectionStatus.CREATED,
            )
            e2e_db.add(insp)
            e2e_db.flush()

            # Step 2: Simulate failure before transaction commits
            raise RuntimeError("Simulated operational failure during transaction")

    # Post-condition: ensure rolled-back inspection does not exist
    current_count = len(insp_repo.list_inspections(include_archived=True))
    assert current_count == initial_count

    found = insp_repo.get_by_inspection_id("INSP-ROLLBACK-TEST")
    assert found is None
