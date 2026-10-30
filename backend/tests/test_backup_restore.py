"""Automated Tests for SQLite Online Backup, Integrity Validation, and Disaster Recovery.

Tests verify non-blocking backup execution, SHA-256 checksums, PRAGMA integrity
checks, corrupted database detection, atomic restoration, safety snapshots,
and media archive backups. All operations run strictly against isolated temporary
databases and directories.
"""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.backup import (
    backup_sqlite_database,
    backup_inspection_media,
    compute_file_sha256,
    restore_sqlite_database,
    verify_backup_integrity,
)
from app.models.defect import Defect
from app.models.device import Device
from app.models.inspection import Inspection


@pytest.fixture
def isolated_source_db(tmp_path: Path) -> Path:
    """Create and seed an isolated SQLite test database with domain records."""
    db_path = tmp_path / "source_test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        # Seed Inspection
        insp = Inspection(
            inspection_id="INSP-TEST-001",
            pipe_identifier="PIPE-PVC-300",
            pipe_material="PVC",
            pipe_diameter_mm=300,
            operator_id="OP-QA-01",
            status="completed",
            total_distance_meters=25.5,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        session.add(insp)
        session.flush()

        # Seed Defect
        defect = Defect(
            defect_id="DEF-TEST-001",
            inspection_id=insp.id,
            frame_id="FRAME-TEST-001",
            defect_class="Rupture",
            confidence=0.92,
            capture_timestamp=datetime.now(timezone.utc),
            estimated_distance_meters=14.2,
            review_status="confirmed",
        )
        session.add(defect)

        # Seed Device
        dev = Device(
            id="esp32-drive-test",
            device_type="ESP32_WROOM",
            firmware_version="1.0.0",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        session.add(dev)
        session.commit()

    engine.dispose()
    return db_path


def test_backup_sqlite_database_success(isolated_source_db: Path, tmp_path: Path):
    """Verify clean execution of online database backup to destination directory."""
    backup_dir = tmp_path / "backups"
    result = backup_sqlite_database(isolated_source_db, backup_dir)

    assert result["status"] == "success"
    assert "backup_path" in result
    backup_path = Path(result["backup_path"])
    assert backup_path.is_file()
    assert result["file_size_bytes"] > 0
    assert len(result["checksum_sha256"]) == 64
    assert result["verification"]["is_valid"] is True


def test_verify_backup_integrity_valid_and_corrupt(isolated_source_db: Path, tmp_path: Path):
    """Verify integrity checker validates healthy backup and flags corrupted file."""
    backup_dir = tmp_path / "backups"
    result = backup_sqlite_database(isolated_source_db, backup_dir)
    backup_path = Path(result["backup_path"])

    # 1. Valid backup verification
    healthy_check = verify_backup_integrity(backup_path)
    assert healthy_check["is_valid"] is True
    assert healthy_check["integrity_check"] == "ok"
    assert healthy_check["foreign_key_violations"] == 0

    # 2. Corrupt database verification
    corrupt_path = tmp_path / "corrupt.db"
    corrupt_path.write_bytes(backup_path.read_bytes())
    with corrupt_path.open("r+b") as f:
        f.seek(100)
        f.write(b"CORRUPTED_DATABASE_BYTES_OVERWRITE_HEADER_INFO" * 10)

    corrupt_check = verify_backup_integrity(corrupt_path)
    assert corrupt_check["is_valid"] is False


def test_restore_sqlite_database_and_verify_counts(isolated_source_db: Path, tmp_path: Path):
    """Verify database restoration preserves row counts and produces a valid target DB."""
    backup_dir = tmp_path / "backups"
    backup_res = backup_sqlite_database(isolated_source_db, backup_dir)
    backup_path = Path(backup_res["backup_path"])

    restore_target = tmp_path / "restored.db"
    restore_res = restore_sqlite_database(backup_path, restore_target)

    assert restore_res["status"] == "success"
    assert Path(restore_res["restored_path"]).is_file()
    assert restore_res["verification"]["is_valid"] is True

    # Validate row counts in restored DB
    conn = sqlite3.connect(str(restore_target))
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM inspections")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT count(*) FROM defects")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT count(*) FROM devices")
    assert cur.fetchone()[0] == 1
    conn.close()


def test_restore_creates_safety_snapshot(isolated_source_db: Path, tmp_path: Path):
    """Verify that restoring over an existing database generates a pre-restore safety snapshot."""
    backup_dir = tmp_path / "backups"
    backup_res = backup_sqlite_database(isolated_source_db, backup_dir)
    backup_path = Path(backup_res["backup_path"])

    # Existing target file
    target_path = tmp_path / "target_existing.db"
    target_path.write_bytes(isolated_source_db.read_bytes())

    restore_res = restore_sqlite_database(backup_path, target_path, create_safety_snapshot=True)
    assert restore_res["safety_snapshot_path"] is not None
    snapshot_path = Path(restore_res["safety_snapshot_path"])
    assert snapshot_path.is_file()
    assert snapshot_path.name.startswith("pipebot_pre_restore_safety_")


def test_restore_rejects_corrupted_backup(tmp_path: Path):
    """Verify that restore raises an error if the source backup file fails integrity checks."""
    corrupt_path = tmp_path / "bad_backup.db"
    corrupt_path.write_bytes(b"NOT_A_VALID_SQLITE_DATABASE_FILE")
    target_path = tmp_path / "target.db"

    with pytest.raises(ValueError, match="Cannot restore invalid backup"):
        restore_sqlite_database(corrupt_path, target_path)


def test_backup_inspection_media(tmp_path: Path):
    """Verify coordinated backup archive creation for defect evidence media."""
    media_dir = tmp_path / "media_store"
    media_dir.mkdir()
    (media_dir / "crop_def_001.jpg").write_bytes(b"FAKE_JPEG_EVIDENCE_DATA_1")
    (media_dir / "crop_def_002.jpg").write_bytes(b"FAKE_JPEG_EVIDENCE_DATA_2")

    backup_dir = tmp_path / "media_backups"
    result = backup_inspection_media(media_dir, backup_dir)

    assert result["status"] == "success"
    archive_path = Path(result["archive_path"])
    assert archive_path.is_file()
    assert archive_path.suffix == ".zip"
    assert result["file_size_bytes"] > 0
    assert len(result["checksum_sha256"]) == 64
