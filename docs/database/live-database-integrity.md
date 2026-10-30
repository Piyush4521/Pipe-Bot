# PipeBot Database Engineering: Active Database Integrity and Audit Report

## 1. Executive Summary

This report documents the empirical audit of the active PipeBot SQLite database located at `D:\PipeBot\backend\data\pipebot.db`. In accordance with engineering instructions, this inspection was conducted in strict read-only mode (`file:... ?mode=ro`) without executing any DDL, DML, migration, downgrade, reset, or cleanup commands.

The audit resolves contradictions in prior reports and provides a factual, evidence-backed assessment of the active database file, schema state, record counts, and referential integrity.

---

## 2. Active Database Configuration and Resolution

| Parameter | Configuration Source | Resolved Value | Verification Status |
|---|---|---|---|
| **Configured Database URL** | `backend/.env` | `"sqlite:///./data/pipebot.db"` | Verified |
| **Filesystem Path** | Relative path resolution | `D:\PipeBot\backend\data\pipebot.db` (`/mnt/d/PipeBot/backend/data/pipebot.db`) | Verified |
| **File Existence** | Filesystem probe | `True` | Verified |
| **File Size** | Filesystem `stat().st_size` | `319,488 bytes` (~312 KB) | Verified |
| **Last Modified Timestamp** | Filesystem `stat().st_mtime` | `2026-10-30T18:29:29.271379+00:00` (UTC) | Recorded |

---

## 3. Schema State and Alembic Revision

- **Alembic Version Table**: `alembic_version` contains exactly one row:
  - `version_num`: `'d4d255efae0c'`
- **Table Inventory**: 17 total tables are present in `sqlite_master`:
  1. `alembic_version` (Alembic tracking)
  2. `inspections` (Active operational inspection master)
  3. `defects` (Active operational defect evidence)
  4. `ai_model_versions` (Empty table, 0 rows)
  5. `audit_events` (Empty table, 0 rows)
  6. `camera_frames` (Empty table, 0 rows)
  7. `device_heartbeats` (Empty table, 0 rows)
  8. `device_sessions` (Empty table, 0 rows)
  9. `devices` (Empty table, 0 rows)
  10. `encoder_samples` (Empty table, 0 rows)
  11. `evidence_media` (Empty table, 0 rows)
  12. `imu_samples` (Empty table, 0 rows)
  13. `inspection_events` (Empty table, 0 rows)
  14. `inspection_reports` (Empty table, 0 rows)
  15. `inspection_summaries` (Empty table, 0 rows)
  16. `localization_records` (Empty table, 0 rows)
  17. `vehicle_status_events` (Empty table, 0 rows)

---

## 4. Record Counts and Operational Data Verification

Every table was queried for exact record counts:

| Table Name | Row Count | Contents Description |
|---|---|---|
| `alembic_version` | 1 | Revision marker `d4d255efae0c`. |
| `inspections` | 1 | Completed baseline inspection session (`INSP-20261030-9F5A7F`). |
| `defects` | 1 | Confirmed Rupture defect detection (`DEF-20261030-B23056`). |
| `ai_model_versions` | 0 | Empty. |
| `audit_events` | 0 | Empty. |
| `camera_frames` | 0 | Empty. |
| `device_heartbeats` | 0 | Empty. |
| `device_sessions` | 0 | Empty. |
| `devices` | 0 | Empty. |
| `encoder_samples` | 0 | Empty. |
| `evidence_media` | 0 | Empty. |
| `imu_samples` | 0 | Empty. |
| `inspection_events` | 0 | Empty. |
| `inspection_reports` | 0 | Empty. |
| `inspection_summaries` | 0 | Empty. |
| `localization_records` | 0 | Empty. |
| `vehicle_status_events`| 0 | Empty. |

### Detailed Record Inspection (Without Exposing Secrets)
1. **Inspection Record**:
   - `id`: `1`
   - `inspection_id`: `'INSP-20261030-9F5A7F'`
   - `pipe_identifier`: `'PVC-LIVE-001'`
   - `pipe_material`: `'PVC'`
   - `pipe_diameter_mm`: `200`
   - `operator_id`: `'TECH-LIVE'`
   - `status`: `'completed'`
   - `started_at`: `'2026-10-30 15:31:30.925330'`
   - `completed_at`: `'2026-10-30 15:32:08.546121'`
   - `total_distance_meters`: `15.3`
   - `notes`: `'Live server test run\nRun completed successfully'`
   - `is_archived`: `0` (False)
2. **Defect Record**:
   - `id`: `1`
   - `defect_id`: `'DEF-20261030-B23056'`
   - `inspection_id`: `1`
   - `frame_id`: `'FRAME-LIVE-0001'`
   - `defect_class`: `'rupture'`
   - `confidence`: `0.94`
   - `bounding_box`: `'{"x": 0.35, "y": 0.4, "width": 0.2, "height": 0.15}'`
   - `capture_timestamp`: `'2026-10-30 15:31:32.000000'`
   - `inference_timestamp`: `None`
   - `estimated_distance_meters`: `8.75`
   - `review_status`: `'confirmed'`
   - `snapshot_path`: `None`
   - `notes`: `'Live test rupture detected\nReview note (confirmed): Confirmed rupture by operator'`
   - `is_deleted`: `0` (False)

---

## 5. Comparison with Historical Baseline

- **Data Integrity**: The operational data rows in `inspections` and `defects` remain identical to the live verification baseline established at the conclusion of backend development.
- **Historical Equivalence Caveat**: During Stage 3 development, an isolated test fixture executed an upgrade before configuration isolation was finalized, after which a downgrade to `d4d255efae0c` was executed. Consequently, while the database version marker is `d4d255efae0c` and the core tables contain the expected baseline data, additional empty table structures exist in the file.
- **Statement of Fact**: Historical byte-for-byte schema equivalence to the original two-table state cannot be claimed. However, zero operational data was lost, all baseline inspection and defect records remain intact, and no orphaned foreign keys exist.

---

## 6. SQLite Engine and Referential Integrity Checks

1. **Database Page and B-Tree Integrity**:
   - Query: `PRAGMA integrity_check;`
   - Result: `[('ok',)]`
   - Assessment: Database file is healthy with zero structural or B-tree corruption.
2. **Foreign-Key Constraint Enforcement**:
   - Query: `PRAGMA foreign_key_check;`
   - Result: `[]` (Empty list)
   - Assessment: 100% of foreign-key references are valid. There are zero orphaned child records.

---

## 7. Operating Rules for Final Stage

To ensure complete stability and safety:
1. No DDL commands (`DROP`, `ALTER`, `TRUNCATE`) will be executed against `backend/data/pipebot.db`.
2. No Alembic upgrade or downgrade commands will be run against `backend/data/pipebot.db`.
3. All persistence integration tests, benchmark measurements, migration validations, and backup/restore tests will execute exclusively against isolated temporary test databases.
4. The active database remains in service for the FastAPI application.

