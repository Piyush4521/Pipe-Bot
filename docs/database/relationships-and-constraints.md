# PipeBot Database Engineering: Relationships, Constraints and Referential Integrity

## 1. Executive Summary

This document specifies the referential integrity rules, foreign-key cascade behaviors, check constraints, transaction boundaries, and audit preservation policies for the PipeBot database tier.

In pipeline inspection and regulatory engineering, data permanence is a legal requirement. Accidental or cascading deletion of inspection records destroys photographic evidence and structural anomaly histories. The PipeBot logical schema strictly enforces non-destructive data handling:
- Destructive cascading deletions on inspection records, defects, and evidence media are prohibited (`ON DELETE RESTRICT`).
- Soft archival (`is_archived`) and soft deletion (`is_deleted`) maintain operational views while keeping historical compliance data permanently accessible.
- Microsecond-accurate timestamp ordering and check constraints guarantee physical validity across all sensor and computer vision readings.

---

## 2. Foreign Key Referential Actions Matrix

The table below defines every foreign-key relationship, parent-child cardinality, and explicit deletion behavior:

| Child Table | Foreign Key Column | Parent Table | Parent Key | On Delete Action | On Update Action | Rationale and Integrity Guarantee |
|---|---|---|---|---|---|---|
| `defects` | `inspection_id` | `inspections` | `id` | **RESTRICT** | CASCADE | Critical audit rule: an inspection cannot be deleted if defects are registered. Soft archival must be used instead. |
| `defects` | `model_version_id` | `ai_model_versions` | `id` | **RESTRICT** | CASCADE | Prevents deletion of AI model configurations referenced by historical defect detections. |
| `evidence_media` | `defect_id` | `defects` | `id` | **RESTRICT** | CASCADE | Defect evidence crops on disk must never be orphaned or severed from their defect metadata. |
| `localization_records` | `defect_id` | `defects` | `id` | **RESTRICT** | CASCADE | Spatial localization data must remain tied to the anomaly detection. |
| `inspection_events` | `inspection_id` | `inspections` | `id` | **RESTRICT** | CASCADE | Milestone history must be preserved for regulatory audit trails. |
| `inspection_reports` | `inspection_id` | `inspections` | `id` | **RESTRICT** | CASCADE | Official compliance certificates cannot be deleted while inspection runs exist. |
| `encoder_samples` | `inspection_id` | `inspections` | `id` | **RESTRICT** | CASCADE | Telemetry records cannot be deleted while parent inspection is active. Partition detachment handles bulk aging. |
| `imu_samples` | `inspection_id` | `inspections` | `id` | **RESTRICT** | CASCADE | High-rate IMU records cannot be individually deleted; tied to inspection lifecycle. |
| `camera_frames` | `inspection_id` | `inspections` | `id` | **RESTRICT** | CASCADE | Frame metadata records remain tied to the active inspection run. |
| `device_sessions` | `device_id` | `devices` | `id` | **RESTRICT** | CASCADE | Registered hardware controllers cannot be removed if historical sessions exist. |
| `device_sessions` | `inspection_id` | `inspections` | `id` | **SET NULL** | CASCADE | Hardware disconnection or session termination outside an active run leaves inspection null. |
| `device_heartbeats` | `session_id` | `device_sessions` | `id` | **CASCADE** | CASCADE | Ephemeral diagnostic heartbeats (RSSI, battery, heap) can be safely purged when an aged session is cleaned. |
| `inspection_summaries` | `inspection_id` | `inspections` | `id` | **CASCADE** | CASCADE | Summary snapshot table is a 1-to-1 extension of inspections; cascades upon inspection purge. |
| `audit_events` | *(None)* | *(None)* | *(None)* | **NONE** | NONE | Intentionally decoupled from foreign keys to guarantee audit records survive table truncation or partition drops. |

---

## 3. Detailed Deletion and Archival Semantics

### 3.1 Prohibition of Destructive Cascading Deletions
Earlier backend iterations utilized SQLAlchemy `cascade="all, delete-orphan"` and SQLite `ondelete="CASCADE"`. This allowed an operator deleting an inspection session to silently eradicate all associated defect evidence, bounding boxes, and photographic crops.

As corrected in Alembic revision `d4d255efae0c` and enforced in this logical schema:
1. **RESTRICT Enforcement**: If an operator or automated script attempts an SQL `DELETE FROM inspections WHERE id = :id`, the database engine immediately raises a foreign key violation (`IntegrityError`) if any defect, event, or report exists.
2. **Soft Archival Workflow**: In normal operations, completing or retiring an inspection executes:
   ```sql
   UPDATE inspections 
   SET is_archived = TRUE, updated_at = CURRENT_TIMESTAMP 
   WHERE id = :id;
   ```
   Archived inspections are excluded from active dashboard lists by default (`WHERE is_archived = FALSE AND is_deleted = FALSE`), but remain retrievable via historical search and reporting endpoints.
3. **Soft Deletion Workflow**: If an operator explicitly requests defect removal (e.g. dismissing an unverified anomaly):
   ```sql
   UPDATE defects 
   SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP 
   WHERE id = :id;
   ```
   The record remains in the database for compliance audits, and the corresponding crop image file on disk is preserved.

---

## 4. Database Check Constraints Catalog

To enforce business and physical laws at the database layer, explicit check constraints are defined for PostgreSQL and SQLite:

### 4.1 Defect Class and Confidence Constraints
- **Canonical Class Validation**:
  `CONSTRAINT ck_defects_defect_class CHECK (defect_class IN ('Deformation', 'Misalignment', 'Obstacle', 'Rupture'))`
  *Guarantee*: Prevents lowercase variants, informal synonyms, or unauthorized class strings from polluting the database.
- **Confidence Bounds**:
  `CONSTRAINT ck_defects_confidence CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0))`
  *Guarantee*: Eliminates negative confidence values or out-of-bounds floating-point scores.
- **Normalized Bounding Box Bounds** (when extracted or validated):
  `CONSTRAINT ck_defects_box_x CHECK (box_x IS NULL OR (box_x >= 0.0 AND box_x <= 1.0))`
  `CONSTRAINT ck_defects_box_y CHECK (box_y IS NULL OR (box_y >= 0.0 AND box_y <= 1.0))`
  `CONSTRAINT ck_defects_box_width CHECK (box_width IS NULL OR (box_width > 0.0 AND box_width <= 1.0))`
  `CONSTRAINT ck_defects_box_height CHECK (box_height IS NULL OR (box_height > 0.0 AND box_height <= 1.0))`
  *Guarantee*: Confirms that bounding box coordinates remain strictly inside normalized image boundaries.

### 4.2 Distance and Geometry Constraints
- **Estimated Conduit Distance**:
  `CONSTRAINT ck_defects_distance CHECK (estimated_distance_meters IS NULL OR estimated_distance_meters >= 0.0)`
  `CONSTRAINT ck_inspections_distance CHECK (total_distance_meters IS NULL OR total_distance_meters >= 0.0)`
  `CONSTRAINT ck_encoder_distance CHECK (estimated_distance_meters IS NULL OR estimated_distance_meters >= 0.0)`
  *Guarantee*: Prevents negative penetration distance values.
- **Pipe Diameter**:
  `CONSTRAINT ck_inspections_diameter CHECK (pipe_diameter_mm > 0)`
  *Guarantee*: Requires physical pipe diameter to be a strictly positive integer.

### 4.3 Inspection Status and Review State Constraints
- **Inspection Lifecycle State**:
  `CONSTRAINT ck_inspections_status CHECK (status IN ('created', 'in_progress', 'paused', 'completed', 'failed', 'cancelled'))`
  *Guarantee*: Validates that only authorized state machine transitions are committed.
- **Defect Review Status**:
  `CONSTRAINT ck_defects_review_status CHECK (review_status IN ('unreviewed', 'confirmed', 'rejected', 'reclassified'))`
  *Guarantee*: Enforces controlled review stages matching frontend operator actions.

---

## 5. Domain Boundaries and ACID Transaction Guarantees

Data modifications across multiple tables must be wrapped in atomic transactions to guarantee that partial failures never leave corrupted or orphaned data.

### 5.1 Defect Detection Ingestion Boundary
When the vision processing service detects a pipeline anomaly:
1. Validates frame existence and AI model configuration.
2. Crops the bounding box from the optical frame and saves the JPEG image to `backend/data/media/crops/insp_{id}/def_{id}.jpg`.
3. Opens an atomic database transaction:
   - Inserts `defects` row.
   - Inserts `evidence_media` row with file path, image dimensions, and SHA-256 checksum.
   - Inserts `localization_records` row if clock synchronization is verified.
   - Commits the transaction.
4. **Rollback Compensation**: If the database transaction fails (e.g. unique constraint collision or connection loss), the service executes a rollback and immediately deletes the newly written crop file from disk. This guarantees that disk storage never contains orphaned image files without matching database records.

### 5.2 Inspection Completion and Summary Boundary
When an operator marks an inspection as completed:
1. Opens an atomic transaction.
2. Updates `inspections.status = 'completed'` and sets `completed_at = CURRENT_TIMESTAMP`.
3. Aggregates all verified defects and computes `total_defects_count`, individual class counts, and overall pipe grade.
4. Upserts the `inspection_summaries` row.
5. Inserts an `inspection_events` record logging the transition and operator ID.
6. Commits the transaction.

---

## 6. Audit Logging and Non-Repudiation Architecture

The `audit_events` table operates under strict append-only rules:
- **No Direct Update or Delete APIs**: The application exposes no REST endpoints for updating or deleting audit event records.
- **Trigger-Level Protection (PostgreSQL)**:
  In production PostgreSQL, a database trigger rejects any `UPDATE` or `DELETE` statements on `audit_events`:
  ```sql
  CREATE OR REPLACE FUNCTION prevent_audit_tampering()
  RETURNS TRIGGER AS $$
  BEGIN
    RAISE EXCEPTION 'Audit trail records are immutable and cannot be updated or deleted.';
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER trg_audit_immutable
  BEFORE UPDATE OR DELETE ON audit_events
  FOR EACH ROW EXECUTE FUNCTION prevent_audit_tampering();
  ```
- **Contextual Captures**: Every administrative change (inspection archival, manual defect distance override, class reclassification) captures `performed_by`, `client_ip`, and full serialized `before_state` and `after_state` JSON snapshots.

