# PipeBot Database Engineering: Logical Database Schema Design

## 1. Executive Summary

This document establishes the implementation-ready logical schema design for PipeBot, transitioning the system from the initial two-table SQLite prototype to an industrial-grade, multi-domain relational architecture.

The logical schema reconciles the Stage 1 conceptual architecture with the authoritative implementation of the existing backend (`backend/app/models/`, `backend/app/schemas/`, `backend/migrations/`) and frontend contracts (`src/types/index.ts`). It bridges the operational requirements of high-frequency robotics telemetry (10 to 50 Hz) and real-time computer vision with strict regulatory compliance, non-destructive audit preservation, and zero-downtime migration readiness.

---

## 2. Architecture Principles and Reconciliation

### 2.1 Reconciling Stage 1 Blueprints with Codebase Reality
During Stage 1, conceptual blueprints proposed general UUID keys and theoretical entity divisions. The detailed logical design reconciles these proposals against the active, verified implementation:
1. **Dual Identifier Pattern**:
   - The existing SQLite schema utilizes an autoincrement integer `id` as the physical surrogate primary key, alongside a mandatory, unique, business-facing public identifier string (`inspection_id` e.g., `INSP-20261030-ABC123`, and `defect_id` e.g., `DEF-20261030-XYZ789`).
   - The API layer supports dual lookups by both internal integer ID and public string ID.
   - *Design Decision*: The logical schema retains the physical integer/bigint primary key (`id`) for high-performance internal joins and index compactness, while enforcing unique indexes on the public UUID/string business keys. This preserves full backward compatibility with existing FastAPI endpoints.
2. **Defect Entity Naming and Canonical Schema**:
   - The database table is canonically named `defects` (matching SQLAlchemy `__tablename__ = "defects"` and migration `d4d255efae0c`), while API responses map to the frontend `DefectDetection` contract.
   - Canonical defect classes are strictly preserved: `Deformation` (0), `Misalignment` (1), `Obstacle` (2), `Rupture` (3). No alternative lowercase variants or synonyms are introduced into the database layer.
3. **Evidence Media Decoupling**:
   - Raw video is never stored in database BLOBs.
   - Frame metadata and localized defect crops are decoupled: `camera_frames` logs optical capture diagnostics, while `evidence_media` tracks cropped anomaly evidence files on disk (`backend/data/media/crops/`) with relative POSIX paths and SHA-256 hashes.
4. **Dual-Engine Compatibility**:
   - The logical schema is structured so that the existing SQLite engine remains fully functional during local field development, while PostgreSQL 16 advanced capabilities (declarative partitioning, BRIN indexing, JSONB operators) can be deployed cleanly via Alembic in future stages.

---

## 3. Domain Model and Entity Inventory

The logical schema spans seven cohesive functional domains comprising 14 core tables and two analytical views/snapshot tables:

```text
+---------------------------------------------------------------------------------------------------+
|                                      PipeBot Logical Schema                                       |
+---------------------------------------------------------------------------------------------------+

 [INSPECTION DOMAIN]
   - inspections                    (Core master record of conduit runs)
   - inspection_events             (Lifecycle and operational milestone events)
   - inspection_summaries          (Denormalized post-run summary snapshot)

 [HARDWARE & SESSION DOMAIN]
   - devices                       (Physical controller and sensor registry)
   - device_sessions               (Continuous boot/connection instances)
   - device_heartbeats             (Periodic RSSI, battery, heap telemetry)
   - vehicle_status_events         (Motor actuation and safety state events)

 [TELEMETRY DOMAIN]
   - encoder_samples               (Dual wheel cumulative ticks, speed, distance)
   - imu_samples                   (MPU6050 6-axis acceleration, gyro, angles)

 [CAMERA & MEDIA DOMAIN]
   - camera_frames                 (Optical capture metadata and status)
   - evidence_media                (Cropped defect snapshot file registry)

 [AI & DEFECT DOMAIN]
   - ai_model_versions             (YOLO weights metadata, config, checksums)
   - defects                       (Verified anomalies, bounding boxes, reviews)

 [LOCALIZATION DOMAIN]
   - localization_records          (Optical-to-odometry temporal matching)

 [REPORTING & AUDIT DOMAIN]
   - inspection_reports            (Compiled PDF/JSON report registry)
   - audit_events                  (Immutable system administration audit log)
```

---

## 4. Entity Categorization: Core vs. Optional Future

To avoid schema bloat and premature complexity, entities are strictly partitioned into **Core Phase** (necessary for immediate telemetry, AI detection, and inspection workflows) and **Optional Future** (deferred to fleet operations):

| Domain | Table Name | Status | Rationale for Inclusion |
|---|---|---|---|
| Inspection | `inspections` | Core | Central root entity tracking pipe geometry, status, and audit timestamps. |
| Inspection | `inspection_events` | Core | Captures state machine transitions (`created`, `in_progress`, `paused`, `completed`, `cancelled`). |
| Inspection | `inspection_summaries` | Core (Snapshot) | Denormalizes defect counts and compliance grades for rapid dashboard rendering without expensive joins. |
| Hardware | `devices` | Core | Master registry of physical hardware units (ESP32-WROOM-32, ESP32-CAM). |
| Hardware | `device_sessions` | Core | Tracks boot cycles and connection durations, isolating telemetry across microcontroller reboots. |
| Hardware | `device_heartbeats` | Core | Diagnostic pulse monitoring battery voltage, signal strength (RSSI), and memory health. |
| Hardware | `vehicle_status_events` | Core | Records discrete actuation mode changes (manual, autonomous, emergency stop, motor states). |
| Telemetry | `encoder_samples` | Core | High-frequency dual-wheel odometer counts, RPM, and raw sensor readings. |
| Telemetry | `imu_samples` | Core | High-frequency 6-axis inertial motion telemetry from MPU6050. |
| Camera | `camera_frames` | Core | Tracks optical capture sequence, dimensions, encoding, and inference queue dispatch. |
| Media | `evidence_media` | Core | Manages on-disk cropped defect JPEG snapshots, relative paths, and SHA-256 hashes. |
| AI | `ai_model_versions` | Core | Provenance registry tracking deployed YOLO model configurations and weights checksums. |
| AI | `defects` | Core | Canonical pipeline defects, normalized bounding boxes, confidence, and review lifecycles. |
| Localization | `localization_records` | Core | Correlates optical capture timestamps with encoder pulses, tracking sync confidence. |
| Reporting | `inspection_reports` | Core | Registry of compiled compliance certificates and exported analysis documents. |
| Audit | `audit_events` | Core | Append-only non-repudiation log for administrative changes and review overrides. |
| Hardware | `sensor_calibration_records` | Optional Future | Deferred until multi-point physical sensor calibration procedures are implemented in firmware. |
| AI | `defect_review_history` | Optional Future | Deferred; individual defect review fields and audit events currently capture operator overrides adequately. |

---

## 5. Telemetry Architecture and Ingestion Strategy

### 5.1 Typed Column Storage vs. Unbounded JSON
High-frequency sensor streams (10 to 50 Hz) are stored strictly as typed relational columns rather than unbounded JSON blobs:
- **Query Efficiency**: Relational columns permit direct CPU vectorization, index utilization, and selective aggregation (`AVG(left_rpm)`, `MAX(left_ticks)`) without CPU-intensive JSON parsing overhead.
- **Data Integrity**: Database-level type constraints prevent invalid types, NaN values, or missing sensor fields from corrupting time-series tables.
- **Storage Optimization**: Structured PostgreSQL rows with fixed data types consume significantly less storage on disk than JSON key-value overhead repeated across millions of rows.

### 5.2 Device Timestamp vs. Server Arrival Timestamp
To prevent clock skew from distorting physical pipeline inspection data, every telemetry and camera table explicitly preserves two distinct temporal coordinates:
1. `device_timestamp` / `device_uptime_ms`: The local hardware clock reported by the microcontroller at the instant of measurement.
2. `recorded_at`: The synchronized UTC timestamp generated by the FastAPI backend upon socket arrival.

When microcontroller clocks drift or lack Network Time Protocol (NTP) connectivity inside buried PVC conduits, `recorded_at` provides an absolute monotonic reference, while `device_uptime_ms` enables precise relative delta calculations.

### 5.3 Configurable Batch Buffer Pattern
Telemetry packets are ingested via WebSocket or UDP into an in-memory queue managed by `TelemetryStateService`. Rather than executing an immediate database transaction per sample:
- Packets accumulate in an asynchronous memory buffer.
- The buffer flushes to the database using multi-row bulk inserts when:
  1. The accumulated sample count reaches `TELEMETRY_BUFFER_BATCH_SIZE` (default configurable: 50 to 200 samples).
  2. OR the elapsed time since last flush reaches `TELEMETRY_BUFFER_FLUSH_INTERVAL_SECONDS` (default configurable: 0.5 to 2.0 seconds).
- This decouples physical disk I/O from network packet arrival, sustaining 50 Hz ingestion rates without thread starvation.

---

## 6. AI Inference and Defect Lifecycle Modeling

### 6.1 Model Metadata vs. Weights Storage
Model weights binary files (`.pt`, `.onnx`, `.engine`) are stored strictly on the local filesystem (`backend/weights/`) and referenced via `ai_model_versions`. The database stores:
- Semantic model identifier (e.g., `yolov8n-pipebot-v1.0.0`).
- Cryptographic SHA-256 hash of the weights file.
- Architecture parameters, confidence thresholds, and input dimensions (`640x640`).
- Canonical class mapping JSON dictionary.

### 6.2 Defect Review Lifecycle
Defects follow an explicit state machine managed through the API:
- `unreviewed` (Initial AI detection state).
- `confirmed` (Operator verified defect as genuine).
- `rejected` (Operator dismissed detection as false positive).
- `reclassified` (Operator corrected defect classification or bounding box).

The database enforces `review_status` transitions and captures `reviewed_by`, `reviewed_at`, and `notes` directly on the defect entity, while generating a non-repudiation log in `audit_events`.

---

## 7. Dual-MCU Synchronization and Localization Modeling

Accurate spatial localization requires determining the crawler's physical conduit position at the exact moment a camera frame was captured.

Because the ESP32-CAM and ESP32-WROOM-32 currently operate on independent microcontrollers without a validated hardware clock synchronization line (such as a shared PPS pulse or hardware PTP):
1. **Distance Nullability**: `defects.estimated_distance_meters` is explicitly defined as `NULLABLE`.
2. **Synchronization Enforcement**: If dual-MCU clock synchronization is unverified (`allow_unverified_sync = False`), `estimated_distance_meters` remains `NULL`.
3. **Localization Records**: The `localization_records` table stores:
   - `frame_capture_timestamp`: Optical frame timestamp.
   - `encoder_sample_timestamp`: Nearest odometer timestamp.
   - `temporal_delta_ms`: Mathematical time difference between capture and measurement.
   - `clock_sync_status`: Enum (`UNVERIFIED_HEURISTIC`, `HARDWARE_PULSE_VERIFIED`, `MANUAL_OVERRIDE`).
4. **Heuristic Window**: The 0.5-second matching window is explicitly designated as an unvalidated heuristic fallback, pending physical hardware shutter synchronization.

