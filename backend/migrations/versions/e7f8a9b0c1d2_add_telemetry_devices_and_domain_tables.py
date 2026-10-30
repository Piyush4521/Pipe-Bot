"""add_telemetry_devices_and_domain_tables

Revision ID: e7f8a9b0c1d2
Revises: d4d255efae0c
Create Date: 2026-10-30 23:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, None] = 'd4d255efae0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_bigint_id():
    """Cross-engine integer ID: compiles to INTEGER on SQLite (rowid) and BIGINT on PostgreSQL."""
    return sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    # 1. Create devices table (master hardware registry)
    op.create_table(
        'devices',
        sa.Column('id', sa.String(length=64), nullable=False, comment='Unique hardware identifier string'),
        sa.Column('device_type', sa.String(length=32), nullable=False, comment='Hardware class: ESP32_WROOM, ESP32_CAM, PROCESSING_SERVER'),
        sa.Column('mac_address', sa.String(length=32), nullable=True, comment='Physical MAC address of network interface'),
        sa.Column('firmware_version', sa.String(length=32), nullable=True, comment='Semantic firmware version string'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true(), comment='Whether device is authorized for field operation'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='Device registration timestamp'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_devices')),
        sa.UniqueConstraint('mac_address', name=op.f('uq_devices_mac_address')),
    )

    # 2. Create ai_model_versions table
    op.create_table(
        'ai_model_versions',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('model_name', sa.String(length=64), nullable=False, comment='Human-readable model architecture (e.g. yolov8n-pipebot)'),
        sa.Column('model_version', sa.String(length=64), nullable=False, comment='Semantic version identifier (e.g. v1.0.0-baseline)'),
        sa.Column('artifact_path', sa.String(length=256), nullable=False, comment='Relative path to model weights file on disk'),
        sa.Column('artifact_checksum_sha256', sa.String(length=64), nullable=False, comment='Cryptographic SHA-256 hash of model weights file'),
        sa.Column('training_dataset_id', sa.String(length=64), nullable=True, comment='Reference to training dataset version'),
        sa.Column('class_mapping', sa.JSON(), nullable=False, comment='Canonical class ID to name dictionary'),
        sa.Column('input_dimensions', sa.String(length=32), nullable=False, server_default='640x640', comment='Input image resolution expected by model'),
        sa.Column('confidence_threshold', sa.Float(), nullable=False, server_default='0.25', comment='Default minimum inference confidence threshold'),
        sa.Column('inference_backend', sa.String(length=32), nullable=False, server_default='ULTRALYTICS', comment='Runtime provider: ULTRALYTICS, ONNX_RUNTIME, OPENVINO'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true(), comment='Whether model is active for live camera inference'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='Model registration timestamp'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_model_versions')),
        sa.UniqueConstraint('model_version', name=op.f('uq_ai_model_versions_model_version')),
    )
    op.create_index(op.f('ix_ai_model_versions_model_version'), 'ai_model_versions', ['model_version'], unique=True)

    # 3. Create device_sessions table
    op.create_table(
        'device_sessions',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('session_uuid', sa.String(length=64), nullable=False, comment='Public session UUID identifier'),
        sa.Column('device_id', sa.String(length=64), nullable=False, comment='Foreign key referencing physical device'),
        sa.Column('inspection_id', get_bigint_id(), nullable=True, comment='Associated active inspection session (nullable if idle)'),
        sa.Column('boot_id', sa.String(length=64), nullable=False, comment='Monotonic boot identifier from MCU startup'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='Client IP address'),
        sa.Column('connected_at', sa.DateTime(timezone=True), nullable=False, comment='UTC connection timestamp'),
        sa.Column('disconnected_at', sa.DateTime(timezone=True), nullable=True, comment='UTC disconnect timestamp'),
        sa.Column('disconnect_reason', sa.String(length=128), nullable=True, comment='Reason for session closure'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], name=op.f('fk_device_sessions_device_id_devices'), ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_device_sessions_inspection_id_inspections'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_device_sessions')),
        sa.UniqueConstraint('session_uuid', name=op.f('uq_device_sessions_session_uuid')),
    )
    op.create_index(op.f('ix_device_sessions_device_id'), 'device_sessions', ['device_id'], unique=False)
    op.create_index(op.f('ix_device_sessions_inspection_id'), 'device_sessions', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_device_sessions_session_uuid'), 'device_sessions', ['session_uuid'], unique=True)

    # 4. Create device_heartbeats table
    op.create_table(
        'device_heartbeats',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('session_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent device connection session'),
        sa.Column('device_id', sa.String(length=64), nullable=False, comment='Foreign key referencing physical device'),
        sa.Column('rssi_dbm', sa.Integer(), nullable=True, comment='WiFi received signal strength indication in dBm'),
        sa.Column('battery_millivolts', sa.Integer(), nullable=True, comment='DC battery potential in millivolts'),
        sa.Column('battery_percent', sa.Float(), nullable=True, comment='Computed battery percentage (0.0 to 100.0)'),
        sa.Column('free_heap_bytes', sa.Integer(), nullable=True, comment='Free heap memory bytes on MCU'),
        sa.Column('uptime_seconds', sa.Float(), nullable=True, comment='Reported device uptime in seconds'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, comment='UTC server receipt timestamp'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], name=op.f('fk_device_heartbeats_device_id_devices'), ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['session_id'], ['device_sessions.id'], name=op.f('fk_device_heartbeats_session_id_device_sessions'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_device_heartbeats')),
    )
    op.create_index(op.f('ix_device_heartbeats_device_id'), 'device_heartbeats', ['device_id'], unique=False)
    op.create_index(op.f('ix_device_heartbeats_recorded_at'), 'device_heartbeats', ['recorded_at'], unique=False)
    op.create_index(op.f('ix_device_heartbeats_session_id'), 'device_heartbeats', ['session_id'], unique=False)

    # 5. Create vehicle_status_events table
    op.create_table(
        'vehicle_status_events',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('inspection_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent inspection session'),
        sa.Column('session_id', get_bigint_id(), nullable=True, comment='Foreign key referencing active device session'),
        sa.Column('drive_mode', sa.String(length=32), nullable=False, server_default='manual', comment='Operational mode: manual, autonomous, reverse, estop'),
        sa.Column('left_motor_state', sa.String(length=32), nullable=False, server_default='idle', comment='Left motor actuation state: idle, forward, reverse, offline'),
        sa.Column('right_motor_state', sa.String(length=32), nullable=False, server_default='idle', comment='Right motor actuation state: idle, forward, reverse, offline'),
        sa.Column('emergency_stop', sa.Boolean(), nullable=False, server_default=sa.false(), comment='Emergency stop hardware status flag'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, comment='UTC timestamp of event recording'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_vehicle_status_events_inspection_id_inspections'), ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['session_id'], ['device_sessions.id'], name=op.f('fk_vehicle_status_events_session_id_device_sessions'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_vehicle_status_events')),
    )
    op.create_index(op.f('ix_vehicle_status_events_inspection_id'), 'vehicle_status_events', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_vehicle_status_events_recorded_at'), 'vehicle_status_events', ['recorded_at'], unique=False)
    op.create_index(op.f('ix_vehicle_status_events_session_id'), 'vehicle_status_events', ['session_id'], unique=False)

    # 6. Create encoder_samples table
    op.create_table(
        'encoder_samples',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('inspection_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent inspection session'),
        sa.Column('session_id', get_bigint_id(), nullable=True, comment='Foreign key referencing active device session'),
        sa.Column('sequence_number', get_bigint_id(), nullable=False, comment='Monotonic packet counter from microcontroller boot'),
        sa.Column('left_ticks', get_bigint_id(), nullable=False, comment='Raw cumulative pulse count from left motor encoder'),
        sa.Column('right_ticks', get_bigint_id(), nullable=False, comment='Raw cumulative pulse count from right motor encoder'),
        sa.Column('left_rpm', sa.Float(), nullable=True, comment='Rotational velocity of left wheel in RPM (derived/uncalibrated)'),
        sa.Column('right_rpm', sa.Float(), nullable=True, comment='Rotational velocity of right wheel in RPM (derived/uncalibrated)'),
        sa.Column('speed_mps', sa.Float(), nullable=True, comment='Forward linear speed in meters per second (derived)'),
        sa.Column('direction', sa.String(length=16), nullable=True, server_default='forward', comment='Physical drive direction: forward, reverse, stopped'),
        sa.Column('device_uptime_ms', get_bigint_id(), nullable=True, comment='Milliseconds since microcontroller boot'),
        sa.Column('device_timestamp', sa.DateTime(timezone=True), nullable=True, comment='Microcontroller hardware RTC timestamp if configured'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, comment='UTC server arrival timestamp'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_encoder_samples_inspection_id_inspections'), ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['session_id'], ['device_sessions.id'], name=op.f('fk_encoder_samples_session_id_device_sessions'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_encoder_samples')),
    )
    op.create_index(op.f('ix_encoder_samples_inspection_id'), 'encoder_samples', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_encoder_samples_recorded_at'), 'encoder_samples', ['recorded_at'], unique=False)
    op.create_index(op.f('ix_encoder_samples_session_id'), 'encoder_samples', ['session_id'], unique=False)

    # 7. Create imu_samples table
    op.create_table(
        'imu_samples',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('inspection_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent inspection session'),
        sa.Column('session_id', get_bigint_id(), nullable=True, comment='Foreign key referencing active device session'),
        sa.Column('sequence_number', get_bigint_id(), nullable=False, comment='Monotonic packet counter from microcontroller boot'),
        sa.Column('accel_x', sa.Float(), nullable=True, comment='Linear acceleration X-axis (raw LSB or calibrated m/s^2)'),
        sa.Column('accel_y', sa.Float(), nullable=True, comment='Linear acceleration Y-axis (raw LSB or calibrated m/s^2)'),
        sa.Column('accel_z', sa.Float(), nullable=True, comment='Linear acceleration Z-axis (raw LSB or calibrated m/s^2)'),
        sa.Column('gyro_x', sa.Float(), nullable=True, comment='Angular rate X-axis (raw LSB or calibrated deg/s)'),
        sa.Column('gyro_y', sa.Float(), nullable=True, comment='Angular rate Y-axis (raw LSB or calibrated deg/s)'),
        sa.Column('gyro_z', sa.Float(), nullable=True, comment='Angular rate Z-axis (raw LSB or calibrated deg/s)'),
        sa.Column('pitch_deg', sa.Float(), nullable=True, comment='Computed pitch inclination angle in degrees (derived)'),
        sa.Column('roll_deg', sa.Float(), nullable=True, comment='Computed roll inclination angle in degrees (derived)'),
        sa.Column('yaw_deg', sa.Float(), nullable=True, comment='Computed heading angle in degrees (derived)'),
        sa.Column('temperature_c', sa.Float(), nullable=True, comment='Internal sensor die temperature in Celsius'),
        sa.Column('sensor_units', sa.String(length=32), nullable=False, server_default='raw_lsb', comment='Physical units format: raw_lsb, si_mps2_degs'),
        sa.Column('device_uptime_ms', get_bigint_id(), nullable=True, comment='Milliseconds since microcontroller boot'),
        sa.Column('device_timestamp', sa.DateTime(timezone=True), nullable=True, comment='Microcontroller hardware RTC timestamp if configured'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, comment='UTC server arrival timestamp'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_imu_samples_inspection_id_inspections'), ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['session_id'], ['device_sessions.id'], name=op.f('fk_imu_samples_session_id_device_sessions'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_imu_samples')),
    )
    op.create_index(op.f('ix_imu_samples_inspection_id'), 'imu_samples', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_imu_samples_recorded_at'), 'imu_samples', ['recorded_at'], unique=False)
    op.create_index(op.f('ix_imu_samples_session_id'), 'imu_samples', ['session_id'], unique=False)

    # 8. Create camera_frames table
    op.create_table(
        'camera_frames',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('frame_id', sa.String(length=64), nullable=False, comment='Public unique frame UUID string matching frontend contract'),
        sa.Column('inspection_id', get_bigint_id(), nullable=False, comment='Foreign key referencing active inspection session'),
        sa.Column('camera_id', sa.String(length=64), nullable=False, server_default='esp32-cam-front', comment='Hardware camera identifier'),
        sa.Column('frame_sequence', get_bigint_id(), nullable=False, server_default='0', comment='Sequence counter from camera firmware stream'),
        sa.Column('frame_width', sa.Integer(), nullable=False, comment='Horizontal image dimension in pixels'),
        sa.Column('frame_height', sa.Integer(), nullable=False, comment='Vertical image dimension in pixels'),
        sa.Column('encoding', sa.String(length=16), nullable=False, server_default='jpeg', comment='Compression format: jpeg, png'),
        sa.Column('frame_bytes', sa.Integer(), nullable=False, comment='Raw frame payload size in bytes'),
        sa.Column('capture_timestamp', sa.DateTime(timezone=True), nullable=True, comment='Optical exposure timestamp if provided by camera clock'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, comment='Server UTC arrival timestamp'),
        sa.Column('processing_status', sa.String(length=32), nullable=False, server_default='pending', comment='Inference queue status: pending, inferred, dropped, error'),
        sa.Column('has_defect', sa.Boolean(), nullable=False, server_default=sa.false(), comment='Whether AI inference identified an anomaly in this frame'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_camera_frames_inspection_id_inspections'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_camera_frames')),
        sa.UniqueConstraint('frame_id', name=op.f('uq_camera_frames_frame_id')),
    )
    op.create_index(op.f('ix_camera_frames_capture_timestamp'), 'camera_frames', ['capture_timestamp'], unique=False)
    op.create_index(op.f('ix_camera_frames_frame_id'), 'camera_frames', ['frame_id'], unique=True)
    op.create_index(op.f('ix_camera_frames_inspection_id'), 'camera_frames', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_camera_frames_recorded_at'), 'camera_frames', ['recorded_at'], unique=False)

    # 9. Add model_version_id column to defects in batch mode
    with op.batch_alter_table('defects', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'model_version_id',
                get_bigint_id(),
                nullable=True,
                comment='Foreign key referencing deployed AI model version used for detection',
            )
        )
        batch_op.create_foreign_key(
            batch_op.f('fk_defects_model_version_id_ai_model_versions'),
            'ai_model_versions',
            ['model_version_id'],
            ['id'],
            ondelete='RESTRICT',
        )
        batch_op.create_index(batch_op.f('ix_defects_model_version_id'), ['model_version_id'], unique=False)

    # 10. Create evidence_media table
    op.create_table(
        'evidence_media',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('media_uuid', sa.String(length=64), nullable=False, comment='Public unique media UUID string'),
        sa.Column('defect_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent defect record'),
        sa.Column('file_path', sa.String(length=512), nullable=False, comment='Relative POSIX path from media root (e.g. crops/insp_1/def_42.jpg)'),
        sa.Column('mime_type', sa.String(length=64), nullable=False, server_default='image/jpeg', comment='MIME type string'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, comment='On-disk file size in bytes'),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False, comment='Cryptographic SHA-256 hash of evidence image file'),
        sa.Column('storage_backend', sa.String(length=32), nullable=False, server_default='LOCAL_FS', comment='Storage backend: LOCAL_FS, S3, MINIO'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='Record creation timestamp'),
        sa.ForeignKeyConstraint(['defect_id'], ['defects.id'], name=op.f('fk_evidence_media_defect_id_defects'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_evidence_media')),
        sa.UniqueConstraint('file_path', name=op.f('uq_evidence_media_file_path')),
        sa.UniqueConstraint('media_uuid', name=op.f('uq_evidence_media_media_uuid')),
    )
    op.create_index(op.f('ix_evidence_media_defect_id'), 'evidence_media', ['defect_id'], unique=False)
    op.create_index(op.f('ix_evidence_media_media_uuid'), 'evidence_media', ['media_uuid'], unique=True)

    # 11. Create localization_records table
    op.create_table(
        'localization_records',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('defect_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent defect record'),
        sa.Column('frame_id', sa.String(length=64), nullable=True, comment='Associated camera optical frame identifier'),
        sa.Column('frame_capture_timestamp', sa.DateTime(timezone=True), nullable=False, comment='Optical frame exposure timestamp from camera clock'),
        sa.Column('encoder_sample_timestamp', sa.DateTime(timezone=True), nullable=False, comment='Microcontroller timestamp of nearest correlated encoder sample'),
        sa.Column('temporal_delta_ms', sa.Float(), nullable=False, comment='Absolute difference between optical capture and encoder sample in milliseconds'),
        sa.Column('clock_sync_status', sa.String(length=32), nullable=False, server_default='UNVERIFIED_SYNC', comment='Synchronization state: UNVERIFIED_SYNC, SYNCHRONIZED, MANUAL_OVERRIDE'),
        sa.Column('sync_notes', sa.String(length=256), nullable=True, comment='Diagnostic explanation if synchronization is unverified or degraded'),
        sa.Column('left_encoder_ticks', get_bigint_id(), nullable=True, comment='Cumulative ticks of left motor encoder at correlated point'),
        sa.Column('right_encoder_ticks', get_bigint_id(), nullable=True, comment='Cumulative ticks of right motor encoder at correlated point'),
        sa.Column('computed_distance_meters', sa.Float(), nullable=True, comment='Calculated pipeline penetration distance (null if sync is unverified)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='Record creation timestamp'),
        sa.ForeignKeyConstraint(['defect_id'], ['defects.id'], name=op.f('fk_localization_records_defect_id_defects'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_localization_records')),
    )
    op.create_index(op.f('ix_localization_records_defect_id'), 'localization_records', ['defect_id'], unique=False)
    op.create_index(op.f('ix_localization_records_frame_id'), 'localization_records', ['frame_id'], unique=False)

    # 12. Create inspection_events table
    op.create_table(
        'inspection_events',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('inspection_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent inspection session'),
        sa.Column('event_type', sa.String(length=64), nullable=False, comment='Event identifier: STATE_CHANGE, OBSTACLE_ENCOUNTERED, NOTE_LOGGED'),
        sa.Column('payload', sa.JSON(), nullable=True, comment='Contextual metadata snapshot for the event'),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False, comment='UTC timestamp of event occurrence'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_inspection_events_inspection_id_inspections'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_inspection_events')),
    )
    op.create_index(op.f('ix_inspection_events_event_type'), 'inspection_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_inspection_events_inspection_id'), 'inspection_events', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_inspection_events_occurred_at'), 'inspection_events', ['occurred_at'], unique=False)

    # 13. Create inspection_summaries table
    op.create_table(
        'inspection_summaries',
        sa.Column('inspection_id', get_bigint_id(), nullable=False, comment='Primary key and foreign key referencing parent inspection session'),
        sa.Column('total_defects_count', sa.Integer(), nullable=False, server_default='0', comment='Total verified defect count'),
        sa.Column('deformation_count', sa.Integer(), nullable=False, server_default='0', comment='Count of Deformation anomalies'),
        sa.Column('misalignment_count', sa.Integer(), nullable=False, server_default='0', comment='Count of Misalignment anomalies'),
        sa.Column('obstacle_count', sa.Integer(), nullable=False, server_default='0', comment='Count of Obstacle anomalies'),
        sa.Column('rupture_count', sa.Integer(), nullable=False, server_default='0', comment='Count of Rupture anomalies'),
        sa.Column('overall_pipe_grade', sa.String(length=16), nullable=False, server_default='PENDING', comment='Pipe compliance grade: A, B, C, D, FAIL, PENDING'),
        sa.Column('total_runtime_seconds', sa.Integer(), nullable=False, server_default='0', comment='Elapsed active inspection duration in seconds'),
        sa.Column('compiled_at', sa.DateTime(timezone=True), nullable=False, comment='UTC timestamp when summary snapshot was computed'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_inspection_summaries_inspection_id_inspections'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('inspection_id', name=op.f('pk_inspection_summaries')),
    )

    # 14. Create inspection_reports table
    op.create_table(
        'inspection_reports',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('report_id', sa.String(length=64), nullable=False, comment='Public unique report identifier (e.g. REP-20261030-001)'),
        sa.Column('inspection_id', get_bigint_id(), nullable=False, comment='Foreign key referencing parent inspection session'),
        sa.Column('report_type', sa.String(length=32), nullable=False, server_default='FULL_COMPLIANCE', comment='Report classification: EXECUTIVE_SUMMARY, FULL_COMPLIANCE, MAINTENANCE_WORKORDER'),
        sa.Column('report_format', sa.String(length=16), nullable=False, server_default='PDF', comment='Document format: PDF, JSON, CSV'),
        sa.Column('file_path', sa.String(length=512), nullable=False, comment='Relative POSIX path to generated report document on disk'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, comment='On-disk report file size in bytes'),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=False, comment='Cryptographic SHA-256 hash of generated report file'),
        sa.Column('overall_rating', sa.String(length=8), nullable=False, server_default='B', comment='Pipeline structural condition grade: A, B, C, D, FAIL'),
        sa.Column('generated_by', sa.String(length=64), nullable=False, comment='Operator badge or user identifier who generated the report'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False, comment='UTC timestamp when report compilation finished'),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name=op.f('fk_inspection_reports_inspection_id_inspections'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_inspection_reports')),
        sa.UniqueConstraint('file_path', name=op.f('uq_inspection_reports_file_path')),
        sa.UniqueConstraint('report_id', name=op.f('uq_inspection_reports_report_id')),
    )
    op.create_index(op.f('ix_inspection_reports_inspection_id'), 'inspection_reports', ['inspection_id'], unique=False)
    op.create_index(op.f('ix_inspection_reports_report_id'), 'inspection_reports', ['report_id'], unique=True)

    # 15. Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', get_bigint_id(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(length=64), nullable=False, comment='Affected domain entity: INSPECTION, DEFECT, MODEL_CONFIG, SYSTEM_SETTING'),
        sa.Column('entity_id', sa.String(length=64), nullable=False, comment='Surrogate or public ID of affected record'),
        sa.Column('action', sa.String(length=32), nullable=False, comment='Action performed: CREATE, UPDATE, ARCHIVE, DELETE, REVIEW_OVERRIDE'),
        sa.Column('performed_by', sa.String(length=64), nullable=False, comment='Authenticated operator badge, username, or client identifier'),
        sa.Column('before_state', sa.JSON(), nullable=True, comment='Prior entity state snapshot serialized as JSON'),
        sa.Column('after_state', sa.JSON(), nullable=True, comment='Updated entity state snapshot serialized as JSON'),
        sa.Column('client_ip', sa.String(length=45), nullable=True, comment='Network client IP address issuing the request'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, comment='UTC timestamp of audit entry creation'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_events')),
    )
    op.create_index(op.f('ix_audit_events_action'), 'audit_events', ['action'], unique=False)
    op.create_index(op.f('ix_audit_events_entity_id'), 'audit_events', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_events_entity_type'), 'audit_events', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_events_recorded_at'), 'audit_events', ['recorded_at'], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index(op.f('ix_audit_events_recorded_at'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_entity_type'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_entity_id'), table_name='audit_events')
    op.drop_index(op.f('ix_audit_events_action'), table_name='audit_events')
    op.drop_table('audit_events')

    op.drop_index(op.f('ix_inspection_reports_report_id'), table_name='inspection_reports')
    op.drop_index(op.f('ix_inspection_reports_inspection_id'), table_name='inspection_reports')
    op.drop_table('inspection_reports')

    op.drop_table('inspection_summaries')

    op.drop_index(op.f('ix_inspection_events_occurred_at'), table_name='inspection_events')
    op.drop_index(op.f('ix_inspection_events_inspection_id'), table_name='inspection_events')
    op.drop_index(op.f('ix_inspection_events_event_type'), table_name='inspection_events')
    op.drop_table('inspection_events')

    op.drop_index(op.f('ix_localization_records_frame_id'), table_name='localization_records')
    op.drop_index(op.f('ix_localization_records_defect_id'), table_name='localization_records')
    op.drop_table('localization_records')

    op.drop_index(op.f('ix_evidence_media_media_uuid'), table_name='evidence_media')
    op.drop_index(op.f('ix_evidence_media_defect_id'), table_name='evidence_media')
    op.drop_table('evidence_media')

    with op.batch_alter_table('defects', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_defects_model_version_id'))
        batch_op.drop_constraint(batch_op.f('fk_defects_model_version_id_ai_model_versions'), type_='foreignkey')
        batch_op.drop_column('model_version_id')

    op.drop_index(op.f('ix_camera_frames_recorded_at'), table_name='camera_frames')
    op.drop_index(op.f('ix_camera_frames_inspection_id'), table_name='camera_frames')
    op.drop_index(op.f('ix_camera_frames_frame_id'), table_name='camera_frames')
    op.drop_index(op.f('ix_camera_frames_capture_timestamp'), table_name='camera_frames')
    op.drop_table('camera_frames')

    op.drop_index(op.f('ix_imu_samples_session_id'), table_name='imu_samples')
    op.drop_index(op.f('ix_imu_samples_recorded_at'), table_name='imu_samples')
    op.drop_index(op.f('ix_imu_samples_inspection_id'), table_name='imu_samples')
    op.drop_table('imu_samples')

    op.drop_index(op.f('ix_encoder_samples_session_id'), table_name='encoder_samples')
    op.drop_index(op.f('ix_encoder_samples_recorded_at'), table_name='encoder_samples')
    op.drop_index(op.f('ix_encoder_samples_inspection_id'), table_name='encoder_samples')
    op.drop_table('encoder_samples')

    op.drop_index(op.f('ix_vehicle_status_events_session_id'), table_name='vehicle_status_events')
    op.drop_index(op.f('ix_vehicle_status_events_recorded_at'), table_name='vehicle_status_events')
    op.drop_index(op.f('ix_vehicle_status_events_inspection_id'), table_name='vehicle_status_events')
    op.drop_table('vehicle_status_events')

    op.drop_index(op.f('ix_device_heartbeats_session_id'), table_name='device_heartbeats')
    op.drop_index(op.f('ix_device_heartbeats_recorded_at'), table_name='device_heartbeats')
    op.drop_index(op.f('ix_device_heartbeats_device_id'), table_name='device_heartbeats')
    op.drop_table('device_heartbeats')

    op.drop_index(op.f('ix_device_sessions_session_uuid'), table_name='device_sessions')
    op.drop_index(op.f('ix_device_sessions_inspection_id'), table_name='device_sessions')
    op.drop_index(op.f('ix_device_sessions_device_id'), table_name='device_sessions')
    op.drop_table('device_sessions')

    op.drop_index(op.f('ix_ai_model_versions_model_version'), table_name='ai_model_versions')
    op.drop_table('ai_model_versions')

    op.drop_table('devices')

