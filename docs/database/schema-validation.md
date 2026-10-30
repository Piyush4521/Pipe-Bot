# PipeBot Database Engineering: Schema Validation and Compatibility Verification

## 1. Executive Overview

This document presents the empirical validation results for the PipeBot Stage 3 schema implementation. It records the automated verification of all 16 domain tables, foreign key constraints, unique indexes, SQLite rowid auto-increment behavior, UTC timestamp handling, canonical defect class parsing, and reversible Alembic migration lifecycles.

---

## 2. Table and Relationship Verification Matrix

| Entity Name | Primary Key | Key Foreign Keys | Unique Constraints | Status |
|---|---|---|---|---|
| `inspections` | `id` (BigIntId) | None | `inspection_id` | Verified in SQLite & Metadata |
| `defects` | `id` (BigIntId) | `inspection_id` (RESTRICT), `model_version_id` (RESTRICT) | `defect_id` | Verified in SQLite & Metadata |
| `inspection_events` | `id` (BigIntId) | `inspection_id` (RESTRICT) | None | Verified in SQLite & Metadata |
| `inspection_summaries`| `inspection_id` | `inspection_id` (CASCADE) | None | Verified in SQLite & Metadata |
| `devices` | `id` (VARCHAR) | None | `mac_address` | Verified in SQLite & Metadata |
| `device_sessions` | `id` (BigIntId) | `device_id` (RESTRICT), `inspection_id` (SET NULL) | `session_uuid` | Verified in SQLite & Metadata |
| `device_heartbeats` | `id` (BigIntId) | `session_id` (CASCADE), `device_id` (RESTRICT) | None | Verified in SQLite & Metadata |
| `vehicle_status_events`| `id` (BigIntId) | `inspection_id` (RESTRICT), `session_id` (SET NULL) | None | Verified in SQLite & Metadata |
| `encoder_samples` | `id` (BigIntId) | `inspection_id` (RESTRICT), `session_id` (SET NULL) | None | Verified in SQLite & Metadata |
| `imu_samples` | `id` (BigIntId) | `inspection_id` (RESTRICT), `session_id` (SET NULL) | None | Verified in SQLite & Metadata |
| `camera_frames` | `id` (BigIntId) | `inspection_id` (RESTRICT) | `frame_id` | Verified in SQLite & Metadata |
| `evidence_media` | `id` (BigIntId) | `defect_id` (RESTRICT) | `media_uuid`, `file_path` | Verified in SQLite & Metadata |
| `ai_model_versions` | `id` (BigIntId) | None | `model_version` | Verified in SQLite & Metadata |
| `localization_records`| `id` (BigIntId) | `defect_id` (RESTRICT) | None | Verified in SQLite & Metadata |
| `inspection_reports` | `id` (BigIntId) | `inspection_id` (RESTRICT) | `report_id`, `file_path` | Verified in SQLite & Metadata |
| `audit_events` | `id` (BigIntId) | None (Decoupled) | None | Verified in SQLite & Metadata |

---

## 3. SQLite Compatibility Verification

All tests executed against isolated SQLite test databases with `PRAGMA foreign_keys = ON`:
1. **Auto-Increment Verification**:
   - `BigIntId` compiles to `INTEGER PRIMARY KEY` on SQLite, aliasing rowid.
   - Verified that inserting multiple records without explicit IDs produces monotonic sequential IDs (1, 2, 3...) rather than random or null values.
2. **Foreign-Key Violation Rejection**:
   - Verified that attempting to insert child records (`inspection_events`, `encoder_samples`) referencing a non-existent parent `inspection_id` raises an immediate `IntegrityError`.
3. **Unique Constraint Rejection**:
   - Verified that duplicate `mac_address`, `inspection_id`, or `file_path` values raise an immediate `IntegrityError`.
4. **UTC Timestamp Normalization**:
   - Verified that naive datetimes and offset-aware datetimes stored via `UtcDateTime` are returned as timezone-aware UTC objects with `tzinfo=timezone.utc`.
5. **Raw Telemetry Storage**:
   - Verified that `encoder_samples` and `imu_samples` store raw pulse counts and LSB values with derived metrics (`left_rpm`, `speed_mps`, `pitch_deg`) set to `NULL`.

---

## 4. PostgreSQL 16 Compatibility Analysis

Because PostgreSQL is not installed in the local environment, compatibility was verified by programmatic compilation of SQLAlchemy DDL against the `postgresql` dialect:
- **BigInt Primary Keys**: Compiles to `BIGSERIAL NOT NULL PRIMARY KEY`.
- **Foreign Keys**: Compiles to `BIGINT` foreign keys referencing parent `BIGINT` columns.
- **Timestamps**: Compiles to `TIMESTAMP WITH TIME ZONE`.
- **JSON Fields**: Compiles to native `JSON` / `JSONB`.
- **Untested Items**: Live PostgreSQL query execution, multi-user lock contention under `asyncpg`, and connection pool sizing remain untested until Dockerized PostgreSQL is provisioned in subsequent stages.

---

## 5. Automated Test Results

### 5.1 Isolated Schema Test Suite (`tests/test_schema_implementation.py`)
- `test_all_sixteen_tables_created_in_metadata`: PASSED
- `test_sqlite_integer_primary_keys_auto_increment`: PASSED
- `test_existing_inspection_and_defect_models_functional`: PASSED
- `test_foreign_keys_reject_invalid_references`: PASSED
- `test_unique_constraints_reject_duplicates`: PASSED
- `test_canonical_defect_classes_preserved`: PASSED
- `test_utc_timestamp_handling`: PASSED
- `test_nullable_localization_behavior`: PASSED
- `test_raw_telemetry_stored_without_fabricated_calibration`: PASSED
- `test_media_metadata_stores_relative_paths_and_checksums`: PASSED
- `test_alembic_upgrade_and_downgrade_isolated_db`: PASSED
- **Result**: 11 passed in 8.10s.

### 5.2 Complete Backend Regression Test Suite
- **Total Backend Tests**: 110 passed in 19.02s (100% pass rate).
- **Existing API & Service Tests**: 99 passed with zero regressions.

### 5.3 Complete Frontend Regression Test Suite
- `npm test` (`scripts/verify-frontend.mjs`): 16 passed in 173ms (100% pass rate).

---

## 6. Live Database State Confirmation

- Operational Database Path: `D:\PipeBot\backend\data\pipebot.db`
- Current Alembic Revision: `d4d255efae0c` (unmigrated and preserved).
- Migration `e7f8a9b0c1d2` exists as a versioned migration script ready for deployment in future stages.

