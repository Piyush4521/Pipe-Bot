# PipeBot Database Security Architecture and Access Controls

## 1. Security Architecture Overview

The PipeBot persistence security architecture implements defense-in-depth principles across data access, network ingestion, cryptographic integrity, and operational accountability.

```
+-----------------------------------------------------------------------------+
|                          NETWORK INGESTION SECURITY                         |
|     Bearer Token Authentication (X-Device-Token), Rate Limiting, Input      |
|     Sanitization, Finite Float Validation, Strict Payload Bounds            |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                         APPLICATION DATA ACCESS LAYER                       |
|     SQLAlchemy 2.0 Parameterized Statements (Zero String Concatenation)      |
|     Path Traversal Defense, Strict Enum Binding, Restrictive Deletions      |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                          CRYPTOGRAPHIC INTEGRITY                            |
|     SHA-256 Checksums for Frame Crops, Reports, and AI Model Artifacts      |
|     PRAGMA integrity_check, Read-Only Backup Verification Modes             |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                           AUDIT AND ACCOUNTABILITY                          |
|     Append-Only Audit Events Registry, Non-Repudiation, Client IP Logging   |
+-----------------------------------------------------------------------------+
```

---

## 2. SQL Injection Prevention

SQL injection vulnerabilities are completely eliminated by design through the exclusive use of SQLAlchemy 2.0 Core and ORM parameterized query expressions:
- Zero Raw String Interpolation: SQL statements never concatenate user-supplied input into queries.
- Type-Safe Statements: All queries use `select()`, `where()`, and `insert()` constructs where parameters are bound as typed DBAPI positional parameters.
- Schema Validation: Pydantic schemas validate all incoming request bodies before they reach the repository layer, rejecting non-finite floats (`NaN`, `Infinity`), oversized strings, and invalid enum values.

---

## 3. Microcontroller Telemetry and Camera Ingestion Authentication

Physical microcontrollers (`ESP32-WROOM-32` and `ESP32-CAM`) transmit telemetry and optical frames over local WiFi/Ethernet networks.
- Token Enforcement: The backend checks the `X-Device-Token` header against `DEVICE_INGEST_TOKEN` in `app/core/config.py`.
- Unauthorized Rejection: Requests lacking a valid token are rejected immediately with `401 Unauthorized` before interacting with the database.
- Input Hardening: The ingestion pipeline validates that rotary encoder ticks are non-negative, IMU accelerations are within physical gravitational bounds, and frame byte sizes do not exceed configured limits (1 MB maximum).

---

## 4. Media Storage and Path Traversal Safeguards

Raw video streams and defect snapshot images are stored on disk, never as database BLOBs. The database persists only relative POSIX file paths.

Path Traversal Protections:
- Canonical Relative Paths: File paths are strictly formatted as `crops/insp_<id>/def_<id>.jpg`.
- Path Sanitization: The media retrieval endpoint resolves paths against the canonical `MEDIA_STORAGE_DIR` and rejects any path containing parent directory traversal tokens (`..`) or absolute system drive roots.
- MIME Validation: Evidence uploads validate image magic bytes (e.g. `\xFF\xD8\xFF` for JPEG) to prevent malicious executable file uploads.

---

## 5. Cryptographic Verification and Provenance

Every persisted file asset is cryptographically bound to its database metadata:
- Defect Evidence Media: `evidence_media.checksum_sha256` stores the hexadecimal SHA-256 hash computed at file creation.
- AI Model Weights: `ai_model_versions.artifact_checksum_sha256` ensures deployed neural network weights match approved training artifacts.
- Inspection Reports: `inspection_reports.checksum_sha256` prevents tampering with compiled engineering compliance certificates.

---

## 6. Non-Repudiation Security Audit Logging

All administrative modifications, defect review status updates, and session lifecycle transitions are permanently recorded in the append-only `audit_events` table:

```python
class AuditEvent(Base):
    id: Mapped[int]                    # Surrogate key
    entity_type: Mapped[str]           # INSPECTION, DEFECT, MODEL_CONFIG
    entity_id: Mapped[str]             # Public identifier of affected record
    action: Mapped[str]                # CREATE, UPDATE, ARCHIVE, REVIEW_OVERRIDE
    performed_by: Mapped[str]          # Operator badge, username, or client token
    before_state: Mapped[dict]         # JSON snapshot of record prior to mutation
    after_state: Mapped[dict]          # JSON snapshot of record after mutation
    client_ip: Mapped[str]             # Network IP address of request issuer
    recorded_at: Mapped[datetime]      # Immutable UTC timestamp
```

Audit Safeguards:
- Decoupled from Foreign Keys: The audit table intentionally omits foreign key constraints to ensure audit entries persist even if referenced entities are archived.
- No Mutation APIs: The `AuditRepository` provides only `log_event()`, `get_event_by_id()`, and `list_events_by_entity()` methods. No update or deletion operations exist.

---

## 7. Filesystem and Operating System Permissions

In deployment environments:
- Database File Permissions: The SQLite database file (`backend/data/pipebot.db`) must be owned by the backend service account with `chmod 600` permissions.
- Secret Management: Application secrets (`DEVICE_INGEST_TOKEN`, `DATABASE_URL`) are loaded from `.env` files which are excluded from Git version control.
- Test Database Isolation: All automated tests execute strictly in temporary memory or isolated `tmp_path` directories with zero access to live database files.

