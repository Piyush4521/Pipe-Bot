# PipeBot Database Operations and Maintenance Guide

## 1. Operational Overview

This runbook establishes standard operating procedures (SOPs) for the PipeBot inspection database layer. It provides database administrators, backend engineers, and field technicians with concrete procedures for monitoring, maintaining, tuning, and troubleshooting the SQLite database during crawler inspection missions.

---

## 2. Health Monitoring and Diagnostics

### 2.1 Automated Health Probes
The backend exposes dedicated HTTP endpoints for database liveliness and readiness validation:

- Readiness Probe: `GET /api/v1/health/ready`
  - Validates that the database connection pool is active and responsive.
  - Returns `200 OK` with `{"status": "ready", "database": "connected"}`.
  - Returns `503 Service Unavailable` if the database file is inaccessible or locked.

- Database Health Detail: `GET /api/v1/health/db`
  - Executes `SELECT 1` ping.
  - Inspects active table availability and SQLite schema responsiveness.

### 2.2 Routine Integrity Inspection
Engineers should run the automated inspection script before and after multi-hour crawler operations:
```bash
# Within WSL or host environment
cd /mnt/d/PipeBot/backend
PYTHONPATH=. .venv/bin/python scripts/inspect_active_db.py
```
Expected output:
- `PRAGMA integrity_check` returns `ok`.
- `PRAGMA foreign_key_check` returns 0 violations.
- Current active Alembic head matches expectations (`d4d255efae0c` for baseline or `e7f8a9b0c1d2` for extended telemetry schema).

---

## 3. SQLite Engine Tuning and Lock Management

### 3.1 Write-Ahead Logging (WAL) Configuration
By default, SQLite uses rollback journals which lock the entire database during write transactions, preventing concurrent reads. PipeBot configures WAL mode for production deployments:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```
Benefits:
- Concurrent Readers: Readers do not block writers, and writers do not block readers.
- Performance: Sequential writes to `-wal` file achieve sub-millisecond commit latency.
- Durability: `NORMAL` synchronous mode guarantees structural consistency across application crashes.

### 3.2 Lock Contention and Busy Timeout
To prevent `sqlite3.OperationalError: database is locked` errors during concurrent telemetry ingestion and UI dashboard queries, every SQLite connection automatically sets a busy timeout handler in `app/db/session.py`:
```python
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()
```
The engine sleeps and retries for up to 5,000 milliseconds before raising an operational error.

---

## 4. Session and Transaction Lifecycle Management

### 4.1 Dependency Injection in FastAPI
Database sessions are injected into route handlers using the `get_db` generator dependency:
```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
Guarantees:
- Every HTTP request receives an isolated database session.
- Connections are automatically closed in the `finally` block even if unhandled exceptions occur.
- Sessions do not leak across asynchronous tasks.

### 4.2 Explicit Transaction Scopes
For complex multi-step write operations (e.g., logging defect + saving evidence + updating analytical summary), the `transaction_scope` context manager guarantees atomic execution:
```python
from app.db.session import transaction_scope

with transaction_scope(session):
    # Step 1: Record Defect
    defect = defect_repo.create(defect_data)
    # Step 2: Attach Evidence Media
    evidence = media_repo.record_evidence(media_data)
    # Step 3: Refresh Analytical Summary
    insp_repo.refresh_summary(inspection_id)
# Transaction commits automatically on scope exit, or rolls back entirely on exception.
```

---

## 5. Maintenance Routines

### 5.1 WAL File Checkpointing
Over long inspection sessions, the `-wal` file can grow significantly if long-running read transactions prevent automated checkpointing.
To force a complete checkpoint and truncate the WAL file:
```sql
PRAGMA wal_checkpoint(TRUNCATE);
```
Recommended frequency:
- At the conclusion of each inspection session.
- Preceding any offline database backup or migration.

### 5.2 Vacuuming and Defragmentation
Frequent updates and deletions of transient telemetry samples can fragment the database file.
To defragment and reclaim disk space:
```sql
VACUUM;
```
Note: `VACUUM` requires sufficient free disk space to write a complete copy of the database file. It should only be run when the crawler crawler is powered down and the backend application is idle.

### 5.3 Telemetry Data Retention Policy
High-frequency sensor telemetry (20Hz wheel encoder pulses and 6-axis IMU samples) generates approximately 426 KB per 1,000 samples (~30 MB per hour of continuous driving).
Recommended operational retention:
1. Active Inspection: Keep all raw samples in the active database during active navigation.
2. Completed Inspection: Compile summary metrics and defect localization records into `inspection_summaries`.
3. Historical Archive: After 30 days, export raw `encoder_samples` and `imu_samples` to compressed parquet or cold storage files, retaining the parent `inspections`, `defects`, and `evidence_media` records permanently.

