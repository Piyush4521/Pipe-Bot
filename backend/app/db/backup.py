"""SQLite Backup and Disaster Recovery Utilities.

Provides online, non-blocking SQLite database backups using the official
sqlite3.Connection.backup() API, with WAL checkpointing, SHA-256 checksums,
PRAGMA integrity validation, and atomic restore routines.
"""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil
import sqlite3
from typing import Any, Dict, Optional, Union


def compute_file_sha256(file_path: Union[str, Path]) -> str:
    """Compute the hexadecimal SHA-256 checksum of a file."""
    path = Path(file_path)
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_backup_integrity(backup_path: Union[str, Path]) -> Dict[str, Any]:
    """Verify the structural and relational integrity of a SQLite database backup file.

    Executes PRAGMA integrity_check and PRAGMA foreign_key_check in read-only mode.
    """
    path = Path(backup_path).resolve()
    if not path.is_file():
        return {
            "is_valid": False,
            "integrity_check": "File does not exist",
            "foreign_key_violations": -1,
            "details": f"Path {path} is not an existing file",
        }

    conn = None
    try:
        # Connect in read-only mode to prevent accidental mutation
        uri = f"file:{path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        cursor = conn.cursor()

        # 1. Structural integrity check
        cursor.execute("PRAGMA integrity_check")
        integrity_results = cursor.fetchall()
        integrity_ok = len(integrity_results) == 1 and integrity_results[0][0] == "ok"

        # 2. Relational foreign key check
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        fk_ok = len(fk_violations) == 0

        is_valid = integrity_ok and fk_ok
        details = "Integrity and foreign key checks passed" if is_valid else (
            f"Integrity: {integrity_results}; FK Violations: {len(fk_violations)}"
        )

        return {
            "is_valid": is_valid,
            "integrity_check": "ok" if integrity_ok else str(integrity_results),
            "foreign_key_violations": len(fk_violations),
            "details": details,
        }
    except Exception as exc:
        return {
            "is_valid": False,
            "integrity_check": f"Exception: {str(exc)}",
            "foreign_key_violations": -1,
            "details": str(exc),
        }
    finally:
        if conn:
            conn.close()


def backup_sqlite_database(
    src_db_path: Union[str, Path],
    backup_dir: Union[str, Path],
    pages_per_step: int = -1,
    sleep_seconds: float = 0.0,
) -> Dict[str, Any]:
    """Perform an online, non-blocking backup of an active SQLite database.

    Uses sqlite3.Connection.backup() to copy database pages cleanly.
    """
    src_path = Path(src_db_path).resolve()
    if not src_path.is_file():
        raise FileNotFoundError(f"Source database file not found at: {src_path}")

    target_dir = Path(backup_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_path = target_dir / f"pipebot_backup_{timestamp_str}.db"

    src_conn = None
    dest_conn = None
    try:
        # Open source database
        src_conn = sqlite3.connect(str(src_path))

        # Checkpoint WAL if database is in WAL mode
        try:
            cur = src_conn.cursor()
            cur.execute("PRAGMA journal_mode")
            mode = cur.fetchone()[0].lower()
            if mode == "wal":
                cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            cur.close()
        except Exception:
            pass  # Best effort checkpoint

        # Open destination database
        dest_conn = sqlite3.connect(str(dest_path))

        # Perform online backup
        with dest_conn:
            src_conn.backup(dest_conn, pages=pages_per_step, sleep=sleep_seconds)

    finally:
        if dest_conn:
            dest_conn.close()
        if src_conn:
            src_conn.close()

    # Validate the generated backup
    verification = verify_backup_integrity(dest_path)
    if not verification["is_valid"]:
        if dest_path.exists():
            dest_path.unlink()
        raise RuntimeError(f"Backup verification failed: {verification['details']}")

    file_size = dest_path.stat().st_size
    sha256_hash = compute_file_sha256(dest_path)

    return {
        "status": "success",
        "backup_path": str(dest_path),
        "source_path": str(src_path),
        "file_size_bytes": file_size,
        "checksum_sha256": sha256_hash,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verification": verification,
    }


def restore_sqlite_database(
    backup_path: Union[str, Path],
    target_db_path: Union[str, Path],
    create_safety_snapshot: bool = True,
) -> Dict[str, Any]:
    """Restore a SQLite database from a verified backup file.

    Optionally generates a pre-restore safety snapshot of the target database
    before executing the atomic restore.
    """
    backup_file = Path(backup_path).resolve()
    target_file = Path(target_db_path).resolve()

    if not backup_file.is_file():
        raise FileNotFoundError(f"Backup file not found at: {backup_file}")

    # Verify backup integrity prior to restore
    verification = verify_backup_integrity(backup_file)
    if not verification["is_valid"]:
        raise ValueError(f"Cannot restore invalid backup: {verification['details']}")

    target_file.parent.mkdir(parents=True, exist_ok=True)

    safety_snapshot_path: Optional[str] = None
    if target_file.exists() and create_safety_snapshot:
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        snapshot_dest = target_file.parent / f"pipebot_pre_restore_safety_{timestamp_str}.db"
        shutil.copy2(target_file, snapshot_dest)
        safety_snapshot_path = str(snapshot_dest)

    # Use sqlite3.backup to safely write to target without file locking issues
    src_conn = None
    dest_conn = None
    try:
        src_conn = sqlite3.connect(str(backup_file))
        dest_conn = sqlite3.connect(str(target_file))
        with dest_conn:
            src_conn.backup(dest_conn, pages=100)
    finally:
        if dest_conn:
            dest_conn.close()
        if src_conn:
            src_conn.close()

    # Clean up any lingering WAL/SHM files for target
    wal_file = target_file.parent / f"{target_file.name}-wal"
    shm_file = target_file.parent / f"{target_file.name}-shm"
    if wal_file.exists():
        wal_file.unlink()
    if shm_file.exists():
        shm_file.unlink()

    # Verify restored target database
    target_verification = verify_backup_integrity(target_file)
    if not target_verification["is_valid"]:
        raise RuntimeError(f"Restored database integrity failed: {target_verification['details']}")

    return {
        "status": "success",
        "restored_path": str(target_file),
        "source_backup_path": str(backup_file),
        "safety_snapshot_path": safety_snapshot_path,
        "restored_at": datetime.now(timezone.utc).isoformat(),
        "checksum_sha256": compute_file_sha256(target_file),
        "verification": target_verification,
    }


def backup_inspection_media(
    src_media_dir: Union[str, Path],
    target_backup_dir: Union[str, Path],
) -> Dict[str, Any]:
    """Create a coordinated compressed ZIP archive of defect evidence crops and media files."""
    media_path = Path(src_media_dir).resolve()
    target_dir = Path(target_backup_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_base = target_dir / f"pipebot_media_backup_{timestamp_str}"

    if not media_path.exists() or not any(media_path.iterdir()):
        # Empty or nonexistent media directory: create empty directory archive
        media_path.mkdir(parents=True, exist_ok=True)

    archive_path_str = shutil.make_archive(
        base_name=str(archive_base),
        format="zip",
        root_dir=str(media_path),
    )
    archive_path = Path(archive_path_str)

    return {
        "status": "success",
        "archive_path": str(archive_path),
        "file_size_bytes": archive_path.stat().st_size,
        "checksum_sha256": compute_file_sha256(archive_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
