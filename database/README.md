# PipeBot Database Engineering & Persistence Guide

This directory documents the database architecture, schema definitions, operational runbooks, and disaster recovery procedures for PipeBot.

## 1. Active Database Status

- Active Database Engine: SQLite 3 with Write-Ahead Logging (WAL)
- Active Database Location: `backend/data/pipebot.db`
- Current Alembic Revision Head: `d4d255efae0c`
- Verified Integrity: `PRAGMA integrity_check = ok`, zero foreign key violations
- Future Target Database: PostgreSQL 16 (Logical schema and migrations verified in isolated test databases)

## 2. Complete Relational Schema (16 Tables)

The database schema captures the complete lifecycle of robotic conduit inspections:

| Table Name | Primary Role | Key Foreign Keys & Constraints |
| :--- | :--- | :--- |
| `inspections` | Pipeline inspection crawl sessions | Restrictive deletion, unique `inspection_id` |
| `defects` | Classified pipeline structural defects | References `inspections.id` (RESTRICT) |
| `camera_frames` | Ingested optical video frames | References `inspections.id` |
| `evidence_media` | Evidence snapshot image files & checksums | References `defects.id` |
| `devices` | Microcontroller registry (ESP32-WROOM, CAM) | Unique hardware ID |
| `device_sessions` | Hardware connection & boot sessions | References `devices.id` |
| `device_heartbeats`| Periodic link health & battery diagnostics | References `device_sessions.id` |
| `encoder_samples` | Rotary odometry pulse readings | References `inspections.id` |
| `imu_samples` | MPU6050 6-axis accelerometer & gyroscope | References `inspections.id` |
| `vehicle_status_events`| Motor drive state & emergency stop status | References `inspections.id` |
| `localization_records`| Frame-to-odometry spatial correlation | References `defects.id` |
| `inspection_events` | Granular session lifecycle transitions | References `inspections.id` |
| `inspection_reports` | Compiled audit reports (JSON / PDF) | References `inspections.id` |
| `inspection_summaries`| Aggregate defect tallies & pipe grades | Primary key references `inspections.id` |
| `ai_model_versions` | YOLOv8 neural network version tracking | Artifact paths & SHA-256 checksums |
| `audit_events` | Security audit trail for compliance | Immutable append-only log |

## 3. Operational Runbooks

### Database Backup Execution:
The automated backup utility creates an atomic copy of the SQLite database using SQLite's native backup API, verifying file integrity immediately upon completion:

```bash
# Execute database and media backup
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
python -c "from app.db.backup import backup_sqlite_database; print(backup_sqlite_database())"
```

Backups are saved to `backend/backups/` with ISO timestamps:
```text
backend/backups/pipebot_backup_20261030_182929.db
```

### Database Restore & Verification:
To restore a validated backup snapshot:
```bash
python -c "from app.db.backup import restore_sqlite_database; print(restore_sqlite_database('backups/pipebot_backup_20261030_182929.db'))"
```

Before applying the restore, the utility automatically captures a safety snapshot of the target database to guarantee zero data loss.

## 4. PostgreSQL 16 Scalability Blueprint

When upgrading to a centralized multi-tenant PostgreSQL 16 server:
1. Set `DATABASE_URL=postgresql+psycopg://user:password@host:5432/pipebot` in `backend/.env`.
2. Apply migrations up to `e7f8a9b0c1d2`:
   ```bash
   alembic upgrade head
   ```
3. PostgreSQL advantages utilized in the codebase:
   - True `BIGINT GENERATED ALWAYS AS IDENTITY` primary keys
   - Native `TIMESTAMPTZ` UTC storage
   - Native `JSONB` for bounding box geometry and sensor payloads
   - Connection pooling via `QueuePool` with health pre-pings
