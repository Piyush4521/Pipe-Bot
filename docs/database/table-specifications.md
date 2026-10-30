# PipeBot Database Engineering: Physical Table Specifications and Data Dictionary

## 1. Executive Overview

This document provides the definitive data dictionary and physical table specifications for the PipeBot relational database tier. It establishes column definitions, SQL data types, nullability, primary/foreign keys, check constraints, default values, index assignments, and lifecycle policies across all seven functional domains.

### Data Type Mapping Strategy
To guarantee dual-engine compatibility between the active SQLite prototype and the target PostgreSQL 16 database, types are defined using standardized ANSI/SQL standards mapped across engines:
- `BIGINT` / `BigIntId`: `sa.BigInteger().with_variant(sa.Integer(), "sqlite")` generates `BIGINT` (BIGSERIAL) on PostgreSQL and `INTEGER PRIMARY KEY` (64-bit rowid auto-increment) on SQLite.
- `INT`: `INTEGER` in PostgreSQL; `INTEGER` in SQLite.
- `UUID`: `UUID` in PostgreSQL; `VARCHAR(36)` in SQLite.
- `TIMESTAMPTZ`: `TIMESTAMP WITH TIME ZONE` in PostgreSQL; `DATETIME` via custom `UtcDateTime` decorator in SQLite.
- `JSONB`: `JSONB` in PostgreSQL; `JSON` (Text) in SQLite.
- `BOOLEAN`: `BOOLEAN` in PostgreSQL; `INTEGER` (0 or 1) in SQLite.
- `FLOAT`: `DOUBLE PRECISION` in PostgreSQL; `REAL` in SQLite.

---

## 2. Domain 1: Inspection Management

### 2.1 Table: `inspections`
- **Purpose**: Central master record representing an individual pipeline crawler examination session.
- **Physical Name**: `inspections`
- **Retention / Archival**: Permanent compliance record. Hard deletion prohibited; archived via `is_archived = TRUE`.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Physical surrogate primary key (`pk_inspections`). |
| `inspection_id` | VARCHAR(64) | NO | None | Public human-readable unique business code (e.g. `INSP-20261030-ABC123`). Unique constraint (`uq_inspections_inspection_id`). |
| `pipe_identifier` | VARCHAR(128) | NO | None | Target conduit asset ID (e.g. `PVC-MAIN-001`). Indexed. |
| `pipe_material` | VARCHAR(64) | NO | 'PVC' | Conduit material composition (e.g. `PVC`, `HDPE`, `Concrete`). |
| `pipe_diameter_mm` | INT | NO | None | Nominal conduit inner diameter in millimeters. Check: `pipe_diameter_mm > 0`. |
| `operator_id` | VARCHAR(64) | NO | None | Badge or user identifier of the certified inspection technician. |
| `status` | VARCHAR(32) | NO | 'created' | Lifecycle state: `created`, `in_progress`, `paused`, `completed`, `failed`, `cancelled`. Check: `status IN ('created','in_progress','paused','completed','failed','cancelled')`. |
| `started_at` | TIMESTAMPTZ | YES | NULL | Exact UTC timestamp when the inspection run transitioned to active drive mode. |
| `completed_at` | TIMESTAMPTZ | YES | NULL | Exact UTC timestamp when the inspection finished or was terminated. |
| `total_distance_meters` | FLOAT | YES | 0.0 | Cumulative linear travel distance inside pipe in meters. Check: `total_distance_meters >= 0.0`. |
| `notes` | TEXT | YES | NULL | Optional technician field observations or situational annotations. |
| `is_archived` | BOOLEAN | NO | FALSE | Soft archival flag preserving historical records from active operational views. Indexed. |
| `is_deleted` | BOOLEAN | NO | FALSE | Soft deletion flag preventing physical data removal. Check: `is_deleted IN (FALSE, TRUE)`. |
| `created_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC record creation timestamp. Managed via `TimestampMixin`. |
| `updated_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC record modification timestamp. Managed via `TimestampMixin`. |

- **Primary Key**: `pk_inspections (id)`
- **Foreign Keys**: None.
- **Indexes**:
  - `uq_inspections_inspection_id`: UNIQUE (`inspection_id`)
  - `ix_inspections_pipe_identifier`: B-tree (`pipe_identifier`)
  - `ix_inspections_is_archived`: B-tree (`is_archived`)
  - `idx_inspections_status_created`: Composite B-tree (`status`, `created_at DESC`) WHERE `is_deleted = FALSE`
- **Relationships**: 1-to-many with `defects`, `inspection_events`, `device_sessions`, `encoder_samples`, `imu_samples`, `camera_frames`, `inspection_reports`.

---

### 2.2 Table: `inspection_events`
- **Purpose**: Granular event log tracking state machine transitions and operational milestones during an inspection run.
- **Physical Name**: `inspection_events`
- **Retention / Archival**: Retained with parent inspection.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_inspection_events`). |
| `inspection_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `inspections.id`. Delete action: `RESTRICT`. |
| `event_type` | VARCHAR(64) | NO | None | Event name: `STATE_CHANGE`, `OBSTACLE_ENCOUNTERED`, `NOTE_LOGGED`, `CALIBRATION_CHECK`. |
| `payload` | JSONB / TEXT | YES | NULL | Contextual event attributes (e.g. prior state, new state, trigger reason). |
| `occurred_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Exact UTC timestamp of event occurrence. Indexed. |

- **Primary Key**: `pk_inspection_events (id)`
- **Foreign Keys**: `fk_inspection_events_inspection_id`: `inspection_id` references `inspections(id)` ON DELETE RESTRICT ON UPDATE CASCADE.
- **Indexes**:
  - `idx_events_inspection_occurred`: B-tree (`inspection_id`, `occurred_at ASC`)

---

### 2.3 Table: `inspection_summaries`
- **Purpose**: Denormalized pre-aggregated metrics compiled upon inspection completion to optimize dashboard loading.
- **Physical Name**: `inspection_summaries`
- **Retention / Archival**: Retained with parent inspection.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `inspection_id` | BIGINT / INTEGER | NO | None | Primary key and foreign key referencing `inspections.id`. |
| `total_defects_count` | INT | NO | 0 | Total number of verified defects detected. Check: `>= 0`. |
| `deformation_count` | INT | NO | 0 | Count of Deformation anomalies. Check: `>= 0`. |
| `misalignment_count` | INT | NO | 0 | Count of Misalignment anomalies. Check: `>= 0`. |
| `obstacle_count` | INT | NO | 0 | Count of Obstacle anomalies. Check: `>= 0`. |
| `rupture_count` | INT | NO | 0 | Count of Rupture anomalies. Check: `>= 0`. |
| `overall_pipe_grade` | VARCHAR(16) | NO | 'PENDING' | Compliance grade: `A`, `B`, `C`, `D`, `FAIL`, `PENDING`. |
| `total_runtime_seconds`| INT | NO | 0 | Elapsed inspection duration in seconds. Check: `>= 0`. |
| `compiled_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC timestamp when summary was compiled. |

- **Primary Key**: `pk_inspection_summaries (inspection_id)`
- **Foreign Keys**: `fk_inspection_summaries_inspection_id`: `inspection_id` references `inspections(id)` ON DELETE CASCADE.

---

## 3. Domain 2: Hardware and Device Sessions

### 3.1 Table: `devices`
- **Purpose**: Master hardware registry of crawler microcontrollers, cameras, and compute boards.
- **Physical Name**: `devices`
- **Retention / Archival**: Master reference data; retained indefinitely.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | VARCHAR(64) | NO | None | Primary key string hardware ID (e.g. `esp32-crawler-wroom`, `esp32-cam-front`). |
| `device_type` | VARCHAR(32) | NO | None | Hardware class: `ESP32_WROOM`, `ESP32_CAM`, `PROCESSING_SERVER`. |
| `mac_address` | VARCHAR(32) | YES | NULL | Unique physical MAC address of WiFi/Ethernet interface. |
| `firmware_version` | VARCHAR(32) | YES | NULL | Semantic version of active firmware image. |
| `is_active` | BOOLEAN | NO | TRUE | Whether the unit is currently commissioned for field operations. |
| `created_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Registration timestamp. |

- **Primary Key**: `pk_devices (id)`
- **Unique Constraints**: `uq_devices_mac`: (`mac_address`) WHERE `mac_address IS NOT NULL`.

---

### 3.2 Table: `device_sessions`
- **Purpose**: Tracks continuous physical connection sessions per device boot cycle.
- **Physical Name**: `device_sessions`
- **Retention / Archival**: Retained for diagnostic traceability (180 days).

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_device_sessions`). |
| `session_uuid` | VARCHAR(36) | NO | None | Unique UUID string for public reference. |
| `device_id` | VARCHAR(64) | NO | None | Foreign key referencing `devices.id`. |
| `inspection_id` | BIGINT / INTEGER | YES | NULL | Foreign key referencing active `inspections.id` (null if idle outside run). |
| `boot_id` | VARCHAR(64) | NO | None | Monotonic boot identifier or random UUID from microcontroller startup. |
| `ip_address` | VARCHAR(45) | YES | NULL | IPv4 or IPv6 network address of the connected client. |
| `connected_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC connection establishment timestamp. |
| `disconnected_at` | TIMESTAMPTZ | YES | NULL | UTC disconnect timestamp (null while session is active). |
| `disconnect_reason` | VARCHAR(128) | YES | NULL | Explicit close reason: `SOCKET_TIMEOUT`, `REBOOT`, `CLIENT_CLOSE`. |

- **Primary Key**: `pk_device_sessions (id)`
- **Foreign Keys**:
  - `fk_device_sessions_device_id`: references `devices(id)` ON DELETE RESTRICT.
  - `fk_device_sessions_inspection_id`: references `inspections(id)` ON DELETE SET NULL.
- **Indexes**:
  - `uq_device_sessions_uuid`: UNIQUE (`session_uuid`)
  - `idx_device_sessions_lookup`: B-tree (`device_id`, `boot_id`, `connected_at DESC`)

---

### 3.3 Table: `device_heartbeats`
- **Purpose**: High-level periodic health telemetry monitoring battery voltage, signal strength, and heap memory.
- **Physical Name**: `device_heartbeats`
- **Retention / Archival**: Retained for 30 to 60 days, then purged.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_device_heartbeats`). |
| `session_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `device_sessions.id`. |
| `device_id` | VARCHAR(64) | NO | None | Foreign key referencing `devices.id`. |
| `rssi_dbm` | INT | YES | NULL | WiFi received signal strength indication in dBm (e.g. -65). |
| `battery_millivolts` | INT | YES | NULL | DC bus or battery pack potential in millivolts (e.g. 11800). |
| `battery_percent` | FLOAT | YES | NULL | Computed battery percentage (0.0 to 100.0). Check: `0.0 <= battery_percent <= 100.0`. |
| `free_heap_bytes` | INT | YES | NULL | Free heap memory available on embedded MCU. |
| `uptime_seconds` | FLOAT | YES | NULL | Reported device uptime in seconds since last boot. |
| `recorded_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC backend receipt timestamp. Indexed. |

- **Primary Key**: `pk_device_heartbeats (id)`
- **Foreign Keys**: `fk_heartbeats_session_id`: references `device_sessions(id)` ON DELETE CASCADE.
- **Indexes**:
  - `idx_heartbeats_session_time`: B-tree (`session_id`, `recorded_at DESC`)

---

### 3.4 Table: `vehicle_status_events`
- **Purpose**: Records discrete motor operational changes, emergency stops, or safety stall warnings.
- **Physical Name**: `vehicle_status_events`
- **Retention / Archival**: Retained with parent inspection.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_vehicle_status_events`). |
| `inspection_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `inspections.id`. |
| `session_id` | BIGINT / INTEGER | YES | NULL | Foreign key referencing `device_sessions.id`. |
| `drive_mode` | VARCHAR(32) | NO | 'manual' | Operational mode: `manual`, `autonomous`, `reverse`, `estop`. |
| `left_motor_state` | VARCHAR(32) | NO | 'idle' | Left motor state: `idle`, `forward`, `reverse`, `offline`. |
| `right_motor_state`| VARCHAR(32) | NO | 'idle' | Right motor state: `idle`, `forward`, `reverse`, `offline`. |
| `emergency_stop` | BOOLEAN | NO | FALSE | Emergency stop hardware status flag. |
| `recorded_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC timestamp of event recording. |

- **Primary Key**: `pk_vehicle_status_events (id)`
- **Foreign Keys**: `fk_vehicle_events_inspection_id`: references `inspections(id)` ON DELETE RESTRICT.

---

## 4. Domain 3: High-Frequency Telemetry

### 4.1 Table: `encoder_samples`
- **Purpose**: High-frequency dual-wheel optical/magnetic encoder cumulative counts and velocity metrics.
- **Physical Name**: `encoder_samples`
- **Retention / Archival**: 60 to 90 days raw retention; downsampled to 1 Hz averages or exported to Parquet for long-term storage.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_encoder_samples`). |
| `inspection_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `inspections.id`. |
| `session_id` | BIGINT / INTEGER | YES | NULL | Foreign key referencing `device_sessions.id`. |
| `sequence_number` | BIGINT | NO | None | Monotonic packet counter from MCU boot. |
| `left_ticks` | BIGINT | NO | None | Raw cumulative pulse count from left motor encoder. |
| `right_ticks` | BIGINT | NO | None | Raw cumulative pulse count from right motor encoder. |
| `left_rpm` | FLOAT | YES | NULL | Rotational speed of left wheel in RPM. Check: finite float. |
| `right_rpm` | FLOAT | YES | NULL | Rotational speed of right wheel in RPM. Check: finite float. |
| `speed_mps` | FLOAT | YES | NULL | Forward linear speed in meters per second. |
| `direction` | VARCHAR(16) | YES | 'forward' | Physical drive direction: `forward`, `reverse`, `stopped`. |
| `device_uptime_ms` | BIGINT | YES | NULL | Milliseconds since MCU boot. |
| `device_timestamp` | TIMESTAMPTZ | YES | NULL | Optional hardware RTC timestamp if configured. |
| `recorded_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Server UTC arrival timestamp. Indexed. |

- **Primary Key**: `pk_encoder_samples (id)`
- **Foreign Keys**: `fk_encoder_samples_inspection_id`: references `inspections(id)` ON DELETE RESTRICT.
- **Indexes**:
  - `idx_encoder_inspection_recorded`: B-tree (`inspection_id`, `recorded_at ASC`)
  - `brin_encoder_recorded`: BRIN (`recorded_at`) in PostgreSQL

---

### 4.2 Table: `imu_samples`
- **Purpose**: High-frequency 6-axis inertial motion telemetry from MPU6050 (accelerometer and gyroscope).
- **Physical Name**: `imu_samples`
- **Retention / Archival**: 60 to 90 days raw retention; downsampled or archived.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_imu_samples`). |
| `inspection_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `inspections.id`. |
| `session_id` | BIGINT / INTEGER | YES | NULL | Foreign key referencing `device_sessions.id`. |
| `sequence_number` | BIGINT | NO | None | Monotonic packet counter from MCU boot. |
| `accel_x` | FLOAT | YES | NULL | Linear acceleration X-axis (raw or calibrated). |
| `accel_y` | FLOAT | YES | NULL | Linear acceleration Y-axis (raw or calibrated). |
| `accel_z` | FLOAT | YES | NULL | Linear acceleration Z-axis (raw or calibrated). |
| `gyro_x` | FLOAT | YES | NULL | Angular rate X-axis. |
| `gyro_y` | FLOAT | YES | NULL | Angular rate Y-axis. |
| `gyro_z` | FLOAT | YES | NULL | Angular rate Z-axis. |
| `pitch_deg` | FLOAT | YES | NULL | Computed pitch inclination angle in degrees. |
| `roll_deg` | FLOAT | YES | NULL | Computed roll inclination angle in degrees. |
| `yaw_deg` | FLOAT | YES | NULL | Computed heading angle in degrees. |
| `temperature_c` | FLOAT | YES | NULL | Internal sensor die temperature in Celsius. |
| `sensor_units` | VARCHAR(32) | NO | 'raw_lsb' | Physical units format: `raw_lsb`, `si_mps2_degs`. |
| `device_uptime_ms` | BIGINT | YES | NULL | Milliseconds since MCU boot. |
| `device_timestamp` | TIMESTAMPTZ | YES | NULL | Hardware timestamp if configured. |
| `recorded_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Server UTC arrival timestamp. Indexed. |

- **Primary Key**: `pk_imu_samples (id)`
- **Foreign Keys**: `fk_imu_samples_inspection_id`: references `inspections(id)` ON DELETE RESTRICT.
- **Indexes**:
  - `idx_imu_inspection_recorded`: B-tree (`inspection_id`, `recorded_at ASC`)
  - `brin_imu_recorded`: BRIN (`recorded_at`) in PostgreSQL

---

## 5. Domain 4: Camera and Media Metadata

### 5.1 Table: `camera_frames`
- **Purpose**: Metadata record for individual optical capture frames received from the ESP32-CAM. Video frames are never stored as database BLOBs.
- **Physical Name**: `camera_frames`
- **Retention / Archival**: Intermediate frames pruned after 14 days unless linked to a defect detection.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Surrogate primary key (`pk_camera_frames`). |
| `frame_id` | VARCHAR(64) | NO | None | Unique frame UUID string matching frontend contract. Unique index. |
| `inspection_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `inspections.id`. |
| `camera_id` | VARCHAR(64) | NO | 'esp32-cam-front' | Hardware camera device identifier. |
| `frame_sequence` | BIGINT | NO | 0 | Sequence counter from camera firmware stream. |
| `frame_width` | INT | NO | None | Horizontal image dimension in pixels. Check: `frame_width > 0`. |
| `frame_height` | INT | NO | None | Vertical image dimension in pixels. Check: `frame_height > 0`. |
| `encoding` | VARCHAR(16) | NO | 'jpeg' | Compression format: `jpeg`, `png`. |
| `frame_bytes` | INT | NO | None | Raw frame payload size in bytes. Check: `frame_bytes > 0`. |
| `capture_timestamp`| TIMESTAMPTZ | YES | NULL | Exposure timestamp if provided by camera clock. |
| `recorded_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Server UTC arrival timestamp. Indexed. |
| `processing_status`| VARCHAR(32) | NO | 'pending' | Status: `pending`, `inferred`, `dropped`, `error`. |
| `has_defect` | BOOLEAN | NO | FALSE | Flag indicating if YOLO inference detected an anomaly. |

- **Primary Key**: `pk_camera_frames (id)`
- **Foreign Keys**: `fk_camera_frames_inspection_id`: references `inspections(id)` ON DELETE RESTRICT.
- **Indexes**:
  - `uq_camera_frames_frame_id`: UNIQUE (`frame_id`)
  - `idx_frames_inspection_capture`: B-tree (`inspection_id`, `capture_timestamp ASC`)
  - `idx_frames_recorded`: B-tree (`recorded_at DESC`)

---

### 5.2 Table: `evidence_media`
- **Purpose**: File pointer, checksum, and storage registry for localized defect crop images stored on disk.
- **Physical Name**: `evidence_media`
- **Retention / Archival**: Permanent compliance record. Retained with parent defect.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_evidence_media`). |
| `media_uuid` | VARCHAR(36) | NO | None | Public media UUID string. Unique. |
| `defect_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `defects.id`. Delete: `RESTRICT`. |
| `file_path` | VARCHAR(512) | NO | None | Relative POSIX path from media root (e.g. `crops/insp_1/def_42.jpg`). Unique. |
| `mime_type` | VARCHAR(64) | NO | 'image/jpeg' | Media format MIME string. |
| `file_size_bytes` | INT | NO | None | On-disk image size in bytes. Check: `file_size_bytes > 0`. |
| `checksum_sha256` | VARCHAR(64) | NO | None | Cryptographic SHA-256 integrity hash of the image file. |
| `storage_backend` | VARCHAR(32) | NO | 'LOCAL_FS' | Storage provider: `LOCAL_FS`, `S3`, `MINIO`. |
| `created_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation timestamp. |

- **Primary Key**: `pk_evidence_media (id)`
- **Foreign Keys**: `fk_evidence_media_defect_id`: references `defects(id)` ON DELETE RESTRICT ON UPDATE CASCADE.
- **Indexes**:
  - `uq_evidence_media_uuid`: UNIQUE (`media_uuid`)
  - `uq_evidence_media_path`: UNIQUE (`file_path`)
  - `ix_evidence_media_defect`: B-tree (`defect_id`)

---

## 6. Domain 5: AI Inference and Defect Management

### 6.1 Table: `ai_model_versions`
- **Purpose**: Provenance tracking of computer vision models deployed for automated pipeline inspection.
- **Physical Name**: `ai_model_versions`
- **Retention / Archival**: Master configuration; retained indefinitely to preserve auditability of historical detections.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_ai_model_versions`). |
| `model_name` | VARCHAR(64) | NO | None | Human-readable architecture name (e.g. `yolov8n-pipebot`). |
| `model_version` | VARCHAR(64) | NO | None | Semantic version string (e.g. `v1.2.0-baseline`). Unique. |
| `artifact_path` | VARCHAR(256) | NO | None | Relative path to weights file on disk (`weights/yolov8_pipe_v1.onnx`). |
| `artifact_checksum_sha256` | VARCHAR(64) | NO | None | Cryptographic SHA-256 hash of model weights file. |
| `training_dataset_id` | VARCHAR(64) | YES | NULL | Reference to training dataset version. |
| `class_mapping` | JSONB / TEXT | NO | None | Index-to-class dictionary: `{"0":"Deformation","1":"Misalignment","2":"Obstacle","3":"Rupture"}`. |
| `input_dimensions` | VARCHAR(32) | NO | '640x640' | Model input image resolution. |
| `confidence_threshold` | FLOAT | NO | 0.25 | Default inference confidence threshold. Check: `0.0 <= confidence_threshold <= 1.0`. |
| `inference_backend` | VARCHAR(32) | NO | 'ULTRALYTICS' | Provider backend: `ULTRALYTICS`, `ONNX_RUNTIME`, `OPENVINO`. |
| `is_active` | BOOLEAN | NO | TRUE | Whether this version is currently active for live inference. |
| `created_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Model registration timestamp. |

- **Primary Key**: `pk_ai_model_versions (id)`
- **Unique Constraints**: `uq_ai_model_version`: (`model_version`)

---

### 6.2 Table: `defects`
- **Purpose**: Canonical pipeline defects, bounding boxes, confidence, spatial distance, and review lifecycle.
- **Physical Name**: `defects` (Authoritative table name matching active Alembic migration `d4d255efae0c`).
- **Retention / Archival**: Permanent compliance record. Hard deletion prohibited; soft delete via `is_deleted = TRUE`.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Physical surrogate primary key (`pk_defects`). |
| `defect_id` | VARCHAR(64) | NO | None | Public unique defect business ID (e.g. `DEF-20261030-XYZ789`). Unique index. |
| `inspection_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `inspections.id`. Delete: `RESTRICT`. Indexed. |
| `frame_id` | VARCHAR(64) | YES | NULL | Public UUID of optical frame exhibiting anomaly. Indexed. |
| `model_version_id`| BIGINT / INTEGER | YES | NULL | Foreign key referencing `ai_model_versions.id` (null if manually logged). |
| `defect_class` | VARCHAR(32) | NO | None | Canonical class: `Deformation`, `Misalignment`, `Obstacle`, `Rupture`. Check: `defect_class IN ('Deformation','Misalignment','Obstacle','Rupture')`. |
| `confidence` | FLOAT | YES | NULL | Model confidence score (0.0 to 1.0). Check: `confidence >= 0.0 AND confidence <= 1.0`. |
| `severity` | VARCHAR(16) | NO | 'moderate' | Severity rating: `minor`, `moderate`, `severe`, `critical`. |
| `bounding_box` | JSONB / TEXT | YES | NULL | Normalized box dictionary (`{"x":0.2,"y":0.3,"width":0.4,"height":0.5}`). |
| `capture_timestamp`| TIMESTAMPTZ | NO | None | Capture timestamp from optical camera frame. Indexed. |
| `inference_timestamp` | TIMESTAMPTZ | YES | NULL | UTC timestamp when YOLO model evaluation completed on server. |
| `estimated_distance_meters` | FLOAT | YES | NULL | Estimated linear distance along conduit in meters. Check: `estimated_distance_meters >= 0.0`. Nullable when sync is unverified. |
| `review_status` | VARCHAR(32) | NO | 'unreviewed' | Review workflow status: `unreviewed`, `confirmed`, `rejected`, `reclassified`. |
| `reviewed_by` | VARCHAR(64) | YES | NULL | Operator identifier who performed review. |
| `reviewed_at` | TIMESTAMPTZ | YES | NULL | UTC timestamp of review completion. |
| `snapshot_path` | VARCHAR(256) | YES | NULL | Relative path to evidence crop image. |
| `notes` | TEXT | YES | NULL | Operator or inspector review notes. |
| `is_deleted` | BOOLEAN | NO | FALSE | Soft deletion flag. Indexed. |
| `created_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC record creation timestamp. |
| `updated_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC record modification timestamp. |

- **Primary Key**: `pk_defects (id)`
- **Foreign Keys**:
  - `fk_defects_inspection_id`: references `inspections(id)` ON DELETE RESTRICT ON UPDATE CASCADE.
  - `fk_defects_model_version_id`: references `ai_model_versions(id)` ON DELETE RESTRICT ON UPDATE CASCADE.
- **Indexes**:
  - `uq_defects_defect_id`: UNIQUE (`defect_id`)
  - `ix_defects_inspection_id`: B-tree (`inspection_id`)
  - `ix_defects_frame_id`: B-tree (`frame_id`)
  - `ix_defects_is_deleted`: B-tree (`is_deleted`)
  - `idx_defects_insp_detected`: B-tree (`inspection_id`, `capture_timestamp ASC`) WHERE `is_deleted = FALSE`
  - `idx_defects_insp_class`: B-tree (`inspection_id`, `defect_class`) WHERE `is_deleted = FALSE`
  - `idx_defects_review_queue`: B-tree (`review_status`, `inspection_id`) WHERE `is_deleted = FALSE`
  - `idx_defects_distance`: B-tree (`inspection_id`, `estimated_distance_meters ASC`) WHERE `estimated_distance_meters IS NOT NULL AND is_deleted = FALSE`

---

## 7. Domain 6: Spatial Localization

### 7.1 Table: `localization_records`
- **Purpose**: Encapsulates the optical frame to encoder correlation, keeping timestamp discrepancies and clock synchronization state explicit.
- **Physical Name**: `localization_records`
- **Retention / Archival**: Retained with parent defect.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_localization_records`). |
| `defect_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `defects.id`. Delete: `RESTRICT`. |
| `frame_id` | VARCHAR(64) | YES | NULL | Reference to optical frame ID. |
| `frame_capture_timestamp` | TIMESTAMPTZ | NO | None | Optical frame exposure timestamp. |
| `encoder_sample_timestamp` | TIMESTAMPTZ | NO | None | Timestamp of closest matched encoder reading. |
| `temporal_delta_ms` | FLOAT | NO | None | Absolute difference between frame exposure and encoder reading in milliseconds. |
| `clock_sync_status` | VARCHAR(32) | NO | 'UNVERIFIED_SYNC' | Sync status: `UNVERIFIED_SYNC`, `SYNCHRONIZED`, `MANUAL_OVERRIDE`. |
| `sync_notes` | VARCHAR(256) | YES | NULL | Contextual reason if synchronization is unverified or degraded. |
| `left_encoder_ticks` | BIGINT | YES | NULL | Cumulative ticks of left wheel at correlated point. |
| `right_encoder_ticks`| BIGINT | YES | NULL | Cumulative ticks of right wheel at correlated point. |
| `computed_distance_meters` | FLOAT | YES | NULL | Computed pipeline distance. Check: `>= 0.0`. Nullable when sync is unverified. |
| `created_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation timestamp. |

- **Primary Key**: `pk_localization_records (id)`
- **Foreign Keys**: `fk_localization_records_defect_id`: references `defects(id)` ON DELETE RESTRICT.
- **Indexes**:
  - `idx_localization_defect`: B-tree (`defect_id`)

---

## 8. Domain 7: Reporting and System Administration

### 8.1 Table: `inspection_reports`
- **Purpose**: Persisted record of generated inspection compliance certificates and exported analysis documents.
- **Physical Name**: `inspection_reports`
- **Retention / Archival**: Permanent compliance record. Retained indefinitely.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_inspection_reports`). |
| `report_id` | VARCHAR(64) | NO | None | Public unique report identifier (e.g. `REP-20261030-001`). Unique. |
| `inspection_id` | BIGINT / INTEGER | NO | None | Foreign key referencing `inspections.id`. Delete: `RESTRICT`. |
| `report_type` | VARCHAR(32) | NO | 'FULL_COMPLIANCE' | Type: `EXECUTIVE_SUMMARY`, `FULL_COMPLIANCE`, `MAINTENANCE_WORKORDER`. |
| `report_format` | VARCHAR(16) | NO | 'PDF' | Export format: `PDF`, `JSON`, `CSV`. |
| `file_path` | VARCHAR(512) | NO | None | Relative path to report document on disk (`reports/insp_1_full.pdf`). Unique. |
| `file_size_bytes` | INT | NO | None | File size in bytes. Check: `file_size_bytes > 0`. |
| `checksum_sha256` | VARCHAR(64) | NO | None | Cryptographic SHA-256 integrity hash of generated report file. |
| `overall_rating` | VARCHAR(8) | NO | 'B' | Compliance grade: `A`, `B`, `C`, `D`, `FAIL`. |
| `generated_by` | VARCHAR(64) | NO | None | Operator badge or user identifier who compiled report. |
| `generated_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC timestamp of report compilation. |

- **Primary Key**: `pk_inspection_reports (id)`
- **Foreign Keys**: `fk_reports_inspection_id`: references `inspections(id)` ON DELETE RESTRICT.
- **Indexes**:
  - `uq_reports_report_id`: UNIQUE (`report_id`)
  - `uq_reports_file_path`: UNIQUE (`file_path`)
  - `idx_reports_inspection`: B-tree (`inspection_id`)

---

### 8.2 Table: `audit_events`
- **Purpose**: Append-only non-repudiation audit trail for security and regulatory compliance.
- **Physical Name**: `audit_events`
- **Retention / Archival**: Permanent compliance record. Hard deletion and updates strictly prohibited.

| Column Name | SQL Type (PG / SQLite) | Nullable | Default | Constraints & Descriptions |
|---|---|---|---|---|
| `id` | BIGINT / INTEGER | NO | AUTOINCREMENT | Primary key (`pk_audit_events`). |
| `entity_type` | VARCHAR(64) | NO | None | Affected entity type: `INSPECTION`, `DEFECT`, `MODEL_CONFIG`, `SYSTEM_SETTING`. |
| `entity_id` | VARCHAR(64) | NO | None | Identifier of affected record (string or integer ID). |
| `action` | VARCHAR(32) | NO | None | Action performed: `CREATE`, `UPDATE`, `ARCHIVE`, `DELETE`, `REVIEW_OVERRIDE`. |
| `performed_by` | VARCHAR(64) | NO | None | Authenticated username, technician badge, or IP address. |
| `before_state` | JSONB / TEXT | YES | NULL | Prior record state snapshot serialized as JSON. |
| `after_state` | JSONB / TEXT | YES | NULL | Updated record state snapshot serialized as JSON. |
| `client_ip` | VARCHAR(45) | YES | NULL | Network IP address of client issuing request. |
| `recorded_at` | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | UTC timestamp of audit entry. Indexed. |

- **Primary Key**: `pk_audit_events (id)`
- **Foreign Keys**: None (Decoupled audit log to ensure records survive parent partition detaches).
- **Indexes**:
  - `idx_audit_recorded`: B-tree (`recorded_at DESC`)
  - `idx_audit_entity`: B-tree (`entity_type`, `entity_id`)

