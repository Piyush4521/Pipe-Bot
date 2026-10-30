# PipeBot Database Engineering: Indexing Strategy and Query Optimization Plan

## 1. Executive Summary

This document defines the query performance profiles, indexing strategies, and time-series access patterns for the PipeBot database tier. 

High-frequency robotics platforms exhibit a fundamental tension between write throughput and read latency:
- Ingestion processes require minimal index overhead to maintain sustained 10 to 50 Hz telemetry ingestion without disk I/O bottlenecks.
- Operator dashboards and report compilation require rapid sub-100ms multi-table joins, spatial lookups, and chronological filtering.

This plan addresses this tension through selective B-tree composite indexing on transactional entities and ultra-lightweight Block Range Indexing (BRIN) on append-only time-series streams.

---

## 2. Core Query Patterns and Proposed Index Design

The system must optimize for 13 distinct query patterns across the inspection lifecycle:

### Pattern 1: Retrieve Single Inspection and Summary Metrics
- **Query Pattern**: Fetch inspection header details along with aggregated defect counts and status.
- **Access Profile**: Point lookup by Primary Key (`id`) or unique code (`inspection_code`).
- **Proposed SQL Template**:
  ```sql
  SELECT i.*, s.total_defects_count, s.overall_pipe_grade
  FROM inspections i
  LEFT JOIN inspection_summaries s ON s.inspection_id = i.id
  WHERE i.id = :inspection_id AND i.is_deleted = FALSE;
  ```
- **Recommended Index**:
  - Primary Key: `PRIMARY KEY (id)` (B-tree).
  - Unique Index: `CREATE UNIQUE INDEX uq_inspections_code ON inspections (inspection_code);`

### Pattern 2: Retrieve Inspections by Date Range
- **Query Pattern**: Dashboard inspection list filtered by date, ordered by newest first.
- **Access Profile**: Range scan on `created_at` or `started_at` with pagination (`LIMIT :limit OFFSET :offset`).
- **Proposed SQL Template**:
  ```sql
  SELECT * FROM inspections
  WHERE created_at >= :start_time AND created_at <= :end_time AND is_deleted = FALSE
  ORDER BY created_at DESC
  LIMIT 25 OFFSET 0;
  ```
- **Recommended Index**:
  - `CREATE INDEX idx_inspections_created_active ON inspections (created_at DESC) WHERE is_deleted = FALSE;`
  - *Optimization*: Partial index excludes soft-deleted rows, reducing index page footprint.

### Pattern 3: Retrieve Inspections by Status
- **Query Pattern**: Dashboard operator filter showing only active or archived runs.
- **Access Profile**: Equality lookup on low-cardinality status enum (`RUNNING`, `COMPLETED`, `ARCHIVED`).
- **Recommended Index**:
  - `CREATE INDEX idx_inspections_status_created ON inspections (status, created_at DESC) WHERE is_deleted = FALSE;`

### Pattern 4: Retrieve Defects for an Inspection
- **Query Pattern**: Defect table view on operator review screen for a selected inspection.
- **Access Profile**: Foreign-key join with ordering by distance or detection timestamp.
- **Proposed SQL Template**:
  ```sql
  SELECT d.*, m.file_path, m.storage_backend
  FROM defects d
  LEFT JOIN evidence_media m ON m.defect_id = d.id
  WHERE d.inspection_id = :inspection_id AND d.is_deleted = FALSE
  ORDER BY d.detected_at ASC;
  ```
- **Recommended Index**:
  - `CREATE INDEX idx_defects_inspection_detected ON defects (inspection_id, detected_at ASC) WHERE is_deleted = FALSE;`

### Pattern 5: Retrieve Defects by Class
- **Query Pattern**: Defect catalog filtering (e.g., show all `Rupture` occurrences across inspections or within one run).
- **Access Profile**: Multi-column filter on inspection and canonical defect class.
- **Recommended Index**:
  - `CREATE INDEX idx_defects_inspection_class ON defects (inspection_id, defect_class) WHERE is_deleted = FALSE;`

### Pattern 6: Retrieve Defects by Review Status
- **Query Pattern**: Operator queue filtering defects awaiting verification (`review_status = 'PENDING_REVIEW'`).
- **Access Profile**: Equality filter on review status.
- **Recommended Index**:
  - `CREATE INDEX idx_defects_review_queue ON defects (review_status, inspection_id) WHERE is_deleted = FALSE;`

### Pattern 7: Retrieve Detections Ordered by Estimated Distance
- **Query Pattern**: Pipeline spatial profile view (defects displayed along pipeline chainage).
- **Access Profile**: Range and sort on `estimated_distance_meters` where distance is valid.
- **Proposed SQL Template**:
  ```sql
  SELECT * FROM defects
  WHERE inspection_id = :inspection_id 
    AND estimated_distance_meters IS NOT NULL 
    AND is_deleted = FALSE
  ORDER BY estimated_distance_meters ASC;
  ```
- **Recommended Index**:
  - `CREATE INDEX idx_defects_inspection_distance ON defects (inspection_id, estimated_distance_meters ASC) WHERE estimated_distance_meters IS NOT NULL AND is_deleted = FALSE;`

### Pattern 8: Retrieve Encoder Telemetry within a Time Range
- **Query Pattern**: Odometry graph rendering and time-slice synchronization lookups.
- **Access Profile**: High-volume sequential range query on time-series telemetry.
- **Proposed SQL Template**:
  ```sql
  SELECT sequence_number, left_cumulative_ticks, right_cumulative_ticks, left_rpm, right_rpm, recorded_at
  FROM encoder_telemetry
  WHERE inspection_id = :inspection_id 
    AND recorded_at >= :start_time AND recorded_at <= :end_time
  ORDER BY recorded_at ASC;
  ```
- **Recommended Index Strategy**:
  - Partitioning Key: `inspection_id` (via range/list partition).
  - Time Index: `CREATE INDEX brin_encoder_recorded_at ON encoder_telemetry USING BRIN (recorded_at);`
  - *Rationale*: BRIN indexes require ~1% of the storage of B-tree indexes while providing fast page-range skipping for monotonically increasing timestamps.

### Pattern 9: Retrieve IMU Telemetry within a Time Range
- **Query Pattern**: Vibration, tilt, and stability graph rendering.
- **Access Profile**: High-volume sequential range query.
- **Proposed SQL Template**:
  ```sql
  SELECT accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, recorded_at
  FROM imu_telemetry
  WHERE inspection_id = :inspection_id 
    AND recorded_at >= :start_time AND recorded_at <= :end_time
  ORDER BY recorded_at ASC;
  ```
- **Recommended Index Strategy**:
  - Partitioning Key: `inspection_id`.
  - Time Index: `CREATE INDEX brin_imu_recorded_at ON imu_telemetry USING BRIN (recorded_at);`

### Pattern 10: Retrieve Camera Frames around Detection Timestamp
- **Query Pattern**: Temporal synchronization query locating the nearest video frame within +/- 500ms of an AI defect detection.
- **Access Profile**: Bi-directional proximity search on frame capture timestamp.
- **Proposed SQL Template**:
  ```sql
  SELECT * FROM camera_frames
  WHERE inspection_id = :inspection_id 
    AND capture_timestamp BETWEEN (:defect_time - INTERVAL '500 milliseconds') AND (:defect_time + INTERVAL '500 milliseconds')
  ORDER BY ABS(EXTRACT(EPOCH FROM (capture_timestamp - :defect_time))) ASC
  LIMIT 1;
  ```
- **Recommended Index**:
  - `CREATE INDEX idx_frames_inspection_capture ON camera_frames (inspection_id, capture_timestamp);`

### Pattern 11: Retrieve Device Sessions and Heartbeat History
- **Query Pattern**: Connection diagnostics showing RSSI drops, battery depletion, or hardware reboots.
- **Access Profile**: Join between sessions and periodic heartbeats.
- **Recommended Index**:
  - `CREATE INDEX idx_heartbeats_session_recorded ON device_heartbeats (session_id, recorded_at DESC);`

### Pattern 12: Generate Inspection Report
- **Query Pattern**: Analytical rollup query computing inspection statistics, defect distributions, and operational durations.
- **Access Profile**: Aggregate scan over an inspection's defects and metadata.
- **Proposed SQL Template**:
  ```sql
  SELECT 
    i.id,
    i.inspection_code,
    i.total_distance_meters,
    COUNT(d.id) AS total_defects,
    COUNT(CASE WHEN d.defect_class = 'Deformation' THEN 1 END) AS deformation_count,
    COUNT(CASE WHEN d.defect_class = 'Misalignment' THEN 1 END) AS misalignment_count,
    COUNT(CASE WHEN d.defect_class = 'Obstacle' THEN 1 END) AS obstacle_count,
    COUNT(CASE WHEN d.defect_class = 'Rupture' THEN 1 END) AS rupture_count,
    AVG(d.confidence) AS mean_defect_confidence
  FROM inspections i
  LEFT JOIN defects d ON d.inspection_id = i.id AND d.is_deleted = FALSE
  WHERE i.id = :inspection_id
  GROUP BY i.id;
  ```
- **Index Support**: Uses `idx_defects_inspection_detected` on `defects` and Primary Key on `inspections`. Query executes in sub-5ms.

### Pattern 13: Retrieve AI Model Versions Used in an Inspection
- **Query Pattern**: Audit compliance query identifying model weights and class mappings used during an automated inspection.
- **Access Profile**: Distinct join between defects and model versions.
- **Proposed SQL Template**:
  ```sql
  SELECT DISTINCT m.*
  FROM ai_model_versions m
  JOIN defects d ON d.model_version_id = m.id
  WHERE d.inspection_id = :inspection_id AND d.is_deleted = FALSE;
  ```
- **Recommended Index**:
  - `CREATE INDEX idx_defects_model_version ON defects (model_version_id);`

---

## 3. Write Throughput vs. Query Performance Trade-Off Analysis

In a high-frequency robotics database, excessive indexing directly degrades insert performance:
1. **The Cost of Indexes on Bulk Writes**:
   - Each secondary B-tree index requires random-access tree navigation and page splitting on every inserted row.
   - At 50 Hz telemetry ingestion (100 combined rows/sec across encoders and IMU), maintaining 5 B-tree indexes per table would require 500 index-page mutations per second, inducing heavy write amplification and disk I/O contention.
2. **Selective Indexing Principles for PipeBot**:
   - High-frequency telemetry tables (`encoder_telemetry`, `imu_telemetry`) MUST NOT have secondary B-tree indexes on individual measurement columns (`accel_x`, `gyro_z`, `ticks`).
   - Use BRIN indexes on `recorded_at` instead of B-tree indexes for time-series streams. A BRIN index only stores minimum and maximum values per 128 disk pages (1 MB block range), introducing virtually zero overhead during sequential appends.
   - Limit B-tree indexes strictly to foreign keys (`inspection_id`, `session_id`) and selective query predicates on low-volume tables (`inspections`, `defects`, `reports`).

---

## 4. Time-Series Query Optimization and Downsampling

When rendering telemetry graphs (odometry or IMU acceleration over time) on the frontend dashboard, fetching 180,000 raw samples for a 1-hour inspection causes excessive network transfer and browser DOM lag.

### 4.1 Server-Side Downsampling Pattern
The database query layer must support bucketing (downsampling) for visualization queries:
```sql
SELECT 
  time_bucket('1 second', recorded_at) AS time_bucket,
  AVG(left_rpm) AS avg_left_rpm,
  AVG(right_rpm) AS avg_right_rpm,
  MAX(left_cumulative_ticks) AS left_ticks,
  MAX(right_cumulative_ticks) AS right_ticks
FROM encoder_telemetry
WHERE inspection_id = :inspection_id
GROUP BY time_bucket
ORDER BY time_bucket ASC;
```
*(Note: In standard PostgreSQL 16 without TimescaleDB, `date_bin('1 second'::interval, recorded_at, '2026-01-01'::timestamptz)` provides identical native functionality).*

This downsampling reduces 36,000 rows to 600 points for a 10-minute chart, reducing payload size by 98% while preserving visual fidelity.

---

## 5. Summary Table: Index Catalog

| Table | Index Name | Index Type | Indexed Columns | Partial Condition / Notes |
|---|---|---|---|---|
| `inspections` | `pk_inspections` | B-tree | `(id)` | Primary Key |
| `inspections` | `uq_inspections_code` | B-tree | `(inspection_code)` | Unique constraint |
| `inspections` | `idx_inspections_created` | B-tree | `(created_at DESC)` | `WHERE is_deleted = FALSE` |
| `inspections` | `idx_inspections_status` | B-tree | `(status, created_at DESC)` | `WHERE is_deleted = FALSE` |
| `defects` | `pk_defects` | B-tree | `(id)` | Primary Key |
| `defects` | `idx_defects_insp_detected` | B-tree | `(inspection_id, detected_at ASC)` | `WHERE is_deleted = FALSE` |
| `defects` | `idx_defects_insp_class` | B-tree | `(inspection_id, defect_class)` | `WHERE is_deleted = FALSE` |
| `defects` | `idx_defects_review_queue` | B-tree | `(review_status, inspection_id)` | `WHERE is_deleted = FALSE` |
| `defects` | `idx_defects_distance` | B-tree | `(inspection_id, estimated_distance_meters ASC)` | `WHERE estimated_distance_meters IS NOT NULL AND is_deleted = FALSE` |
| `defects` | `idx_defects_model_version`| B-tree | `(model_version_id)` | Foreign Key lookup |
| `evidence_media` | `pk_evidence_media` | B-tree | `(id)` | Primary Key |
| `evidence_media` | `uq_media_file_path` | B-tree | `(file_path)` | Unique file path |
| `evidence_media` | `idx_media_defect` | B-tree | `(defect_id)` | Foreign Key join |
| `encoder_telemetry` | `pk_encoder_telemetry` | B-tree | `(id, inspection_id)` | Composite PK on partitioned table |
| `encoder_telemetry` | `brin_encoder_recorded`| BRIN | `(recorded_at)` | Low overhead sequential time index |
| `imu_telemetry` | `pk_imu_telemetry` | B-tree | `(id, inspection_id)` | Composite PK on partitioned table |
| `imu_telemetry` | `brin_imu_recorded` | BRIN | `(recorded_at)` | Low overhead sequential time index |
| `camera_frames` | `pk_camera_frames` | B-tree | `(id, inspection_id)` | Composite PK on partitioned table |
| `camera_frames` | `idx_frames_capture` | B-tree | `(inspection_id, capture_timestamp)` | Temporal frame matching |
| `device_heartbeats`| `idx_heartbeats_session`| B-tree | `(session_id, recorded_at DESC)` | Device telemetry lookup |
| `audit_events` | `idx_audit_recorded` | B-tree | `(recorded_at DESC)` | Audit log timeline scan |

