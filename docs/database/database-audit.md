# PipeBot Database Engineering: Subsystem Audit and Technology Evaluation

## 1. Executive Summary

This audit assesses the current data persistence tier of the PipeBot pipeline inspection platform. It reviews the active SQLite implementation, evaluates data integrity and concurrency constraints, identifies architectural bottlenecks under real-time robotics workloads, and defines a transition strategy toward an enterprise relational model.

The current backend operates a lightweight SQLite database managed by SQLAlchemy 2.0 and Alembic. While SQLite provides an zero-configuration environment for single-process testing and development, its single-writer locking architecture cannot sustain continuous high-frequency telemetry ingestion alongside concurrent operator API requests. 

This document outlines the current schema, analyzes existing limitations, evaluates PostgreSQL and TimescaleDB, and specifies the migration strategy required to achieve industrial reliability.

---

## 2. Existing Database Implementation

### 2.1 Technology Stack
- **Database Engine**: SQLite 3 (stored locally at `backend/data/pipebot.db`).
- **ORM / Query Layer**: SQLAlchemy 2.0 (`app.db.base.Base`, `DeclarativeBase`, `Mapped`, `mapped_column`).
- **Schema Migration Tool**: Alembic (configured with `render_as_batch=True` in `migrations/env.py` to navigate SQLite ALTER TABLE limitations).
- **Session Management**: Thread-safe `sessionmaker` with `autocommit=False`, `autoflush=False`, `expire_on_commit=False`, injected via FastAPI `Depends(get_db)`.
- **Integrity Enforcement**: Explicit SQLite connection event listener enforcing foreign keys:
  ```python
  @event.listens_for(Engine, "connect")
  def set_sqlite_pragma(dbapi_connection, connection_record):
      cursor = dbapi_connection.cursor()
      cursor.execute("PRAGMA foreign_keys=ON")
      cursor.close()
  ```
- **Timezone Normalization**: Custom SQLAlchemy `TypeDecorator` (`UtcDateTime`) ensuring all datetime values written to and read from SQLite are timezone-aware UTC objects (`tzinfo=timezone.utc`).

---

### 2.2 Current Database Schema Analysis

The current operational database contains exactly two domain tables and one migration tracking table:

```text
+-----------------------------------------------------------------------------------+
|                                  inspections                                      |
+-----------------------------------------------------------------------------------+
| id                    | INTEGER      | Primary Key, Autoincrement                 |
| inspection_id         | VARCHAR(64)  | Unique, Indexed, Public Identifier         |
| pipe_identifier       | VARCHAR(128) | Indexed, Target Conduit Tag                |
| pipe_material         | VARCHAR(64)  | Default 'PVC'                              |
| pipe_diameter_mm      | INTEGER      | Default 200 (150 mm to 300 mm range)       |
| operator_id           | VARCHAR(128) | Indexed, Technician Identifier             |
| status                | VARCHAR(32)  | Enum (created, in_progress, paused, ...)   |
| started_at            | DATETIME     | Nullable, UtcDateTime                      |
| completed_at          | DATETIME     | Nullable, UtcDateTime                      |
| total_distance_meters | FLOAT        | Nullable, Odometry Penetration             |
| notes                 | TEXT         | Nullable, Operator Remarks                 |
| is_archived           | BOOLEAN      | Default False, Indexed, Archival Flag      |
| created_at            | DATETIME     | UtcDateTime, Audit Creation Timestamp      |
| updated_at            | DATETIME     | UtcDateTime, Audit Modification Timestamp  |
+-----------------------------------------------------------------------------------+
                                          | 1
                                          |
                                          | Foreign Key: inspections.id (RESTRICT)
                                          v N
+-----------------------------------------------------------------------------------+
|                                     defects                                       |
+-----------------------------------------------------------------------------------+
| id                        | INTEGER      | Primary Key, Autoincrement             |
| defect_id                 | VARCHAR(64)  | Unique, Indexed, Public Identifier     |
| inspection_id             | INTEGER      | Indexed, Foreign Key -> inspections.id |
| frame_id                  | VARCHAR(128) | Indexed, Optical Frame Identifier      |
| defect_class              | VARCHAR(32)  | Enum (Deformation, Misalignment, ...)  |
| confidence                | FLOAT        | Nullable, Statistical Confidence (0-1) |
| bounding_box              | JSON         | Nullable, Normalized Bounding Box      |
| capture_timestamp         | DATETIME     | UtcDateTime, Frame Capture Instant     |
| inference_timestamp       | DATETIME     | Nullable, UtcDateTime, Server AI Time  |
| estimated_distance_meters | FLOAT        | Nullable, Spatial Odometry Offset      |
| review_status             | VARCHAR(32)  | Enum (pending, confirmed, rejected)    |
| snapshot_path             | VARCHAR(512) | Nullable, Relative URI to Evidence Crop|
| notes                     | TEXT         | Nullable, Engineering Notes            |
| is_deleted                | BOOLEAN      | Default False, Soft-Delete Audit Flag  |
| created_at                | DATETIME     | UtcDateTime, Audit Creation Timestamp  |
| updated_at                | DATETIME     | UtcDateTime, Audit Modification Timestamp|
+-----------------------------------------------------------------------------------+
```

---

### 2.3 Migration History
The database schema state is tracked by Alembic in `backend/migrations/versions/`:
1. `88f24fc2264d_create_inspection_and_defect_tables.py`:
   - Established initial `inspections` and `defects` tables with standard indexes.
   - Configured initial foreign key with `ondelete="CASCADE"`.
2. `d4d255efae0c_audit_safe_retention_and_utc_timestamps.py`:
   - Refactored `defects.inspection_id` foreign key from `CASCADE` to `RESTRICT` using Alembic batch mode.
   - Added `inspections.is_archived` boolean column with indexed default `False`.
   - Prevented accidental cascading deletion of inspection records and defect evidence.

---

## 3. Existing Database Limitations

While the current SQLite schema successfully supports CRUD operations and testing, an architectural audit reveals critical bottlenecks:

### 3.1 Single-Writer Database Lock Contention
- SQLite uses database-level locking during write operations (`database is locked` error under concurrency).
- If the backend attempts to write incoming wheel encoder packets, MPU6050 samples, or device heartbeats directly to SQLite, the database remains in a near-continuous write lock.
- Concurrently, operator API requests (such as defect review submissions, inspection status transitions, or dashboard queries) experience latency spikes or timeout failures.
- This is the fundamental technical reason why telemetry ingestion is currently handled in-process in `TelemetryStateService` rather than persisted to SQLite.

### 3.2 Complete Absence of Telemetry Persistence
- High-frequency rotary encoder measurements, IMU motion records, and vehicle electrical diagnostics are discarded after in-memory ring buffer eviction.
- Historical inspection replay, trajectory reconstruction, speed profile calculation, and post-inspection validation cannot be conducted from database records.

### 3.3 Lack of Native Partitioning and Time-Series Pruning
- SQLite lacks native table partitioning.
- Over weeks of field inspections, unpartitioned telemetry tables would grow into millions of contiguous rows, degrading B-tree index performance and making historical data purging computationally expensive.

### 3.4 Dynamic Typing and Constraint Enforcement Limits
- SQLite employs type affinity rather than strict static typing. Data types such as `BOOLEAN` and `DATETIME` are stored as integers or text strings without strict database-level format validation.
- Native enum types do not exist in SQLite; enum constraints rely on application-level checks or generated CHECK constraints.

### 3.5 Backup and Concurrency Risks During Active Writes
- Performing physical database file copies during active crawler inspections risks database corruption unless complex WAL checkpointing is executed.
- Single-file storage couples operational data with historical archives, increasing blast radius in the event of filesystem corruption.

---

## 4. Database Technology Evaluation

| Architecture Dimension | SQLite (Current) | PostgreSQL (Recommended Core) | TimescaleDB (Future Extension) | MongoDB / NoSQL (Evaluated) |
|---|---|---|---|---|
| Primary Use Case | Embedded / Edge Prototype | Industrial Relational Core | Heavy Time-Series Telemetry | Document Store |
| Write Concurrency | Single writer (file lock) | Multi-version Concurrency (MVCC) | Distributed Hypertables | Document-level locks |
| Foreign Key Integrity | PRAGMA event listener | Native, declarative, strict | Native PostgreSQL FKs | Application-level only |
| Telemetry Ingestion Rate | Low (< 50 writes/sec) | High (5,000 to 20,000 writes/sec) | Very High (100,000+ writes/sec) | High |
| Table Partitioning | None (Manual table split) | Native Declarative (Range/List) | Automated Hypertables | Sharding |
| Time-Series Compression | None | Block compression / ZSTD | Native columnar chunk compression | Snappy / WiredTiger |
| Analytical Window Functions| Basic SQLite subset | Comprehensive ANSI SQL | Advanced time-bucket functions | Aggregation pipelines |
| Operational Complexity | Minimal (Zero config) | Moderate (Docker / Service) | Higher (Postgres extension) | Moderate to High |
| Storage Location Control | Explicit D: drive path | Explicit volume mounting to D: | Explicit volume mounting to D: | Variable |

### 4.1 Evaluation Details

#### SQLite
- **Verdict**: Retain strictly as an offline standalone fallback and local testing harness.
- **Justification**: SQLite requires zero system daemons and enables automated pytest suites to run in isolated temporary databases (`tests/test_pipebot.db`) in under 6 seconds. However, it cannot serve as the production ingestion database for continuous multi-sensor telemetry.

#### PostgreSQL 16
- **Verdict**: Strongly recommended as the primary database architecture for PipeBot.
- **Justification**:
  - Full ACID compliance with Multi-Version Concurrency Control (MVCC) eliminates writer-reader lock contention.
  - Native declarative range partitioning allows telemetry tables to be partitioned by date or by `inspection_id`, keeping query execution plans fast.
  - Native JSONB support enables storage of structured bounding box coordinate history and variable hardware diagnostics while maintaining indexability via GIN indexes.
  - Native `TIMESTAMPTZ` enforces microsecond UTC timestamp precision across all records.
  - Connection pooling through PgBouncer or SQLAlchemy async pool easily sustains high-throughput asynchronous writes.

#### TimescaleDB (PostgreSQL Extension)
- **Verdict**: Deferred. Keep as an optional future upgrade path.
- **Justification**: TimescaleDB introduces automatic chunk management and columnar chunk compression. However, for a single inspection crawler prototype operating on a local processing computer, native PostgreSQL range partitioning is more than sufficient. Introducing TimescaleDB now adds operational deployment complexity without immediate technical necessity.

#### MongoDB / Document Stores
- **Verdict**: Rejected.
- **Justification**: PipeBot's core domain is relational and hierarchical: an inspection owns defects, which reference frames, which correlate with encoder samples, which are bound to specific vehicle hardware sessions. Relational referential integrity with restrictive foreign keys is essential to prevent orphan records and accidental audit deletion. Document stores sacrifice relational constraints for horizontal schema fluidity, which is counterproductive for regulatory pipeline compliance.

---

## 5. Recommended Architecture and Deployment Strategy

### 5.1 Dual-Tier Database Strategy
1. **Tier 1 (Production Relational Target)**: PostgreSQL 16 running locally via containerization or local service.
2. **Tier 2 (Development and Pytest Fallback)**: SQLite retained for lightweight unit testing, CI pipelines, and disconnected field laptops lacking Docker infrastructure.

### 5.2 Containerization and Docker Deployment
To maintain zero contamination of the Windows system drive (C:) and guarantee reproducible environments:
- The PostgreSQL service will be configured via a Docker Compose manifest located strictly at `D:\PipeBot\docker-compose.yml`.
- Data persistence volumes must be bound explicitly to the host project directory on drive D (e.g. `D:\PipeBot\backend\data\postgres_data`).
- Port mapping will bind exclusively to loopback (`127.0.0.1:5432`) to prevent unauthorized network exposure.
- Credentials must be loaded from `backend/.env` without hardcoded secrets.

---

## 6. Migration Risks and Mitigation Plan

| Risk Factor | Root Cause | Impact | Mitigation Strategy |
|---|---|---|---|
| Datetime Representation | SQLite stores datetimes as ISO strings; Postgres uses native 8-byte TIMESTAMPTZ. | Query comparison errors or timezone offset skew. | Standardize all models on `UtcDateTime` with `DateTime(timezone=True)`. Validate UTC normalization on ingestion. |
| Enum Value Representation | SQLite uses string varchar checks; Postgres uses native CREATE TYPE enum. | Migration downgrade failures or alter table lockups. | Use `Enum(native_enum=False, length=32)` in SQLAlchemy to store enums as validated VARCHARs, preserving cross-engine parity. |
| Foreign Key RESTRICT Behavior | SQLite requires PRAGMA foreign_keys=ON; Postgres enforces natively. | Tests passing on SQLite might fail on Postgres if constraints differ. | Alembic migrations explicitly specify `ondelete="RESTRICT"` with standardized constraint naming conventions. |
| Batch Mode Migration Syntax | Alembic batch mode is required for SQLite but redundant in Postgres. | Syntax incompatibilities during schema upgrade. | Configure `env.py` to check `context.get_x_argument()` or dialect name, applying batch mode conditionally on SQLite. |
| High Write Volume Lag | Ingesting 20 Hz to 50 Hz telemetry via individual INSERT statements exhausts database connections. | Connection pool starvation and dropped telemetry packets. | Implement in-memory telemetry buffer chunks in the service layer, writing telemetry to Postgres in batches of 100 to 500 rows inside a single transaction. |

