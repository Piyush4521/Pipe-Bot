# PipeBot Database Engineering: Data Requirements and Entity Inventory

## 1. Executive Overview

This document specifies the complete data requirements and conceptual entity model for PipeBot, an AI-powered robotic PVC pipeline inspection platform. It defines domain boundaries, core entities, field attributes, relationships, data volume calculations, and hardware parameter dependencies.

The architecture balances two distinct persistence paradigms:
1. **Transactional Domain Data**: Inspection lifecycles, operator reviews, defect categorizations, and system audit logs requiring strict ACID guarantees and relational referential integrity.
2. **High-Frequency Time-Series Data**: Wheel encoder ticks, IMU inertial measurements, device heartbeats, and video frame metadata requiring low-latency bulk append operations and temporal range querying.

---

## 2. Conceptual Entity Inventory and Classification

Entities are categorized by functional domain and classified by priority:
- **Essential (Prototype Phase)**: Required for immediate inspection management, real-time telemetry streaming, AI defect logging, and operator review.
- **Optional (Future Expansion)**: Deferred until multi-crawler fleet operations, automated multi-sensor calibration, or distributed multi-tenant deployments are scheduled.

---

### Domain A: Inspection Management

#### 1. Inspection (Essential)
- **Purpose**: The central root entity representing an individual pipeline examination run.
- **Key Attributes**:
  - `id` (UUID / Integer, Primary Key)
  - `inspection_code` (String, unique human-readable identifier, e.g., `INSP-20261030-001`)
  - `pipe_id` (String, identifier of physical pipeline section)
  - `operator_name` (String, name or badge ID of technician)
  - `location` (String, geographic or facility zone)
  - `pipe_diameter_mm` (Float, nominal inner diameter of pipeline)
  - `status` (Enum: `PENDING`, `RUNNING`, `PAUSED`, `STOPPED`, `COMPLETED`, `ARCHIVED`)
  - `started_at` (UtcDateTime, nullable)
  - `completed_at` (UtcDateTime, nullable)
  - `total_distance_meters` (Float, cumulative distance inspected)
  - `notes` (Text, optional operator annotations)
  - `is_archived` (Boolean, soft-archive flag for historical retention)
  - `is_deleted` (Boolean, soft-delete flag preventing destructive data loss)
  - `created_at`, `updated_at` (UtcDateTime)
- **Relationships**: 1-to-many with Device Sessions, Encoder Samples, IMU Samples, Defect Detections, Frame Metadata, Inspection Events, and Reports.
- **Classification**: Transactional.
- **Expected Volume**: 1 to 20 records per crawler per day.

#### 2. Inspection Event (Essential)
- **Purpose**: Tracks operational milestones and state transitions throughout an inspection run.
- **Key Attributes**:
  - `id` (UUID / Integer, Primary Key)
  - `inspection_id` (Foreign Key -> Inspection)
  - `event_type` (Enum: `STARTED`, `PAUSED`, `RESUMED`, `STOPPED`, `COMPLETED`, `NOTE_ADDED`, `OBSTACLE_ENCOUNTERED`)
  - `payload` (JSON, contextual metadata such as distance or operator notes)
  - `occurred_at` (UtcDateTime)
- **Relationships**: Many-to-1 with Inspection.
- **Classification**: Transactional.
- **Expected Volume**: 5 to 50 records per inspection.

#### 3. Inspection Status History (Optional - Future Expansion)
- **Purpose**: Formal audit log of state machine transitions. In the prototype, this is adequately captured by `Inspection Event`.
- **Classification**: Transactional audit log.

#### 4. Inspection Summary (Essential - Computed View / Table)
- **Purpose**: Denormalized aggregate statistics computed upon inspection completion for fast dashboard rendering.
- **Key Attributes**:
  - `inspection_id` (Primary Key, Foreign Key -> Inspection)
  - `total_duration_seconds` (Integer)
  - `total_distance_meters` (Float)
  - `total_defects_count` (Integer)
  - `deformation_count` (Integer)
  - `misalignment_count` (Integer)
  - `obstacle_count` (Integer)
  - `rupture_count` (Integer)
  - `overall_pipe_grade` (Enum / String: `A`, `B`, `C`, `D`, `FAIL`)
- **Relationships**: 1-to-1 with Inspection.
- **Classification**: Transactional analytical snapshot.

---

### Domain B: Hardware and Device Management

#### 1. Device (Essential)
- **Purpose**: Inventory of physical microcontrollers and camera modules mounted on the crawler.
- **Key Attributes**:
  - `id` (String / UUID, Primary Key, e.g., `esp32-crawler-01`, `cam-sensor-01`)
  - `device_type` (Enum: `CONTROLLER_WROOM32`, `CAMERA_ESP32CAM`, `ENVIRONMENTAL_SENSOR`)
  - `mac_address` (String, unique hardware MAC)
  - `firmware_version` (String, semantic version)
  - `is_active` (Boolean)
- **Classification**: Master Configuration.
- **Expected Volume**: 2 to 5 records per crawler unit.

#### 2. Device Session (Essential)
- **Purpose**: Tracks a single continuous connection session of a hardware module during an inspection.
- **Key Attributes**:
  - `id` (UUID, Primary Key)
  - `device_id` (Foreign Key -> Device)
  - `inspection_id` (Foreign Key -> Inspection, nullable if disconnected outside run)
  - `boot_id` (Integer / String, hardware boot counter)
  - `connected_at` (UtcDateTime)
  - `disconnected_at` (UtcDateTime, nullable)
  - `ip_address` (String)
  - `disconnect_reason` (String, nullable)
- **Relationships**: Many-to-1 with Device and Inspection; 1-to-many with Heartbeats and Telemetry.
- **Classification**: Transactional.
- **Expected Volume**: 1 to 5 records per inspection per device.

#### 3. Device Heartbeat (Essential - Time-Series)
- **Purpose**: High-level periodic pulse monitoring health, WiFi RSSI, battery voltage, and free heap.
- **Key Attributes**:
  - `id` (Integer / UUID, Primary Key)
  - `session_id` (Foreign Key -> Device Session)
  - `device_id` (Foreign Key -> Device)
  - `rssi` (Integer, dBm)
  - `battery_millivolts` (Integer, mV)
  - `free_heap_bytes` (Integer)
  - `uptime_ms` (Integer)
  - `recorded_at` (UtcDateTime, backend ingest timestamp)
- **Classification**: Time-Series (Low frequency, 0.5 to 1.0 Hz).
- **Expected Volume**: 600 to 3,600 records per 60-minute inspection.

#### 4. Vehicle Status Event (Essential)
- **Purpose**: Records discrete motor operational changes, emergency stops, or stall warnings.
- **Key Attributes**:
  - `id` (UUID, Primary Key)
  - `inspection_id` (Foreign Key -> Inspection)
  - `drive_mode` (Enum: `MANUAL`, `AUTONOMOUS`, `REVERSE`, `ESTOP`)
  - `left_motor_pwm` (Integer, 0-255)
  - `right_motor_pwm` (Integer, 0-255)
  - `warning_flags` (Integer, bitmask)
  - `recorded_at` (UtcDateTime)
- **Classification**: Event-driven transactional.
- **Expected Volume**: 10 to 200 records per inspection.

---

### Domain C: Telemetry Management

#### 1. Encoder Sample (Essential - High Frequency Time-Series)
- **Purpose**: Dual-wheel optical/magnetic encoder cumulative counts and velocity metrics.
- **Key Attributes**:
  - `id` (BigInt, Primary Key)
  - `inspection_id` (Foreign Key -> Inspection)
  - `device_id` (String, identifier of controller)
  - `sequence_number` (BigInt, sequential per device boot)
  - `left_cumulative_ticks` (BigInt, cumulative pulse count)
  - `right_cumulative_ticks` (BigInt, cumulative pulse count)
  - `left_rpm` (Float, nullable, calculated rotations per minute)
  - `right_rpm` (Float, nullable, calculated rotations per minute)
  - `device_uptime_ms` (BigInt, device timer clock)
  - `device_timestamp` (UtcDateTime, nullable, if device RTC is configured)
  - `recorded_at` (UtcDateTime, backend network arrival timestamp)
- **Relationships**: Many-to-1 with Inspection.
- **Classification**: Time-Series.
- **Expected Volume**: 36,000 to 180,000 records per 60-minute inspection (at 10 Hz to 50 Hz).

#### 2. IMU Sample (Essential - High Frequency Time-Series)
- **Purpose**: 6-axis inertial motion telemetry (MPU6050 accelerometer and gyroscope).
- **Key Attributes**:
  - `id` (BigInt, Primary Key)
  - `inspection_id` (Foreign Key -> Inspection)
  - `device_id` (String)
  - `sequence_number` (BigInt)
  - `accel_x` (Float, linear acceleration axis X)
  - `accel_y` (Float, linear acceleration axis Y)
  - `accel_z` (Float, linear acceleration axis Z)
  - `gyro_x` (Float, angular velocity axis X)
  - `gyro_y` (Float, angular velocity axis Y)
  - `gyro_z` (Float, angular velocity axis Z)
  - `sensor_units` (String, raw LSB vs calibrated m/s2 and deg/s)
  - `temperature_c` (Float, nullable internal sensor temperature)
  - `device_uptime_ms` (BigInt)
  - `recorded_at` (UtcDateTime)
- **Relationships**: Many-to-1 with Inspection.
- **Classification**: Time-Series.
- **Expected Volume**: 36,000 to 180,000 records per 60-minute inspection (at 10 Hz to 50 Hz).

#### 3. Sensor Calibration Record (Optional - Future Expansion)
- **Purpose**: Calibration offsets and scale factors for wheel diameter, encoder ticks-per-meter, and IMU zero-rate drift.

---

### Domain D: Camera and Media Metadata

#### 1. Frame Metadata (Essential)
- **Purpose**: Metadata record for camera frames received by backend. Video frames are never stored as database BLOBs.
- **Key Attributes**:
  - `id` (UUID, Primary Key)
  - `inspection_id` (Foreign Key -> Inspection)
  - `camera_id` (String, e.g., `esp32-cam-front`)
  - `frame_sequence` (BigInt, monotonic counter from camera)
  - `frame_width` (Integer, pixels)
  - `frame_height` (Integer, pixels)
  - `frame_encoding` (String, e.g., `image/jpeg`)
  - `frame_bytes` (Integer, payload size in bytes)
  - `capture_timestamp` (UtcDateTime, camera optical exposure timestamp if provided, else backend arrival)
  - `recorded_at` (UtcDateTime, backend receipt timestamp)
  - `processing_status` (Enum: `PENDING`, `INFERRED`, `DROPPED`, `STORED`)
  - `has_defect` (Boolean, default False)
- **Relationships**: Many-to-1 with Inspection; 1-to-many with Defect Detections.
- **Classification**: Time-Series / Relational metadata.
- **Expected Volume**: 18,000 to 36,000 records per 60-minute inspection (at 5 to 10 FPS).

#### 2. Evidence Media Reference (Essential)
- **Purpose**: File pointer and cryptographic hash for localized defect crop images stored on filesystem.
- **Key Attributes**:
  - `id` (UUID, Primary Key)
  - `defect_id` (Foreign Key -> Defect)
  - `file_path` (String, relative path from storage root, e.g., `media/crops/insp_1/def_42.jpg`)
  - `mime_type` (String, e.g., `image/jpeg`)
  - `file_size_bytes` (Integer)
  - `checksum_sha256` (String, integrity validation hash)
  - `storage_backend` (Enum: `LOCAL_FS`, `S3`, `MINIO`)
  - `created_at` (UtcDateTime)
- **Relationships**: 1-to-1 or Many-to-1 with Defect.
- **Classification**: Transactional media index.
- **Expected Volume**: 5 to 100 records per inspection.

---

### Domain E: AI Inference and Defect Management

#### 1. AI Model Version (Essential)
- **Purpose**: Provenance tracking of computer vision models deployed for automated pipeline inspection.
- **Key Attributes**:
  - `id` (UUID, Primary Key)
  - `model_name` (String, e.g., `yolov8n-pipebot`)
  - `model_version` (String, semantic version or training run ID, e.g., `v1.2.0-baseline`)
  - `artifact_path` (String, relative path to model weights file, e.g., `weights/yolov8_pipe_v1.onnx`)
  - `artifact_checksum_sha256` (String, model weights file hash)
  - `training_dataset_id` (String, nullable dataset reference)
  - `class_mapping` (JSON, exact index-to-label map: `{"0":"Deformation","1":"Misalignment","2":"Obstacle","3":"Rupture"}`)
  - `input_dimensions` (String, e.g., `640x640`)
  - `inference_backend` (Enum: `ONNX_RUNTIME`, `ULTRALYTICS_PYTORCH`, `OPENVINO`)
  - `is_active` (Boolean)
  - `created_at` (UtcDateTime)
- **Classification**: Master Configuration.
- **Expected Volume**: 1 to 10 records total. Model weights files remain on the filesystem and are never stored as database BLOBs.

#### 2. Defect Detection (Essential)
- **Purpose**: Represents an identified pipeline flaw, preserving canonical class, confidence, bounding box, localization, and review lifecycle.
- **Key Attributes**:
  - `id` (Integer / UUID, Primary Key)
  - `inspection_id` (Foreign Key -> Inspection)
  - `frame_id` (Foreign Key -> Frame Metadata, nullable)
  - `model_version_id` (Foreign Key -> AI Model Version, nullable for manual defects)
  - `defect_class` (Enum: `Deformation`, `Misalignment`, `Obstacle`, `Rupture`)
  - `confidence` (Float, range 0.0000 to 1.0000)
  - `severity` (Enum: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, default `MEDIUM`)
  - `box_x` (Float, normalized 0.0-1.0 coordinate)
  - `box_y` (Float, normalized 0.0-1.0 coordinate)
  - `box_width` (Float, normalized 0.0-1.0 dimension)
  - `box_height` (Float, normalized 0.0-1.0 dimension)
  - `snapshot_path` (String, relative path to evidence snapshot)
  - `estimated_distance_meters` (Float, nullable physical pipeline distance)
  - `localization_status` (Enum: `UNVERIFIED_SYNC`, `SYNCHRONIZED`, `MANUAL_OVERRIDE`, `ESTIMATED`, default `UNVERIFIED_SYNC`)
  - `localization_notes` (String, explanation of sync or distance status)
  - `review_status` (Enum: `PENDING_REVIEW`, `CONFIRMED`, `REJECTED`, `RECLASSIFIED`, default `PENDING_REVIEW`)
  - `reviewed_by` (String, operator identifier)
  - `reviewed_at` (UtcDateTime, nullable)
  - `operator_notes` (Text, optional review justification)
  - `is_deleted` (Boolean, soft deletion flag)
  - `detected_at` (UtcDateTime, frame/inference timestamp)
  - `created_at`, `updated_at` (UtcDateTime)
- **Relationships**: Many-to-1 with Inspection; Many-to-1 with AI Model Version; 1-to-1 with Frame Metadata and Evidence Media Reference.
- **Classification**: Transactional.
- **Expected Volume**: 5 to 100 records per inspection.

#### 3. Defect Review History (Optional - Future Expansion)
- **Purpose**: Fine-grained audit log of operator review overrides (class reassignments, severity adjustments). In prototype, captured directly on `Defect Detection` review fields and `Audit Event`.

---

### Domain F: Localization and Spatial Mapping

#### 1. Localization Association Record (Essential - Spatial Mapping)
- **Purpose**: Encapsulates the optical frame to encoder correlation, keeping timestamp discrepancies explicit.
- **Key Attributes**:
  - `id` (UUID, Primary Key)
  - `defect_id` (Foreign Key -> Defect Detection)
  - `frame_id` (Foreign Key -> Frame Metadata)
  - `frame_capture_timestamp` (UtcDateTime)
  - `encoder_sample_timestamp` (UtcDateTime)
  - `temporal_delta_ms` (Float, absolute difference between optical exposure and odometer tick)
  - `clock_sync_status` (Enum: `UNVERIFIED`, `VERIFIED_PTP`, `VERIFIED_HARDWARE_PULSE`, `INFERRED_APPROX`)
  - `left_encoder_ticks` (BigInt)
  - `right_encoder_ticks` (BigInt)
  - `computed_distance_meters` (Float, nullable)
  - `created_at` (UtcDateTime)
- **Classification**: Relational analytical record.

---

### Domain G: Reporting and Export

#### 1. Inspection Report (Essential)
- **Purpose**: Persisted record of generated inspection certificates and analytical summaries.
- **Key Attributes**:
  - `id` (UUID, Primary Key)
  - `inspection_id` (Foreign Key -> Inspection)
  - `report_type` (Enum: `EXECUTIVE_SUMMARY`, `FULL_DEFECT_CATALOG`, `MAINTENANCE_WORKORDER`)
  - `report_format` (Enum: `PDF`, `JSON`, `CSV`)
  - `file_path` (String, relative path to generated file, e.g., `reports/insp_1_full.pdf`)
  - `file_size_bytes` (Integer)
  - `checksum_sha256` (String)
  - `generated_by` (String, operator or system user)
  - `generated_at` (UtcDateTime)
- **Relationships**: Many-to-1 with Inspection.
- **Classification**: Transactional document registry.
- **Expected Volume**: 1 to 5 records per inspection.

---

### Domain H: System Administration and Audit

#### 1. Audit Event (Essential)
- **Purpose**: Non-repudiation audit trail for security-critical actions (inspection archival, defect reclassification, manual overrides).
- **Key Attributes**:
  - `id` (BigInt, Primary Key)
  - `entity_type` (String, e.g., `INSPECTION`, `DEFECT`, `SYSTEM_CONFIG`)
  - `entity_id` (String)
  - `action` (Enum: `CREATE`, `UPDATE`, `ARCHIVE`, `DELETE`, `REVIEW_OVERRIDE`)
  - `performed_by` (String, username or client IP)
  - `before_state` (JSON, nullable)
  - `after_state` (JSON, nullable)
  - `recorded_at` (UtcDateTime)
- **Classification**: Transactional audit log (Append-only).
- **Expected Volume**: 20 to 200 records per inspection.

---

## 3. Data Volume Calculations and Storage Projections

Calculations are modeled across three hypothetical sampling rates (10 Hz, 20 Hz, 50 Hz) and three realistic operational durations (10 min, 30 min, 60 min) for a single inspection run.

### 3.1 Telemetry Row Generation Rates

| Stream | 10 Hz | 20 Hz | 50 Hz |
|---|---|---|---|
| **Encoder Samples / sec** | 10 rows/s | 20 rows/s | 50 rows/s |
| **IMU Samples / sec** | 10 rows/s | 20 rows/s | 50 rows/s |
| **Combined Telemetry / sec** | 20 rows/s | 40 rows/s | 100 rows/s |

### 3.2 Total Records per Inspection Run

| Ingestion Rate | 10 Minutes (600s) | 30 Minutes (1,800s) | 60 Minutes (3,600s) |
|---|---|---|---|
| **Encoder Samples @ 10 Hz** | 6,000 rows | 18,000 rows | 36,000 rows |
| **Encoder Samples @ 20 Hz** | 12,000 rows | 36,000 rows | 72,000 rows |
| **Encoder Samples @ 50 Hz** | 30,000 rows | 90,000 rows | 180,000 rows |
| **IMU Samples @ 10 Hz** | 6,000 rows | 18,000 rows | 36,000 rows |
| **IMU Samples @ 20 Hz** | 12,000 rows | 36,000 rows | 72,000 rows |
| **IMU Samples @ 50 Hz** | 30,000 rows | 90,000 rows | 180,000 rows |
| **Camera Frames @ 5 FPS** | 3,000 rows | 9,000 rows | 18,000 rows |
| **Camera Frames @ 10 FPS** | 6,000 rows | 18,000 rows | 36,000 rows |
| **Defect Detections (estimated)** | 5 to 20 rows | 15 to 50 rows | 30 to 100 rows |

### 3.3 Storage Footprint Projections

Assuming relational column byte widths in PostgreSQL (including row headers and B-tree indexes):
- `Encoder Sample`: ~120 bytes per row (with indexes)
- `IMU Sample`: ~160 bytes per row (with indexes)
- `Frame Metadata`: ~180 bytes per row
- `Defect Record`: ~400 bytes per row
- `Crop Evidence Image (Filesystem)`: ~50 KB to 150 KB per image (average 100 KB)

#### Estimated Storage for a 60-Minute Inspection (at 20 Hz Telemetry, 5 FPS Frames, 50 Defects):
- **Encoder Table**: 72,000 rows * 120 bytes = 8.64 MB
- **IMU Table**: 72,000 rows * 160 bytes = 11.52 MB
- **Frame Metadata Table**: 18,000 rows * 180 bytes = 3.24 MB
- **Defect Records Table**: 50 rows * 400 bytes = 20 KB
- **Inspection and Event Tables**: < 50 KB
- **Total Relational Database Growth**: **~23.5 MB per 1-hour inspection**
- **Filesystem Media Growth**: 50 defect crops * 100 KB = **~5.0 MB per 1-hour inspection**

#### Monthly Projection (20 Inspections per Month):
- **Relational Storage**: ~470 MB / month (~5.6 GB / year)
- **Filesystem Media Storage**: ~100 MB / month (~1.2 GB / year)

*Conclusion*: Data volume is well within the capabilities of a standard PostgreSQL 16 instance. High row counts require partition management and index optimization rather than multi-node sharding or distributed databases.

---

## 4. Unverified Hardware Specifications

The database schema and physical calculations must accommodate the physical reality that several hardware specifications and firmware contracts remain unverified on the physical crawler.

The following parameters must be treated as unverified configuration inputs and must not be hardcoded in database schemas or queries:

1. **Encoder Tick Resolution**:
   - Status: Unverified.
   - Impact: Number of pulses per wheel revolution depends on the optical encoder disc slotted grating and hall-sensor pole count. Hardcoding ticks-to-meters conversion in database triggers or queries is strictly prohibited.
2. **Wheel Diameter and Effective Contact Geometry**:
   - Status: Unverified.
   - Impact: Crawler wheel diameter, tread wear, and compression against PVC pipe curve dictate linear travel distance per revolution. Must remain an external calibration parameter.
3. **Gearbox Reduction Ratio**:
   - Status: Unverified.
   - Impact: Motor-to-wheel gear ratio affects RPM calculations and odometer integration.
4. **IMU Sensor Physical Units**:
   - Status: Unverified.
   - Impact: MPU6050 output may arrive as raw 16-bit integer two's complement ADC values (LSB) or converted floating-point SI units (m/s2 for acceleration, deg/s or rad/s for angular velocity). Schema must explicitly store `sensor_units` string or enum alongside values until firmware contracts are frozen.
5. **Telemetry Sampling and Ingestion Frequency**:
   - Status: Unverified.
   - Impact: ESP32-WROOM-32 transmission loop rate over WiFi UDP/TCP/WebSocket is not yet empirically tested under motor vibration and RF noise. System must handle variable frequencies between 5 Hz and 50 Hz without schema modification.
6. **Dual-MCU Shutter Clock Synchronization**:
   - Status: Unverified.
   - Impact: ESP32-CAM optical frame exposure time cannot be assumed identical to ESP32-WROOM-32 encoder transmission time. Until physical hardware synchronization (e.g., GPIO strobe or hardware PTP) is deployed, `estimated_distance_meters` must be nullable and default to NULL.

