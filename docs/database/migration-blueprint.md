# PipeBot Database Engineering: SQLite-to-PostgreSQL Migration Blueprint

## 1. Executive Summary

This document establishes the end-to-end migration blueprint for transitioning the PipeBot persistence tier from the current SQLite prototype (`backend/data/pipebot.db`) to the production PostgreSQL 16 schema.

This blueprint specifies the table mappings, schema creation sequence, data extraction and transformation pipeline, primary and foreign key preservation rules, cryptographic checksum reconciliations, rollback procedures, and downtime mitigation strategies.

**CRITICAL SAFEGUARD**: This document is an architectural blueprint. Migration execution is deferred to subsequent implementation stages. The existing SQLite database and Alembic migration scripts remain completely untouched.

---

## 2. Existing Table Mapping and Schema Transformation

The operational SQLite database currently contains two business tables managed by Alembic head `d4d255efae0c`. These tables map directly into the target schema:

### 2.1 Table: `inspections` Mapping

| Existing SQLite Column | Existing Type | Target PostgreSQL Column | Target Type | Transformation & Mapping Rule |
|---|---|---|---|---|
| `id` | INTEGER (PK) | `id` | BIGINT (PK) | Value preserved identically to retain surrogate key integrity. Sequence initialized to `MAX(id) + 1`. |
| `inspection_id` | VARCHAR(64) | `inspection_id` | VARCHAR(64) | Value preserved identically. Unique index applied (`uq_inspections_inspection_id`). |
| `pipe_identifier` | VARCHAR(128) | `pipe_identifier` | VARCHAR(128) | Preserved identically. |
| `pipe_material` | VARCHAR(64) | `pipe_material` | VARCHAR(64) | Preserved identically. Defaults to 'PVC' if empty. |
| `pipe_diameter_mm` | INTEGER | `pipe_diameter_mm` | INTEGER | Preserved identically. Check constraint applied: `> 0`. |
| `operator_id` | VARCHAR(64) | `operator_id` | VARCHAR(64) | Preserved identically. |
| `status` | VARCHAR(32) | `status` | VARCHAR(32) | Enforces check constraint: `status IN ('created','in_progress','paused','completed','failed','cancelled')`. |
| `started_at` | DATETIME | `started_at` | TIMESTAMPTZ | Converted via `UtcDateTime` normalization to offset-aware UTC. |
| `completed_at` | DATETIME | `completed_at` | TIMESTAMPTZ | Converted to offset-aware UTC. |
| `total_distance_meters`| FLOAT | `total_distance_meters`| DOUBLE PRECISION | Preserved identically. Check constraint: `>= 0.0`. |
| `notes` | TEXT | `notes` | TEXT | Preserved identically. |
| `is_archived` | BOOLEAN (0/1) | `is_archived` | BOOLEAN | Converted from integer 0/1 to native PostgreSQL boolean. |
| *(New in target)* | N/A | `is_deleted` | BOOLEAN | Initialized to `FALSE`. |
| `created_at` | DATETIME | `created_at` | TIMESTAMPTZ | Converted to offset-aware UTC. |
| `updated_at` | DATETIME | `updated_at` | TIMESTAMPTZ | Converted to offset-aware UTC. |

---

### 2.2 Table: `defects` Mapping

| Existing SQLite Column | Existing Type | Target PostgreSQL Column | Target Type | Transformation & Mapping Rule |
|---|---|---|---|---|
| `id` | INTEGER (PK) | `id` | BIGINT (PK) | Preserved identically. Sequence initialized to `MAX(id) + 1`. |
| `defect_id` | VARCHAR(64) | `defect_id` | VARCHAR(64) | Preserved identically. Unique index applied (`uq_defects_defect_id`). |
| `inspection_id` | INTEGER (FK) | `inspection_id` | BIGINT (FK) | Preserved identically. Foreign key references `inspections(id)` with `ON DELETE RESTRICT`. |
| `frame_id` | VARCHAR(64) | `frame_id` | VARCHAR(64) | Preserved identically. |
| *(New in target)* | N/A | `model_version_id` | BIGINT (FK) | Initialized to baseline YOLO model version record. |
| `defect_class` | VARCHAR(32) | `defect_class` | VARCHAR(32) | Validated against canonical set: `Deformation`, `Misalignment`, `Obstacle`, `Rupture`. Check constraint applied. |
| `confidence` | FLOAT | `confidence` | DOUBLE PRECISION | Preserved identically. Check constraint: `0.0 <= confidence <= 1.0`. |
| *(New in target)* | N/A | `severity` | VARCHAR(16) | Initialized to 'moderate' (or mapped from frontend severity if present). |
| `bounding_box` | JSON (Text) | `bounding_box` | JSONB | Migrated from SQLite text to native PostgreSQL JSONB with normalization verification. |
| `capture_timestamp` | DATETIME | `capture_timestamp` | TIMESTAMPTZ | Converted to offset-aware UTC. |
| `inference_timestamp`| DATETIME | `inference_timestamp` | TIMESTAMPTZ | Converted to offset-aware UTC. |
| `estimated_distance_meters`| FLOAT | `estimated_distance_meters`| DOUBLE PRECISION | Preserved. Nullable if synchronization is unverified. Check: `>= 0.0`. |
| `review_status` | VARCHAR(32) | `review_status` | VARCHAR(32) | Enforces canonical review states: `unreviewed`, `confirmed`, `rejected`, `reclassified`. |
| *(New in target)* | N/A | `reviewed_by` | VARCHAR(64) | Initialized to NULL unless operator notes indicate reviewer. |
| *(New in target)* | N/A | `reviewed_at` | TIMESTAMPTZ | Initialized to NULL unless reviewed. |
| `snapshot_path` | VARCHAR(256) | `snapshot_path` | VARCHAR(256) | Preserved identically. Verifies physical file presence under `backend/data/media/crops/`. |
| `notes` | TEXT | `notes` | TEXT | Preserved identically. |
| `is_deleted` | BOOLEAN (0/1) | `is_deleted` | BOOLEAN | Converted from integer 0/1 to native boolean. |
| `created_at` | DATETIME | `created_at` | TIMESTAMPTZ | Converted to offset-aware UTC. |
| `updated_at` | DATETIME | `updated_at` | TIMESTAMPTZ | Converted to offset-aware UTC. |

---

## 3. Strict DDL Table Creation Order

To honor foreign-key dependency trees and prevent creation failures, tables in PostgreSQL must be created in this exact topological order:

```text
  1. devices                               (Master hardware registry, no foreign keys)
  2. inspections                           (Core master inspection table)
  3. ai_model_versions                     (Vision model registry)
  4. device_sessions                       (Depends on devices and inspections)
  5. defects                               (Depends on inspections and ai_model_versions)
  6. evidence_media                        (Depends on defects)
  7. localization_records                  (Depends on defects)
  8. encoder_samples [Partitioned]         (Depends on inspections and device_sessions)
  9. imu_samples [Partitioned]             (Depends on inspections and device_sessions)
 10. camera_frames                         (Depends on inspections)
 11. device_heartbeats                     (Depends on device_sessions and devices)
 12. vehicle_status_events                 (Depends on inspections and device_sessions)
 13. inspection_events                     (Depends on inspections)
 14. inspection_summaries                  (Depends on inspections)
 15. inspection_reports                    (Depends on inspections)
 16. audit_events                          (Decoupled append-only audit trail)
```

---

## 4. Data Extraction, Transformation and Load (ETL) Sequence

The data migration from SQLite to PostgreSQL executes via an automated, idempotent migration script:

```text
+-------------------+        +----------------------+        +---------------------+
| SQLite Source DB  |  --->  | Python ETL Pipeline  |  --->  | PostgreSQL Target DB|
| (Read-Only State) |        | (Validation & Normal)|        | (Atomic Transaction)|
+-------------------+        +----------------------+        +---------------------+
```

### 4.1 Step-by-Step ETL Execution Plan
1. **Source State Lock**:
   - The backend service is set to maintenance mode or read-only mode.
   - The SQLite database file `backend/data/pipebot.db` is copied to a timestamped snapshot: `backend/data/pipebot_pre_migration_backup.db`.
2. **Schema Provisioning in PostgreSQL**:
   - Alembic runs the target migration revision creating all 16 tables, check constraints, and indexes in PostgreSQL.
3. **Data Extract & Transform**:
   - **Step A: Master Configurations**:
     - Insert default hardware record in `devices` (`id='esp32-crawler-default'`, `device_type='ESP32_WROOM'`).
     - Insert default YOLO model metadata record in `ai_model_versions` (`model_name='yolov8n-pipebot'`, `model_version='v1.0.0-baseline'`).
   - **Step B: Inspections ETL**:
     - Read all rows from SQLite `inspections`.
     - Normalize timestamps to strict UTC.
     - Validate `pipe_diameter_mm > 0`.
     - Bulk insert rows into PostgreSQL `inspections` with `OVERRIDING SYSTEM VALUE` to preserve existing integer `id` keys.
     - Reset sequence: `SELECT setval('inspections_id_seq', (SELECT MAX(id) FROM inspections));`.
   - **Step C: Defects ETL**:
     - Read all rows from SQLite `defects`.
     - Map `defect_class` to canonical strings (`Deformation`, `Misalignment`, `Obstacle`, `Rupture`).
     - Link `model_version_id` to default model record.
     - Bulk insert into PostgreSQL `defects`, preserving integer `id` keys.
     - Reset sequence: `SELECT setval('defects_id_seq', (SELECT MAX(id) FROM defects));`.
   - **Step D: Evidence Media Generation**:
     - For every defect with non-null `snapshot_path`, verify file presence on disk (`backend/data/media/crops/`).
     - Compute SHA-256 hash of each image file.
     - Insert matching rows into `evidence_media` linked to `defect_id`.
   - **Step E: Inspection Summaries Compilation**:
     - Compute and insert summary snapshots into `inspection_summaries` for all completed inspections.

---

## 5. Verification and Reconciliation Protocols

Before the new database can be designated active, it must pass three verification checks:

### 5.1 Row-Count and Checksum Reconciliation
A reconciliation script executes:
```python
# Verification query
assert sqlite_cur.execute("SELECT count(*) FROM inspections").fetchone()[0] == \
       pg_cur.execute("SELECT count(*) FROM inspections").fetchone()[0], "Inspection row count mismatch!"

assert sqlite_cur.execute("SELECT count(*) FROM defects").fetchone()[0] == \
       pg_cur.execute("SELECT count(*) FROM defects").fetchone()[0], "Defect row count mismatch!"
```

### 5.2 Referential Integrity Verification
PostgreSQL executes immediate constraint validation:
```sql
SELECT d.id, d.defect_id, d.inspection_id 
FROM defects d 
LEFT JOIN inspections i ON i.id = d.inspection_id 
WHERE i.id IS NULL;
```
*Result must be zero rows.*

### 5.3 On-Disk Evidence Media Verification
A file verification script iterates through all records in `evidence_media`:
- Verifies that `file_path` resolves to an existing file under `D:\PipeBot\backend\data\media\`.
- Verifies that `SHA256(file_bytes) == evidence_media.checksum_sha256`.
- Logs any missing or corrupted media files as reconciliation anomalies.

---

## 6. Rollback Strategy, Write Freeze and Cutover Protocol

### 6.1 Production Write-Freeze Protocol
Simply toggling `DATABASE_URL` after new write traffic has arrived at PostgreSQL does not constitute a valid rollback because new inspection writes, sensor logs, and defect reviews committed to PostgreSQL would be silently lost upon reverting to the older SQLite file.

A safe production cutover enforces a three-phase write-freeze protocol:
1. **Pre-Cutover Write Freeze**:
   - The backend service enables `MAINTENANCE_MODE = True`, rejecting new inspection creation or defect review mutation requests (`HTTP 503 Service Unavailable: Migration in Progress`).
   - Active crawler telemetry queues are flushed and closed.
2. **Deterministic Baseline Backup**:
   - An atomic filesystem snapshot of `backend/data/pipebot.db` is copied to `backend/data/pipebot_pre_migration_YYYYMMDD_HHMMSS.db`.
   - On-disk media crops in `backend/data/media/crops/` are verified against database records.
3. **Execution and Reconciliation Gate**:
   - ETL script executes migration into PostgreSQL.
   - Row-count checks and foreign-key verifications run.
   - If verification passes, `DATABASE_URL` is switched to PostgreSQL and write mode is re-enabled.

### 6.2 Rollback Protocols: Pre-Write vs. Post-Write Scenarios
1. **Scenario A: Failure During Cutover Window (Pre-Write Phase)**:
   - Before write traffic is re-enabled: Revert `DATABASE_URL` to the SQLite path, restart FastAPI, and lift maintenance mode. Because SQLite remained read-only during the cutover window, zero data loss occurs.
2. **Scenario B: Failure After Operational Writes Have Occurred (Post-Write Phase)**:
   - If a critical bug is discovered after hours of active operations on PostgreSQL, changing `DATABASE_URL` back to SQLite will destroy the newly accumulated inspection data.
   - *Required Action*: A reverse differential delta ETL must be executed:
     a. Place backend into emergency maintenance mode.
     b. Extract all inspections, defects, and events with `created_at >= cutover_timestamp` from PostgreSQL.
     c. Transform and insert these new delta records into the preserved SQLite database.
     d. Reset SQLite autoincrement sequences.
     e. Switch `DATABASE_URL` back to SQLite and restart backend.

