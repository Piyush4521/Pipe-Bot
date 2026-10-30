# PipeBot Database Engineering: Scalable Database Architecture Blueprint

## 1. Executive Summary

This architecture blueprint specifies the target persistence tier for the PipeBot robotic PVC pipeline inspection platform. It defines the technology selection, deployment topology, transaction boundaries, storage partitioning, data lifecycle policies, and disaster recovery strategies required to transition PipeBot from a single-user SQLite prototype to an industrial-grade, multi-user inspection system.

The core recommendation establishes **PostgreSQL 16** as the primary relational and time-series database, deployed locally via Docker with all persistent volumes pinned to the `D:\PipeBot` workspace. SQLite is retained as a zero-dependency offline edge fallback.

---

## 2. Database Technology Decision and Justification

### 2.1 Primary Platform: PostgreSQL 16
PostgreSQL 16 is selected as the primary enterprise database engine for PipeBot based on the following verified technical capabilities:
1. **Multi-Version Concurrency Control (MVCC)**: Allows concurrent high-frequency telemetry ingestion from crawler microcontrollers without blocking operator dashboard queries, report compilation, or video analysis workers.
2. **Declarative Table Partitioning**: Enables native range partitioning by `inspection_id` or date for high-volume telemetry tables (`encoder_telemetry`, `imu_telemetry`, `frame_metadata`), ensuring query pruning and trivial historical data purging.
3. **Block Range Indexing (BRIN)**: Provides ultra-compact indexes for physically ordered time-series columns (`recorded_at`), reducing index storage by over 90% compared to traditional B-tree indexes while maintaining rapid time-slice retrieval.
4. **Structured JSONB with GIN Indexing**: Stores flexible, non-queried hardware configuration payloads and audit snapshots without degrading relational schema rigor.
5. **Robust Connection Pooling and Async Ecosystem**: Seamlessly integrates with FastAPI via `asyncpg` and SQLAlchemy 2.0 AsyncEngine, supporting hundreds of concurrent operations without connection exhaustion.

### 2.2 Technology Deferrals and Non-Recommendations
- **TimescaleDB**: Deferred. Native PostgreSQL 16 range partitioning and BRIN indexes handle PipeBot's projected 10-50 Hz telemetry volume (under 100,000 rows/hour) with lower operational overhead and no external extension dependency. TimescaleDB may be re-evaluated if fleet operations scale to dozens of simultaneous crawlers.
- **MongoDB / NoSQL**: Rejected. Inspection workflows, defect reviews, compliance grading, and spatial defect localization are inherently relational and require foreign-key referential integrity and strict ACID transaction boundaries.
- **Redis**: Deferred. In-memory telemetry ring buffers are currently handled efficiently in Python memory (`TelemetryStateService`). A distributed Redis cache will only be introduced when multiple backend worker processes require shared pub/sub state.

### 2.3 Edge-to-Central Hybrid Architecture
PipeBot adopts a two-tier operational architecture:
- **Edge Deployment (Crawler / Field Laptop)**: A local processing unit running FastAPI and Dockerized PostgreSQL 16 (or SQLite fallback if Docker is unavailable) captures live streams and logs telemetry with zero external network dependency.
- **Centralized Deployment (Facility Server / Cloud)**: Completed inspection packages, defect snapshots, and summarized telemetry are synchronized to a centralized PostgreSQL cluster for enterprise fleet analytics and historical compliance auditing.

---

## 3. Docker Deployment Specification

When containerized PostgreSQL is deployed, it must follow strict configuration rules to adhere to project constraints:

### 3.1 Directory and Volume Placement
- The container configuration and persistent storage must reside exclusively on the `D:` drive inside the project hierarchy:
  - Configuration: `D:\PipeBot\docker\postgres\`
  - Data Volume: `D:\PipeBot\data\postgres_data\`
- **STRICT PROHIBITION**: Docker named volumes or bind mounts must never map to the `C:` drive or user profile directories.

### 3.2 Security and Network Isolation
- PostgreSQL must bind strictly to the localhost loopback adapter (`127.0.0.1:5432`) during development. Public interface exposure (`0.0.0.0`) is prohibited without network firewalls, TLS encryption, and secure credential rotation.
- Credentials must be injected via environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) loaded from `backend/.env`. Safe defaults are provided in `.env.example`.
- Dedicated non-root user execution inside the official `postgres:16-alpine` image.

---

## 4. Domain Ownership and Service Boundaries

Data access is partitioned across distinct service domains to maintain clean architectural separation and single-responsibility principles:

```text
+---------------------------------------------------------------------------------+
|                                FastAPI Application                              |
+---------------------------------------------------------------------------------+
       |                                |                               |
       v                                v                               v
+--------------------+        +--------------------+        +--------------------+
| Inspection Domain  |        |  Telemetry Domain  |        |   Vision Domain    |
| - Inspection Repo  |        | - Ingest Buffer    |        | - Frame Ingest     |
| - Lifecycle Service|        | - Telemetry Repo   |        | - Inference Pipe   |
| - Audit Service    |        | - Odometer Engine  |        | - Evidence Service |
+--------------------+        +--------------------+        +--------------------+
       |                                |                               |
       +--------------------------------+-------------------------------+
                                        |
                                        v
                    +---------------------------------------+
                    |        PostgreSQL 16 Database         |
                    |  - Relational Schemas & Foreign Keys  |
                    |  - Range Partitions (Telemetry)       |
                    |  - BRIN & B-Tree Composite Indexes    |
                    +---------------------------------------+
                                        |
                                        v
                    +---------------------------------------+
                    |    Filesystem Media Tier (D: Drive)   |
                    |  - D:\PipeBot\backend\data\media\     |
                    |  - Defect Evidence JPEG Crops         |
                    |  - Generated Inspection PDF Reports   |
                    +---------------------------------------+
```

1. **Inspection Domain**:
   - Owns `inspections`, `inspection_events`, `inspection_summaries`, and `reports`.
   - Authorizes state machine transitions (`PENDING` -> `RUNNING` -> `COMPLETED` -> `ARCHIVED`).
   - Enforces non-destructive archival and prevents unauthorized record deletion.
2. **Telemetry Domain**:
   - Owns `device_sessions`, `device_heartbeats`, `encoder_telemetry`, and `imu_telemetry`.
   - Manages asynchronous write buffering to prevent per-packet database roundtrips.
   - Computes distance odometry and passes spatial coordinates to the vision domain.
3. **Vision and AI Domain**:
   - Owns `camera_frames`, `ai_model_versions`, `defects`, and `evidence_media`.
   - Coordinates with filesystem storage for defect crop snapshots.
   - Enforces canonical defect classes: `Deformation`, `Misalignment`, `Obstacle`, `Rupture`.
4. **Audit and Administration Domain**:
   - Owns `audit_events`.
   - Maintains append-only immutable records of administrative updates, defect overrides, and archival actions.

---

## 5. ACID Transaction Boundaries and Ingestion Buffering

### 5.1 Relational Transaction Boundaries
Multi-table business operations must execute within explicit atomic database transactions:
1. **Inspection Status Transition**:
   - Updates `inspections.status`.
   - Inserts `inspection_events` record with transition metadata and operator ID.
   - Both writes must commit together; failure rolls back both changes.
2. **Defect Detection Ingestion**:
   - Validates frame existence and AI model version.
   - Persists crop image to `backend/data/media/crops/`.
   - In a single transaction, inserts `defects` and `evidence_media` records.
   - If database insert fails, the newly written image crop file is unlinked during rollback to prevent orphaned disk artifacts.
3. **Inspection Archival**:
   - Sets `is_archived = True` on `inspections`.
   - Records an `audit_events` row.
   - Restrictive foreign keys ensure associated defects and telemetry remain linked and accessible for historical audit.

### 5.2 High-Frequency Telemetry Write Buffer Pattern
Writing every 10-50 Hz telemetry packet individually causes extreme transaction overhead and lock contention. The architecture mandates an asynchronous batch buffer:
- Incoming telemetry packets from ESP32-WROOM-32 are validated and appended to an in-memory queue.
- A background worker flushes the queue to PostgreSQL using `COPY` or multi-row `INSERT ... VALUES`:
  - **Batch Flush Triggers**: Every 100 accumulated records OR every 1,000 milliseconds (whichever occurs first).
  - **Failure Handling**: If a batch fails, the transaction rolls back, error counters increment, and the buffer retries before logging to prevent memory exhaustion.
- Telemetry writes are decoupled from REST API requests, guaranteeing sub-50ms API responsiveness during active crawler movement.

---

## 6. Storage Tiering and Media Abstraction

### 6.1 Storage Tiering Principles
- **Relational Metadata**: Stored in PostgreSQL (inspection info, timestamps, sensor readings, bounding boxes, review states).
- **Binary Evidence Images**: Stored on local filesystem (`D:\PipeBot\backend\data\media\crops\`). The database stores relative POSIX URI paths (`crops/insp_1/defect_12.jpg`) and SHA-256 integrity checksums.
- **Continuous Video**: Never stored in the database. Live streams are displayed via WebRTC/MJPEG and processed in RAM. Optional full-run video recordings reside on disk as MP4 files with database metadata references.
- **AI Model Weights**: Stored on filesystem (`backend/weights/`). The database tracks model versions, configuration hyperparameters, and artifact checksums.

### 6.2 Storage Provider Abstraction
To ensure portability between local field computers and cloud deployments, all file operations must route through a unified `StorageProvider` interface:
```python
class StorageProvider(Protocol):
    async def save_evidence_image(self, relative_path: str, data: bytes) -> str: ...
    async def get_evidence_image(self, relative_path: str) -> bytes: ...
    async def delete_evidence_image(self, relative_path: str) -> bool: ...
    async def check_exists(self, relative_path: str) -> bool: ...
```
- **LocalFilesystemStorage**: Active default, operating under `D:\PipeBot\backend\data\media\`.
- **S3CompatibleStorage**: Future drop-in implementation for AWS S3 or MinIO without modifying defect management services.

---

## 7. Scalability and Partitioning Strategy

### 7.1 Table Partitioning
High-frequency telemetry tables (`encoder_telemetry`, `imu_telemetry`, `camera_frames`) must utilize PostgreSQL 16 declarative range partitioning:
- **Partition Key**: `inspection_id` (Range / List) or `recorded_at` (Range by month).
- **Benefit 1 (Query Pruning)**: Querying telemetry for a single inspection scans only that inspection's partition, bypassing millions of unrelated historical rows.
- **Benefit 2 (Maintenance)**: Purging or archiving aged telemetry is executed via `ALTER TABLE ... DETACH PARTITION` and `DROP TABLE`, which finishes instantaneously without index fragmentation or `VACUUM` table locks.

### 7.2 Connection Pooling Architecture
- Backend uses SQLAlchemy 2.0 async engine backed by `asyncpg`.
- Pool configuration:
  - `pool_size`: 10 connections.
  - `max_overflow`: 20 connections.
  - `pool_timeout`: 30 seconds.
  - `pool_recycle`: 1,800 seconds (30 minutes).
- For future multi-operator deployments with multiple FastAPI replicas, an external `PgBouncer` service will sit in front of PostgreSQL in transaction pooling mode.

---

## 8. Data Retention and Lifecycle Policies

PipeBot enforces a three-tier data retention lifecycle to prevent storage exhaustion while preserving compliance records:

| Tier | Data Classification | Entities | Retention Policy | Actions upon Expiration |
|---|---|---|---|---|
| **Tier 1: Permanent Compliance** | Certified inspection evidence and legal audit records | `inspections`, `defects`, `evidence_media`, `inspection_reports`, `audit_events` | Permanent (Indefinite) | Never automatically deleted. Soft-archival supported. |
| **Tier 2: High-Frequency Telemetry** | Raw 10-50 Hz sensor streams | `encoder_telemetry`, `imu_telemetry`, `device_heartbeats` | 60 to 90 Days | Downsampled to 1 Hz summary points or archived to compressed cold storage (`.parquet` / `.csv.gz`). |
| **Tier 3: Ephemeral Processing** | Intermediate video frames without defects | `camera_frames` (without linked defects), debug logs | 7 to 14 Days | Automatically dropped via scheduled partition detachment or cleanup cron job. |

*Safety Rule*: No inspection evidence or defect record may be permanently removed without an authenticated administrative request logged to `audit_events`.

---

## 9. Backup, Disaster Recovery and Verification Plan

### 9.1 Database Backup Strategy
1. **Daily Logical Backups**: Automated `pg_dump` executed daily at midnight, compressed with `gzip`, producing timestamped artifacts:
   `D:\PipeBot\backups\db\pipebot_db_YYYYMMDD_HHMMSS.sql.gz`
2. **Continuous WAL Archiving**: Write-Ahead Logs archived to `D:\PipeBot\backups\wal\` enabling Point-In-Time Recovery (PITR) up to the minute of failure.
3. **Backup Retention**: Daily backups retained for 30 days; weekly backups retained for 12 months.

### 9.2 Media Filesystem Backup
- Defect evidence crops (`backend/data/media/`) must be backed up concurrently with database dumps.
- Tools: `rsync` or local snapshotting preserving file timestamps.
- **Referential Consistency**: Database backup must complete immediately before or during media snapshotting to prevent database records pointing to missing snapshot files.

### 9.3 Disaster Recovery and Restore Testing
Backups are considered invalid until verified by automated restore testing:
- **Monthly Automated Restore Drill**: A test script restores the latest `pg_dump` into an ephemeral PostgreSQL instance, executes `SELECT count(*) FROM inspections`, verifies foreign-key integrity, and validates that sample evidence media paths exist on disk.
- **Disk Capacity Guard**: Automated health check monitors free disk space on `D:`. If available space drops below 15%, alerts are raised and automatic telemetry downsampling is triggered.

