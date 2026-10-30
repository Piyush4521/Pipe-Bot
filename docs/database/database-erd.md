# PipeBot Database Engineering: Entity-Relationship Diagram and Relational Model

## 1. Executive Summary

This document presents the reconciled conceptual and logical Entity-Relationship (ER) model for the PipeBot pipeline inspection system. It incorporates the Stage 2 logical schema design refinements, reconciling the Stage 1 conceptual diagram with the active backend implementation (`backend/app/models/`, `backend/app/schemas/`, `backend/migrations/`).

The model enforces audit-preserving integrity: inspection runs, defect evidence, and compliance reports use restrictive foreign-key constraints (`ON DELETE RESTRICT`) and soft-archival flags (`is_archived`, `is_deleted`) to prevent accidental destruction of physical inspection records.

---

## 2. Mermaid Entity-Relationship Diagram

```mermaid
erDiagram
    INSPECTION ||--o{ INSPECTION_EVENT : "logs"
    INSPECTION ||--o| INSPECTION_SUMMARY : "summarizes"
    INSPECTION ||--o{ DEVICE_SESSION : "hosts"
    INSPECTION ||--o{ VEHICLE_STATUS_EVENT : "records"
    INSPECTION ||--o{ ENCODER_TELEMETRY : "records"
    INSPECTION ||--o{ IMU_TELEMETRY : "records"
    INSPECTION ||--o{ CAMERA_FRAME : "captures"
    INSPECTION ||--o{ DEFECT : "contains"
    INSPECTION ||--o{ INSPECTION_REPORT : "generates"

    DEVICE ||--o{ DEVICE_SESSION : "establishes"
    DEVICE_SESSION ||--o{ DEVICE_HEARTBEAT : "pulses"
    DEVICE_SESSION ||--o{ ENCODER_TELEMETRY : "streams"
    DEVICE_SESSION ||--o{ IMU_TELEMETRY : "streams"

    AI_MODEL_VERSION ||--o{ DEFECT : "detects"
    CAMERA_FRAME ||--o{ DEFECT : "exhibits"
    
    DEFECT ||--|| EVIDENCE_MEDIA : "references"
    DEFECT ||--o| LOCALIZATION_RECORD : "associates"

    INSPECTION {
        bigint id PK
        string inspection_id UK
        string pipe_identifier
        string pipe_material
        int pipe_diameter_mm
        string operator_id
        string status
        timestamp started_at
        timestamp completed_at
        float total_distance_meters
        text notes
        boolean is_archived
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }

    INSPECTION_SUMMARY {
        bigint inspection_id PK_FK
        int total_defects_count
        int deformation_count
        int misalignment_count
        int obstacle_count
        int rupture_count
        string overall_pipe_grade
        int total_runtime_seconds
        timestamp compiled_at
    }

    INSPECTION_EVENT {
        bigint id PK
        bigint inspection_id FK
        string event_type
        jsonb payload
        timestamp occurred_at
    }

    DEVICE {
        string id PK
        string device_type
        string mac_address UK
        string firmware_version
        boolean is_active
        timestamp created_at
    }

    DEVICE_SESSION {
        bigint id PK
        string session_uuid UK
        string device_id FK
        bigint inspection_id FK
        string boot_id
        string ip_address
        timestamp connected_at
        timestamp disconnected_at
        string disconnect_reason
    }

    DEVICE_HEARTBEAT {
        bigint id PK
        bigint session_id FK
        string device_id FK
        int rssi_dbm
        int battery_millivolts
        float battery_percent
        int free_heap_bytes
        float uptime_seconds
        timestamp recorded_at
    }

    VEHICLE_STATUS_EVENT {
        bigint id PK
        bigint inspection_id FK
        bigint session_id FK
        string drive_mode
        string left_motor_state
        string right_motor_state
        boolean emergency_stop
        timestamp recorded_at
    }

    ENCODER_TELEMETRY {
        bigint id PK
        bigint inspection_id FK
        bigint session_id FK
        bigint sequence_number
        bigint left_ticks
        bigint right_ticks
        float left_rpm
        float right_rpm
        float speed_mps
        string direction
        bigint device_uptime_ms
        timestamp device_timestamp
        timestamp recorded_at
    }

    IMU_TELEMETRY {
        bigint id PK
        bigint inspection_id FK
        bigint session_id FK
        bigint sequence_number
        float accel_x
        float accel_y
        float accel_z
        float gyro_x
        float gyro_y
        float gyro_z
        float pitch_deg
        float roll_deg
        float yaw_deg
        float temperature_c
        string sensor_units
        bigint device_uptime_ms
        timestamp device_timestamp
        timestamp recorded_at
    }

    CAMERA_FRAME {
        bigint id PK
        string frame_id UK
        bigint inspection_id FK
        string camera_id
        bigint frame_sequence
        int frame_width
        int frame_height
        string encoding
        int frame_bytes
        timestamp capture_timestamp
        timestamp recorded_at
        string processing_status
        boolean has_defect
    }

    AI_MODEL_VERSION {
        bigint id PK
        string model_name
        string model_version UK
        string artifact_path
        string artifact_checksum_sha256
        string training_dataset_id
        jsonb class_mapping
        string input_dimensions
        float confidence_threshold
        string inference_backend
        boolean is_active
        timestamp created_at
    }

    DEFECT {
        bigint id PK
        string defect_id UK
        bigint inspection_id FK
        string frame_id
        bigint model_version_id FK
        string defect_class
        float confidence
        string severity
        jsonb bounding_box
        timestamp capture_timestamp
        timestamp inference_timestamp
        float estimated_distance_meters
        string review_status
        string reviewed_by
        timestamp reviewed_at
        string snapshot_path
        text notes
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }

    EVIDENCE_MEDIA {
        bigint id PK
        string media_uuid UK
        bigint defect_id FK
        string file_path UK
        string mime_type
        int file_size_bytes
        string checksum_sha256
        string storage_backend
        timestamp created_at
    }

    LOCALIZATION_RECORD {
        bigint id PK
        bigint defect_id FK
        string frame_id
        timestamp frame_capture_timestamp
        timestamp encoder_sample_timestamp
        float temporal_delta_ms
        string clock_sync_status
        string sync_notes
        bigint left_encoder_ticks
        bigint right_encoder_ticks
        float computed_distance_meters
        timestamp created_at
    }

    INSPECTION_REPORT {
        bigint id PK
        string report_id UK
        bigint inspection_id FK
        string report_type
        string report_format
        string file_path UK
        int file_size_bytes
        string checksum_sha256
        string overall_rating
        string generated_by
        timestamp generated_at
    }

    AUDIT_EVENT {
        bigint id PK
        string entity_type
        string entity_id
        string action
        string performed_by
        jsonb before_state
        jsonb after_state
        string client_ip
        timestamp recorded_at
    }
```

---

## 3. Reconciled Schema Corrections from Stage 1

During Stage 2 detailed table specifications and compatibility audits, the following corrections were incorporated into the ER diagram:
1. **Primary and Foreign Key Types**:
   - Replaced theoretical `UUID` primary keys on `INSPECTION` and `DEFECT` with `bigint id PK` (autoincrement integer rowid) and explicit business key strings (`string inspection_id UK`, `string defect_id UK`). This matches the existing operational SQLite schema (`backend/app/models/inspection.py` and `backend/app/models/defect.py`) and avoids breaking the dual-lookup API contract.
   - Updated all foreign keys referencing inspections and defects to `bigint FK`.
2. **Entity Additions**:
   - Added `INSPECTION_SUMMARY` (1-to-1 extension of `INSPECTION`) to model pre-aggregated compliance grades and defect metrics without expensive joins.
   - Added `VEHICLE_STATUS_EVENT` (1-to-many from `INSPECTION`) to record discrete drive modes, emergency stop assertions, and motor actuation changes.
3. **Telemetry Column Names Reconciled with Existing Contracts**:
   - Updated `ENCODER_TELEMETRY` column names from `left_cumulative_ticks` / `right_cumulative_ticks` to `left_ticks` / `right_ticks`, exactly matching `EncoderTelemetryIngest` Pydantic schemas and frontend interfaces.
   - Updated `DEFECT` bounding box model from individual coordinate columns (`box_x`, `box_y`, `box_width`, `box_height`) to standardized `jsonb bounding_box` matching the active database model and Alembic migration `d4d255efae0c`.
4. **Media and Localization Relationships**:
   - Preserved `EVIDENCE_MEDIA` (1-to-1 with `DEFECT`) and `LOCALIZATION_RECORD` (1-to-0..1 with `DEFECT`), with `defect_id` typed as `bigint FK` referencing `DEFECT.id`.

---

## 4. Referential Integrity Rules and Constraints

1. **Non-Destructive Operations**:
   - Primary business entities (`INSPECTION`, `DEFECT`) must never be deleted through standard operator workflows. Soft deletion (`is_deleted = TRUE`) and soft archival (`is_archived = TRUE`) are enforced.
2. **Strict Foreign Key Action Specification**:
   - `INSPECTION` -> `DEFECT`: `ON UPDATE CASCADE, ON DELETE RESTRICT`.
   - `DEFECT` -> `EVIDENCE_MEDIA`: `ON UPDATE CASCADE, ON DELETE RESTRICT`.
   - `AI_MODEL_VERSION` -> `DEFECT`: `ON UPDATE CASCADE, ON DELETE RESTRICT`.
   - `DEVICE_SESSION` -> `DEVICE_HEARTBEAT`: `ON UPDATE CASCADE, ON DELETE CASCADE`.
3. **Canonical Value Validation**:
   - `DEFECT.defect_class`: Restricted to `Deformation`, `Misalignment`, `Obstacle`, `Rupture`.
   - `DEFECT.confidence`: Check constraint `confidence >= 0.0 AND confidence <= 1.0`.
   - `INSPECTION.status`: Restricted to `created`, `in_progress`, `paused`, `completed`, `failed`, `cancelled`.
