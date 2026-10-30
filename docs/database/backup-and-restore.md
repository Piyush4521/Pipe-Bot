# PipeBot Database Backup and Disaster Recovery Runbook

## 1. Disaster Recovery Strategy Overview

The PipeBot backup and disaster recovery architecture is designed to protect structural pipe inspection records, computer vision defect evidence, and hardware sensor telemetry against hardware failure, filesystem corruption, or operational errors.

Key Architecture Principles:
- Non-Blocking Online Backups: Backups run concurrently while the crawler operates, using the official `sqlite3.Connection.backup()` engine API.
- Cryptographic Verification: Every backup archive is verified with SHA-256 hashing and structural integrity checks.
- Pre-Restore Safety Snapshots: Restorations automatically capture a snapshot of the target database before overwriting.
- Coordinated Media Synchronization: Defect evidence image crops stored on disk are backed up synchronously with database metadata.

---

## 2. Backup Mechanisms and Implementation

### 2.1 The SQLite Online Backup API
Standard file copying (`cp` or `shutil.copy2`) of an active SQLite database in WAL mode is unsafe because the file may be modified mid-copy, yielding a corrupt image.
PipeBot uses `sqlite3.Connection.backup()` implemented in `app/db/backup.py`:

```python
from app.db.backup import backup_sqlite_database

# Non-blocking online backup to target directory
result = backup_sqlite_database(
    src_db_path="data/pipebot.db",
    backup_dir="backups/database",
)
```

Process Workflow:
1. Opens source connection to active database.
2. Checkpoints WAL file if in WAL mode (`PRAGMA wal_checkpoint(TRUNCATE)`).
3. Opens destination connection to a new timestamped database file (`pipebot_backup_YYYYMMDD_HHMMSS.db`).
4. Executes page-level transfer via `src_conn.backup(dest_conn)`.
5. Closes both database connections cleanly.
6. Connects to destination database in read-only mode to execute `PRAGMA integrity_check` and `PRAGMA foreign_key_check`.
7. Computes hexadecimal SHA-256 checksum and returns execution metadata.

### 2.2 Coordinated Media Backup
Defect evidence images stored in `data/media` are archived using `backup_inspection_media`:
```python
from app.db.backup import backup_inspection_media

media_result = backup_inspection_media(
    src_media_dir="data/media",
    target_backup_dir="backups/media",
)
```
Generates a timestamped compressed ZIP archive (`pipebot_media_backup_YYYYMMDD_HHMMSS.zip`) with SHA-256 verification.

---

## 3. Integrity Verification Procedures

Every backup file must be verified before being archived or used for restoration.

### 3.1 Automated Verification Function
```python
from app.db.backup import verify_backup_integrity

verification = verify_backup_integrity("backups/database/pipebot_backup_20261030_120000.db")
if verification["is_valid"]:
    print("Backup is healthy and structurally sound")
else:
    print(f"Backup corrupted: {verification['details']}")
```

### 3.2 Manual CLI Verification
Field engineers can manually verify a backup file using the SQLite CLI:
```bash
sqlite3 backups/database/pipebot_backup_20261030_120000.db "PRAGMA integrity_check;"
# Expected output: ok

sqlite3 backups/database/pipebot_backup_20261030_120000.db "PRAGMA foreign_key_check;"
# Expected output: (empty, indicating zero violations)
```

---

## 4. Disaster Recovery and Restoration Procedures

### 4.1 Automated Atomic Restore
Restoration is performed via `restore_sqlite_database`:
```python
from app.db.backup import restore_sqlite_database

restore_meta = restore_sqlite_database(
    backup_path="backups/database/pipebot_backup_20261030_120000.db",
    target_db_path="data/pipebot.db",
    create_safety_snapshot=True,
)
```

Safeguards executed during restore:
1. Pre-validation: Verifies source backup file with `verify_backup_integrity()`. If invalid, restoration is aborted immediately with `ValueError`.
2. Safety Snapshot: If `target_db_path` already exists, copies it to `pipebot_pre_restore_safety_YYYYMMDD_HHMMSS.db`.
3. Safe Write: Uses `sqlite3.backup()` to stream pages into target, avoiding Windows file locking errors.
4. Clean Cache: Deletes stale `-wal` and `-shm` index files for the target database.
5. Post-validation: Executes integrity checks on the newly restored target database.

### 4.2 Emergency Manual Recovery Runbook
If an operator accidentally corrupts or deletes the active database:

Step 1: Stop the FastAPI backend process immediately:
```bash
pkill -f "uvicorn app.main:app"
```

Step 2: Locate the most recent verified backup in `backups/database/`:
```bash
ls -lt backups/database/pipebot_backup_*.db | head -n 1
```

Step 3: Verify the selected backup:
```bash
sqlite3 <selected_backup_file> "PRAGMA integrity_check;"
```

Step 4: Execute restore via python script or manual copy:
```bash
cp <selected_backup_file> backend/data/pipebot.db
rm -f backend/data/pipebot.db-wal backend/data/pipebot.db-shm
```

Step 5: Verify the restored database:
```bash
PYTHONPATH=. .venv/bin/python scripts/inspect_active_db.py
```

Step 6: Restart the FastAPI application and verify readiness probe (`/api/v1/health/ready`).

---

## 5. Backup Retention and Rotation Policy

| Backup Tier | Frequency | Target Directory | Retention Period |
| :--- | :--- | :--- | :--- |
| Pre-Mission Snapshot | Before starting crawler inspection | `backups/database/pre_mission/` | 14 days |
| Post-Mission Full | At completion of inspection | `backups/database/` | 90 days |
| Media Archive (ZIP) | At completion of inspection | `backups/media/` | 90 days |
| Pre-Restore Snapshot | Automatically prior to any restore | `data/pre_restore_safety/` | 30 days |
| Long-Term Cold Archive | Quarterly consolidated archive | External S3 / Cold Storage | 3 years (Compliance) |

