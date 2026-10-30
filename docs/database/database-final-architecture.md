# PipeBot Database Engineering: Final Architecture Specification

## 1. System Overview and Architectural Context

PipeBot is an AI-powered robotic crawler engineered for non-destructive visual and structural inspection of internal PVC pipelines (150mm to 300mm diameter). The system architecture integrates physical robotics, edge microcontrollers (ESP32-WROOM-32 locomotion, ESP32-CAM optical capture), a FastAPI backend, and a React TypeScript dashboard.

The database layer serves as the single source of truth for:
- Inspection session lifecycles and metadata.
- Deep learning computer vision defect detections (Deformation, Misalignment, Obstacle, Rupture).
- High-frequency odometry and 6-axis inertial motion telemetry.
- Microcontroller health diagnostics and telemetry sessions.
- Camera frame capture metadata and on-disk evidence media tracking.
- Pre-aggregated analytical summaries and compliance grading.
- Exported compliance certificates and engineering inspection reports.
- Append-only non-repudiation security and administrative audit events.

```
+-----------------------------------------------------------------------------+
|                               REACT FRONTEND                                |
|          (TypeScript, Vite, Tailwind CSS, Live Telemetry Dashboard)         |
+-----------------------------------------------------------------------------+
                                       ^
                                       | HTTP REST & WebSocket (JSON)
                                       v
+-----------------------------------------------------------------------------+
|                               FASTAPI BACKEND                               |
|   +---------------------------------------------------------------------+   |
|   |                       Application Service Layer                     |   |
|   |   (InspectionService, DefectService, TelemetryState, VisionPipeline) |   |
|   +---------------------------------------------------------------------+   |
|                                       |                                     |
|   +---------------------------------------------------------------------+   |
|   |                       Repository Data Access Layer                  |   |
|   |   (Inspection, Defect, Telemetry, Media, Report, Audit, AIModel)    |   |
|   +---------------------------------------------------------------------+   |
|                                       |                                     |
|   +---------------------------------------------------------------------+   |
|   |                     SQLAlchemy 2.0 ORM & Core                       |   |
|   |     (BigIntId Dialect Variant, UtcDateTime, Strict Foreign Keys)    |   |
|   +---------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------+
                                       |
                   +-------------------+-------------------+
                   | (Active Development)                  | (Future Production Target)
                   v                                       v
      +-------------------------+             +-------------------------+
      |      SQLite 3.37+       |             |      PostgreSQL 16      |
      |   WAL Mode, Busy=5000   |             |   TimescaleDB Extension |
      |   Local File Storage    |             |   Partitioned Analytics |
      +-------------------------+             +-------------------------+
```

---

## 2. Core Entities and Domain Relationships

The data model comprises 16 distinct domain tables organized into 7 cohesive architectural subsystems:

### 2.1 Inspection Management Domain
- `inspections`: Primary session registry tracking pipe identifier, nominal diameter (150-300mm), conduit composition (PVC, HDPE), operator credentials, lifecycle status (`created`, `in_progress`, `paused`, `completed`, `failed`, `cancelled`), and soft-archival state (`is_archived`).
- `inspection_events`: Chronological milestone event stream tracking operational transitions (`INSPECTION_CREATED`, `STARTED`, `PAUSED`, `RESUMED`, `COMPLETED`, `CANCELLED`).
- `inspection_summaries`: Pre-aggregated analytical cache maintaining verified defect counts per canonical class, elapsed inspection runtime, and overall pipeline condition grade (`A`, `B`, `C`, `D`, `FAIL`).

### 2.2 Defect and Anomaly Detection Domain
- `defects`: Detected pipe anomalies classified strictly into canonical classes (`Deformation`, `Misalignment`, `Obstacle`, `Rupture`). Maintains bounding box geometry, detection confidence (0.0 to 1.0), capture timestamp, correlated distance, and operator review state (`pending`, `confirmed`, `rejected`).
- `evidence_media`: File registry tracking on-disk localized defect crop images with cryptographic SHA-256 hashes, POSIX file paths, MIME types, and storage backend identifiers (`LOCAL_FS`).
- `localization_records`: Spatial correlation registry pairing optical capture timestamps with encoder odometry samples. Explicitly preserves uncalibrated hardware states via `UNVERIFIED_SYNC` status and nullable distances.

### 2.3 Hardware Fleet and Diagnostics Domain
- `devices`: Physical crawler microcontroller inventory (`ESP32_WROOM`, `ESP32_CAM`) tracking MAC addresses, hardware revisions, and firmware builds.
- `device_sessions`: Microcontroller boot session tracking power cycles, boot IDs, IP addresses, and active connection spans.
- `device_heartbeats`: Periodic diagnostic pulse telemetry tracking WiFi RSSI (dBm), battery millivolts, battery state of charge (%), free heap memory (bytes), and controller uptime (seconds).
- `vehicle_status_events`: Hardware state transition events tracking drive mode (`manual`, `autonomous`), motor activation, illumination PWM duty cycle, and emergency stop engagements.

### 2.4 High-Frequency Telemetry Time-Series Domain
- `encoder_samples`: Rotary pulse odometry samples capturing monotonic packet sequence numbers, raw cumulative left and right wheel pulse ticks, derived RPM, forward speed, and direction.
- `imu_samples`: 6-axis MPU6050 inertial measurement samples capturing tri-axial linear acceleration (`accel_x`, `accel_y`, `accel_z`), tri-axial angular rate (`gyro_x`, `gyro_y`, `gyro_z`), and fused pitch/roll/yaw attitudes.

### 2.5 Machine Learning Provenance Domain
- `ai_model_versions`: Deployed neural network model metadata tracking model architectures (`yolov8n-pipebot`), semantic version identifiers, on-disk artifact paths, SHA-256 model weights checksums, class index mappings, and confidence evaluation thresholds.

### 2.6 Compliance and Engineering Reporting Domain
- `inspection_reports`: Persisted registry of compiled engineering summary reports and formal pipe compliance certificates with SHA-256 document checksums and overall structural condition grades.

### 2.7 Security and Operational Audit Domain
- `audit_events`: Append-only, non-repudiation audit trail recording security-critical events, administrative updates, review overrides, and state changes with JSON before/after snapshots and client IP addresses.

---

## 3. Cross-Dialect Portability Strategy

To guarantee seamless migration between SQLite (development and offline robotic deployment) and PostgreSQL 16 (centralized multi-tenant cloud operations), the following architectural patterns are strictly enforced:

### 3.1 Surrogate Primary Key Dialect Variant
A custom type alias is utilized for all surrogate primary keys:
```python
BigIntId = sa.BigInteger().with_variant(sa.Integer(), "sqlite")
```
- In SQLite: Renders as `INTEGER PRIMARY KEY AUTOINCREMENT`, binding to 64-bit rowid tables.
- In PostgreSQL: Renders as native 64-bit `BIGINT` with identity sequence (`BIGSERIAL`).

### 3.2 Strict UTC Timestamp Normalization
All database columns tracking wall-clock time use the custom `UtcDateTime` SQLAlchemy TypeDecorator:
- Serializes `datetime` objects to ISO 8601 UTC strings (`YYYY-MM-DDTHH:MM:SS.ffffff+00:00`) in SQLite.
- Binds to `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`) in PostgreSQL.
- Naive datetime inputs are intercepted and normalized to UTC instant representation to prevent timezone skew.

### 3.3 Foreign Key Enforcement and Cascade Safeguards
- Foreign keys in SQLite require connection-level enforcement via `PRAGMA foreign_keys = ON`.
- Destructive cascading deletions (`ON DELETE CASCADE`) are strictly prohibited on core historical evidence (`inspections` -> `defects` -> `evidence_media`). Instead, `ON DELETE RESTRICT` guarantees that defect data and physical inspection evidence can never be deleted while parent inspections exist.
- Soft-deletion (`is_deleted`) and soft-archival (`is_archived`) patterns ensure full regulatory traceability.

---

## 4. Repository Pattern Architecture

Direct SQL execution from API route handlers or WebSocket consumers is strictly prohibited. All data access occurs through specialized repository classes encapsulated in `app.repositories`:
- `InspectionRepository`: Session creation, status transitions, event timelines, analytical summary caching.
- `DefectRepository`: Defect creation, bounding boxes, distance ordering, evidence attachment, spatial localization records.
- `TelemetryRepository`: Device registration, boot sessions, heartbeats, batch sample ingestion, windowed time-series queries.
- `MediaRepository`: Frame capture metadata logging, defect evidence crop tracking, checksum verification.
- `ReportRepository`: Report document registration, checksum verification, report listing.
- `AuditRepository`: Append-only security audit event logging.
- `AIModelRepository`: Neural network version registration, activation management, threshold configuration.

