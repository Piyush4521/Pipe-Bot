"""Isolated Database Schema Implementation and Compatibility Test Suite.

Verifies table creation, SQLite auto-increment behavior, foreign keys, unique constraints,
canonical defect classes, UTC timestamps, nullable localization, and Alembic upgrade/downgrade
against an isolated temporary SQLite database.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import pytest
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from alembic.config import Config
from alembic import command

from app.db.base import Base
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
    PIPE_DEFECT_CLASSES,
    VehicleStatusEvent,
)


@pytest.fixture
def isolated_db(tmp_path: Path):
    """Fixture providing an isolated SQLite database with PRAGMA foreign_keys enabled."""
    db_file = tmp_path / "isolated_schema_test.db"
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables in isolated database
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    yield session_factory, engine

    engine.dispose()
    if db_file.exists():
        db_file.unlink()


def test_all_sixteen_tables_created_in_metadata():
    """Verify that all 16 required tables exist in Base.metadata and are registered."""
    expected_tables = {
        "inspections",
        "defects",
        "inspection_events",
        "inspection_summaries",
        "devices",
        "device_sessions",
        "device_heartbeats",
        "vehicle_status_events",
        "encoder_samples",
        "imu_samples",
        "camera_frames",
        "evidence_media",
        "ai_model_versions",
        "localization_records",
        "inspection_reports",
        "audit_events",
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"


def test_sqlite_integer_primary_keys_auto_increment(isolated_db):
    """Verify that BigIntId on SQLite aliases rowid and auto-increments (1, 2, 3...)."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        # Create devices
        dev1 = Device(id="dev-wroom-1", device_type="ESP32_WROOM")
        dev2 = Device(id="dev-wroom-2", device_type="ESP32_WROOM")
        session.add_all([dev1, dev2])

        # Create inspections without explicit ID
        insp1 = Inspection(
            inspection_id="INSP-AUTO-001",
            pipe_identifier="PVC-100",
            pipe_diameter_mm=200,
            operator_id="OP-01",
        )
        insp2 = Inspection(
            inspection_id="INSP-AUTO-002",
            pipe_identifier="PVC-100",
            pipe_diameter_mm=200,
            operator_id="OP-01",
        )
        session.add_all([insp1, insp2])
        session.commit()

        assert insp1.id == 1
        assert insp2.id == 2

        # Create encoder samples without explicit ID
        enc1 = EncoderSample(
            inspection_id=insp1.id,
            sequence_number=100,
            left_ticks=1000,
            right_ticks=1020,
        )
        enc2 = EncoderSample(
            inspection_id=insp1.id,
            sequence_number=101,
            left_ticks=1010,
            right_ticks=1030,
        )
        session.add_all([enc1, enc2])
        session.commit()

        assert enc1.id == 1
        assert enc2.id == 2


def test_existing_inspection_and_defect_models_functional(isolated_db):
    """Verify that existing inspection and defect operations remain 100% functional."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        insp = Inspection(
            inspection_id="INSP-FUNC-001",
            pipe_identifier="PVC-200",
            pipe_material="PVC",
            pipe_diameter_mm=250,
            operator_id="TECH-42",
            status=InspectionStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
        )
        session.add(insp)
        session.commit()

        defect = Defect(
            defect_id="DEF-FUNC-001",
            inspection_id=insp.id,
            frame_id="FRAME-001",
            defect_class=DefectClass.RUPTURE,
            confidence=0.92,
            bounding_box={"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4},
            capture_timestamp=datetime.now(timezone.utc),
            review_status=DefectReviewStatus.CONFIRMED,
        )
        session.add(defect)
        session.commit()

        assert defect.id is not None
        assert defect.inspection.inspection_id == "INSP-FUNC-001"
        assert insp.defect_count == 1


def test_foreign_keys_reject_invalid_references(isolated_db):
    """Verify that SQLite PRAGMA foreign_keys=ON rejects records referencing missing parents."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        # Attempt to insert event for non-existent inspection ID 9999
        event_obj = InspectionEvent(
            inspection_id=9999,
            event_type="STATE_CHANGE",
            payload={"status": "running"},
        )
        session.add(event_obj)
        with pytest.raises(IntegrityError):
            session.commit()


def test_unique_constraints_reject_duplicates(isolated_db):
    """Verify unique constraints reject duplicate business identifiers."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        dev1 = Device(id="dev-unique-1", device_type="ESP32_WROOM", mac_address="AA:BB:CC:DD:EE:01")
        dev2 = Device(id="dev-unique-2", device_type="ESP32_WROOM", mac_address="AA:BB:CC:DD:EE:01")
        session.add(dev1)
        session.commit()

        session.add(dev2)
        with pytest.raises(IntegrityError):
            session.commit()


def test_canonical_defect_classes_preserved():
    """Verify exact canonical defect classes match requirements."""
    expected_classes = ["Deformation", "Misalignment", "Obstacle", "Rupture"]
    assert PIPE_DEFECT_CLASSES == expected_classes
    assert [c.value for c in DefectClass] == expected_classes


def test_utc_timestamp_handling(isolated_db):
    """Verify UtcDateTime guarantees timezone-aware UTC datetime values."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        now_utc = datetime.now(timezone.utc)
        insp = Inspection(
            inspection_id="INSP-UTC-001",
            pipe_identifier="PVC-150",
            pipe_diameter_mm=150,
            operator_id="TECH-UTC",
            started_at=now_utc,
        )
        session.add(insp)
        session.commit()

        retrieved = session.scalar(select(Inspection).where(Inspection.id == insp.id))
        assert retrieved.started_at is not None
        assert retrieved.started_at.tzinfo == timezone.utc


def test_nullable_localization_behavior(isolated_db):
    """Verify LocalizationRecord can be persisted with null distance when sync is unverified."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        insp = Inspection(
            inspection_id="INSP-LOC-001",
            pipe_identifier="PVC-150",
            pipe_diameter_mm=150,
            operator_id="TECH-LOC",
        )
        session.add(insp)
        session.commit()

        defect = Defect(
            defect_id="DEF-LOC-001",
            inspection_id=insp.id,
            frame_id="FRAME-LOC-01",
            defect_class=DefectClass.DEFORMATION,
            capture_timestamp=datetime.now(timezone.utc),
            estimated_distance_meters=None,
        )
        session.add(defect)
        session.commit()

        loc_record = LocalizationRecord(
            defect_id=defect.id,
            frame_id="FRAME-LOC-01",
            frame_capture_timestamp=datetime.now(timezone.utc),
            encoder_sample_timestamp=datetime.now(timezone.utc),
            temporal_delta_ms=12.5,
            clock_sync_status="UNVERIFIED_SYNC",
            sync_notes="ESP32-CAM and ESP32-WROOM-32 hardware clock sync not calibrated",
            computed_distance_meters=None,
        )
        session.add(loc_record)
        session.commit()

        assert loc_record.id is not None
        assert loc_record.computed_distance_meters is None
        assert loc_record.clock_sync_status == "UNVERIFIED_SYNC"


def test_raw_telemetry_stored_without_fabricated_calibration(isolated_db):
    """Verify raw encoder and IMU samples store raw counts with derived fields nullable."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        insp = Inspection(
            inspection_id="INSP-TELEM-001",
            pipe_identifier="PVC-200",
            pipe_diameter_mm=200,
            operator_id="TECH-TELEM",
        )
        session.add(insp)
        session.commit()

        # Raw encoder reading without RPM or speed calibration
        enc = EncoderSample(
            inspection_id=insp.id,
            sequence_number=1,
            left_ticks=5420,
            right_ticks=5415,
            left_rpm=None,
            right_rpm=None,
            speed_mps=None,
        )
        # Raw IMU reading with raw LSB sensor units
        imu = IMUSample(
            inspection_id=insp.id,
            sequence_number=1,
            accel_x=124.0,
            accel_y=-32.0,
            accel_z=16384.0,
            gyro_x=5.0,
            gyro_y=-2.0,
            gyro_z=1.0,
            sensor_units="raw_lsb",
            pitch_deg=None,
            roll_deg=None,
            yaw_deg=None,
        )
        session.add_all([enc, imu])
        session.commit()

        assert enc.id is not None
        assert enc.left_rpm is None
        assert enc.speed_mps is None
        assert imu.sensor_units == "raw_lsb"
        assert imu.pitch_deg is None


def test_media_metadata_stores_relative_paths_and_checksums(isolated_db):
    """Verify EvidenceMedia stores relative paths, file size, and SHA-256 hashes."""
    session_factory, _ = isolated_db
    with session_factory() as session:
        insp = Inspection(
            inspection_id="INSP-MED-001",
            pipe_identifier="PVC-150",
            pipe_diameter_mm=150,
            operator_id="TECH-MED",
        )
        session.add(insp)
        session.commit()

        defect = Defect(
            defect_id="DEF-MED-001",
            inspection_id=insp.id,
            frame_id="FRAME-MED-01",
            defect_class=DefectClass.OBSTACLE,
            capture_timestamp=datetime.now(timezone.utc),
        )
        session.add(defect)
        session.commit()

        evidence = EvidenceMedia(
            media_uuid="MED-UUID-001",
            defect_id=defect.id,
            file_path="crops/insp_1/def_med_001.jpg",
            mime_type="image/jpeg",
            file_size_bytes=45210,
            checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            storage_backend="LOCAL_FS",
        )
        session.add(evidence)
        session.commit()

        assert evidence.id is not None
        assert evidence.file_path.startswith("crops/")
        assert len(evidence.checksum_sha256) == 64


def test_alembic_upgrade_and_downgrade_isolated_db(tmp_path: Path):
    """Verify that Alembic can upgrade to head, downgrade to prior head, and re-upgrade."""
    backend_dir = Path(__file__).resolve().parent.parent
    test_db_file = tmp_path / "alembic_migration_test.db"
    test_db_url = f"sqlite:///{test_db_file}"

    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "migrations"))
    cfg.set_main_option("sqlalchemy.url", test_db_url)

    # 1. Upgrade from scratch to new head (e7f8a9b0c1d2)
    command.upgrade(cfg, "head")

    # Verify tables created
    engine = create_engine(test_db_url)
    with engine.connect() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        table_names = {r[0] for r in tables}
        assert "devices" in table_names
        assert "encoder_samples" in table_names
        assert "evidence_media" in table_names
        assert "audit_events" in table_names

    # 2. Downgrade to d4d255efae0c
    command.downgrade(cfg, "d4d255efae0c")

    with engine.connect() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        table_names = {r[0] for r in tables}
        assert "devices" not in table_names
        assert "encoder_samples" not in table_names
        assert "inspections" in table_names
        assert "defects" in table_names

    # 3. Re-upgrade to head
    command.upgrade(cfg, "head")

    with engine.connect() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        table_names = {r[0] for r in tables}
        assert "devices" in table_names
        assert "encoder_samples" in table_names

    engine.dispose()
    if test_db_file.exists():
        test_db_file.unlink()

