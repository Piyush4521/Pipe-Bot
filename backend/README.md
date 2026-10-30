# PipeBot Backend: Computer Vision, Telemetry Ingestion and Pipeline Inspection

> **Current Status**: Stage 5 of 5 Completed (Backend Integration QA, Security, Performance, Documentation and GitHub Release).  
> The backend provides a modular FastAPI architecture with SQLite database persistence, Alembic migrations, complete inspection lifecycle management, defect anomaly tracking with canonical taxonomy (Deformation, Misalignment, Obstacle, Rupture), thread-safe in-memory telemetry ingestion, duplex operator WebSocket communication, ESP32-CAM MJPEG stream parsing, defensive OpenCV frame decoding, drop-oldest bounded queue backpressure, pluggable AI inference abstraction, temporal-spatial odometry localization safety policy, defect evidence snapshot cropping and media serving, frontend contract compatibility aliases, and a 99-test automated pytest suite.

---

## 1. Architecture Overview

The backend follows a layered architecture separating database models, repositories, business services, camera ingestion, computer vision, spatial localization, telemetry caching, WebSocket managers, and API endpoints:

```text
D:\PipeBot\backend
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py        # Health, readiness, and database probe endpoints
│   │       │   ├── system.py        # Subsystem status contract endpoint
│   │       │   ├── inspections.py   # Inspection session lifecycle and query endpoints
│   │       │   ├── defects.py       # Defect detection recording, review, and query endpoints
│   │       │   ├── telemetry.py     # High-frequency telemetry ingestion and query endpoints
│   │       │   ├── websocket.py     # Duplex WebSocket streaming endpoint
│   │       │   ├── camera.py        # Camera status, start, stop, and frame ingestion endpoints
│   │       │   ├── vision.py        # AI vision subsystem status endpoint
│   │       │   └── media.py         # Path-traversal safe defect evidence media server
│   │       └── router.py            # API v1 consolidated router
│   ├── camera/
│   │   ├── camera_state.py          # Camera status singleton, frame counters, rolling FPS
│   │   ├── frame_validator.py       # OpenCV BGR validation, size limits, byte decoding
│   │   ├── frame_reader.py          # Asynchronous MJPEG stream parser with drop-oldest queue
│   │   └── camera_client.py         # Camera background worker lifecycle supervision
│   ├── core/
│   │   ├── config.py                # Pydantic BaseSettings configuration singleton
│   │   ├── exceptions.py            # Domain exceptions (NotFound, Conflict, StateTransition)
│   │   ├── lifespan.py              # Application startup, background workers, and shutdown
│   │   └── logging.py               # Rotating file and console logging configuration
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy DeclarativeBase and TimestampMixin
│   │   ├── init_db.py               # Database connectivity verification and initialization
│   │   └── session.py               # Engine creation, PRAGMA foreign keys, and sessionmaker
│   ├── localization/
│   │   └── timestamp_associator.py  # Spatial odometry correlation and non-extrapolation engine
│   ├── models/
│   │   ├── __init__.py              # Central SQLAlchemy model exports for Alembic
│   │   ├── inspection.py            # Inspection session model and status enum
│   │   └── defect.py                # Defect detection model, defect class, and review enum
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── inspection_repository.py # Inspection persistence, filtering, and queries
│   │   └── defect_repository.py     # Defect persistence, soft-delete, and queries
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── health.py                # Health and system status schemas
│   │   ├── inspection.py            # Inspection request, update, and response schemas
│   │   ├── defect.py                # Defect request, review update, and bounding box schemas
│   │   ├── telemetry.py             # Telemetry ingest, response, and WebSocket envelope schemas
│   │   ├── frame.py                 # Camera status and frame metadata schemas
│   │   └── detection.py             # Inference result, bounding box, and vision status schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── health_service.py        # Health, ping latency, and dynamic subsystem link evaluation
│   │   ├── inspection_service.py    # Inspection session business logic and state transitions
│   │   ├── defect_service.py        # Defect creation, review workflow, and soft-delete
│   │   ├── telemetry_state.py       # In-memory telemetry cache, ring buffer, reboot detection
│   │   ├── websocket_manager.py     # Operator WebSocket registry, limit enforcement, broadcasts
│   │   └── frame_processing_service.py # Vision pipeline, evidence crop, DB persistence
│   ├── vision/
│   │   ├── interfaces.py            # InferenceProvider abstract base class
│   │   ├── model_registry.py        # Factory and test override hooks for vision providers
│   │   └── providers/
│   │       ├── unavailable_provider.py # Default safe fallback provider
│   │       └── ultralytics_provider.py   # YOLO provider with CUDA RTX 2050 auto-detection
│   └── main.py                      # FastAPI application factory, CORS, exception handlers
├── data/
│   ├── media/                       # Cropped defect evidence images (gitignored)
│   └── pipebot.db                   # SQLite database storage (gitignored)
├── docs/
│   ├── inspection-api.md            # Detailed inspection and defect API endpoint reference
│   ├── api-contracts.md             # Frontend/backend contract compatibility audit
│   ├── telemetry-api.md             # Detailed telemetry ingestion and status query reference
│   ├── websocket-protocol.md        # Duplex operator WebSocket streaming protocol
│   ├── device-integration.md        # ESP32-WROOM and ESP32-CAM firmware integration guide
│   ├── camera-ingestion.md          # Camera MJPEG stream ingestion and validation reference
│   ├── vision-integration.md        # AI vision inference, provider architecture, evidence reference
│   └── localization.md              # Spatial odometry correlation and physical constraints reference
├── logs/
│   └── pipebot.log                  # Rotating application logs (gitignored, 10MB x 5 backups)
├── migrations/
│   ├── versions/                    # Alembic migration script history
│   │   ├── 88f24fc2264d_create_inspection_and_defect_tables.py
│   │   └── d4d255efae0c_enforce_restrictive_fk_and_archival.py
│   ├── env.py                       # Alembic environment configured for SQLite batch mode
│   ├── script.py.mako               # Migration template
│   └── alembic.ini                  # Alembic CLI configuration
├── tests/
│   ├── conftest.py                  # Pytest fixtures and isolated SQLite test database
│   ├── test_health.py               # Test suite for health, readiness, and system status
│   ├── test_inspections.py          # Test suite for inspection CRUD and lifecycle states
│   ├── test_defects.py              # Test suite for defect recording, review, and filtering
│   ├── test_integrity.py            # Test suite for foreign keys, constraints, and rollbacks
│   ├── test_timestamps.py           # Test suite for UTC normalization and timestamp separation
│   ├── test_telemetry.py            # Test suite for telemetry ingestion, sequences, and timeouts
│   ├── test_websocket.py            # Test suite for WebSocket connections, envelopes, and broadcasts
│   ├── test_frame_validation.py     # Test suite for OpenCV decoding, size limits, queue drops
│   ├── test_camera.py               # Test suite for camera endpoints, lifecycle, and stale state
│   ├── test_vision.py               # Test suite for inference providers, thresholds, bounding boxes
│   ├── test_localization.py         # Test suite for odometry correlation and non-extrapolation
│   └── test_vision_integration.py   # Test suite for evidence cropping, media serving, and DB defect creation
├── .env                             # Active environment configuration
├── .env.example                     # Environment template
├── .gitignore                       # Python, virtualenv, and media ignore rules
├── pyproject.toml                   # Project metadata and pytest configuration
├── requirements.txt                 # Pinned Python package dependencies
└── README.md                        # Backend documentation
```

---

## 2. Prerequisites and Python Version

- **Python Version**: Python 3.10.x (verified on Python 3.10.12 in WSL Ubuntu 22.04).
- **Environment Isolation**: Dedicated virtual environment located at `backend/.venv`.
- **Operating System**: Linux / WSL (Ubuntu) or Windows PowerShell with Python 3.10.
- **Hardware Acceleration**: Optional NVIDIA GeForce RTX 2050 Mobile GPU with CUDA support for YOLO inference.

---

## 3. Environment Setup and Installation

All setup steps must be executed within `D:\PipeBot\backend`:

### 3.1. Virtual Environment Setup (WSL / Linux)

```bash
cd /mnt/d/PipeBot/backend

# Create virtual environment
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install pinned dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2. Virtual Environment Setup (Windows PowerShell)

```powershell
cd D:\PipeBot\backend

# Create virtual environment
py -3.10 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Environment Configuration (.env)

The application loads configuration via Pydantic Settings from `backend/.env`. A template is provided in `backend/.env.example`.

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `PipeBot Backend` | Name of the FastAPI application |
| `APP_VERSION` | `0.1.0` | Semantic version string |
| `APP_ENV` | `development` | Deployment environment (`development`, `testing`, `production`) |
| `DEBUG` | `true` | Enable or disable debug mode |
| `API_V1_PREFIX` | `/api/v1` | Root path prefix for v1 API endpoints |
| `DATABASE_URL` | `sqlite:///./data/pipebot.db` | SQLAlchemy SQLite database connection string |
| `CAMERA_ID` | `esp32_cam_01` | Default identifier for optical camera |
| `CAMERA_STREAM_URL` | `""` | Stream URL for ESP32-CAM MJPEG endpoint |
| `CAMERA_MAX_FRAME_BYTES` | `1048576` | Maximum frame size limit (1 MB) |
| `CAMERA_QUEUE_SIZE` | `10` | Bounded memory queue capacity (drop-oldest backpressure) |
| `MEDIA_STORAGE_DIR` | `data/media` | Directory for defect crop evidence snapshots |
| `INFERENCE_ENABLED` | `false` | Master switch for automated YOLO inference |
| `INFERENCE_PROVIDER` | `unavailable` | Inference provider (`unavailable` or `ultralytics`) |
| `INFERENCE_CONFIDENCE_THRESHOLD` | `0.5` | Minimum statistical confidence score |
| `INFERENCE_DEVICE` | `cpu` | Inference target device (`cpu` or `cuda`) |

---

## 5. Running the Development Server

Execute from the backend directory with the virtual environment activated:

```bash
# WSL / Linux
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

```powershell
# Windows PowerShell
cd D:\PipeBot\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Interactive API Documentation

When the server is running, interactive documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

---

## 6. Available Endpoints (Stage 4)

### System and Health Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Application root info, version, and links | `200 OK` |
| `GET` | `/api/v1/health` | Service health status and timestamp | `200 OK` |
| `GET` | `/api/v1/health/ready` | Readiness probe verifying database connectivity | `200 OK` / `503` |
| `GET` | `/api/v1/health/database` | Database connectivity status and ping latency (ms) | `200 OK` / `503` |
| `GET` | `/api/v1/system/status` | Dynamic subsystem status matrix matching frontend contract | `200 OK` |

### Camera and Vision Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/camera/status` | Query camera connection, rolling FPS, and dropped frames | `200 OK` |
| `POST` | `/api/v1/camera/start` | Start asynchronous camera stream reader worker | `200 OK` |
| `POST` | `/api/v1/camera/stop` | Stop camera stream reader and clean up resources | `200 OK` |
| `POST` | `/api/v1/camera/frame` | Ingest single optical frame via multipart form upload | `200 OK` / `422` |
| `GET` | `/api/v1/vision/status` | Query AI vision provider availability, device, and classes | `200 OK` |
| `GET` | `/api/v1/media/{filename}` | Retrieve cropped defect evidence image with path protection | `200 OK` / `404` |

### Telemetry and Device Ingestion Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/telemetry/encoder` | Ingest wheel encoder odometry from ESP32 | `200 OK` / `401` / `422` |
| `POST` | `/api/v1/telemetry/imu` | Ingest MPU6050 6-axis inertial motion and angles | `200 OK` / `401` / `422` |
| `POST` | `/api/v1/telemetry/vehicle/status` | Ingest vehicle power, motor current, and e-stop state | `200 OK` / `401` / `422` |
| `POST` | `/api/v1/telemetry/heartbeat` | Ingest periodic device diagnostic heartbeat | `200 OK` / `401` / `422` |
| `GET` | `/api/v1/telemetry/latest` | Retrieve latest consolidated telemetry snapshot | `200 OK` |
| `GET` | `/api/v1/telemetry/status` | Retrieve per-device connection diagnostics | `200 OK` |
| `GET` | `/api/v1/telemetry/inspection/{id}` | Query in-memory inspection telemetry log | `200 OK` |

### WebSocket Telemetry Streaming Routes
| Protocol | Endpoint | Description | Payload Format |
| :--- | :--- | :--- | :--- |
| `WS` | `/api/v1/ws/telemetry` | Standard API v1 duplex operator stream | Typed Envelope |
| `WS` | `/ws/telemetry` | Frontend contract compatibility alias | Typed Envelope |
| `WS` | `/ws` | Vite configuration default alias | Typed Envelope |

### Inspection Management Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/inspections` | Create new inspection session (status: `created`) | `201 Created` |
| `GET` | `/api/v1/inspections` | List paginated inspections (status filter, limit, offset) | `200 OK` |
| `GET` | `/api/v1/inspections/{id}` | Retrieve single inspection by public ID or database ID | `200 OK` / `404` |
| `PATCH` | `/api/v1/inspections/{id}` | Update mutable inspection metadata | `200 OK` / `404` |
| `POST` | `/api/v1/inspections/{id}/start` | Transition status from `created` to `in_progress` | `200 OK` / `409` |
| `POST` | `/api/v1/inspections/{id}/pause` | Transition status from `in_progress` to `paused` | `200 OK` / `409` |
| `POST` | `/api/v1/inspections/{id}/complete` | Complete session and record final odometry distance | `200 OK` / `409` |
| `POST` | `/api/v1/inspections/{id}/cancel` | Cancel session before completion | `200 OK` / `409` |
| `POST` | `/api/v1/inspections/{id}/archive` | Safely archive session without destroying defect evidence | `200 OK` / `404` |
| `DELETE` | `/api/v1/inspections/{id}` | Reject permanent deletion request to preserve audit history | `409 Conflict` |
| `GET` | `/api/v1/inspections/{id}/defects` | List paginated defects for an inspection session | `200 OK` / `404` |

### Defect Management Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/defects` | Record new anomaly linked to an existing inspection | `201 Created` / `404` |
| `GET` | `/api/v1/defects` | List paginated defects (class, review status, search) | `200 OK` |
| `GET` | `/api/v1/defects/{id}` | Retrieve single defect detection | `200 OK` / `404` |
| `PATCH` | `/api/v1/defects/{id}/review` | Update review status (`pending`, `confirmed`, `rejected`) | `200 OK` / `404` |
| `DELETE` | `/api/v1/defects/{id}` | Soft-delete defect to preserve regulatory compliance logs | `200 OK` / `404` |

---

## 7. Automated Testing

The automated test suite runs via `pytest` with an isolated SQLite test database (`tests/test_pipebot.db`).

```bash
# WSL / Linux
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
pytest -v
```

```powershell
# Windows PowerShell
cd D:\PipeBot\backend
.\.venv\Scripts\Activate.ps1
pytest -v
```

### Verified Test Suite (99 Tests Passing Across 13 Modules)

1. **Health Suite** (`tests/test_health.py`): 7 tests covering root, health, readiness, database health, dynamic system status, database failure handling (503), and 404 routes.
2. **Inspection Suite** (`tests/test_inspections.py`): 12 tests covering creation, explicit IDs, duplicate conflict (409), validation failure (422), dual-ID lookup, 404 handling, pagination, status filtering, metadata updates, complete lifecycle (`created` -> `in_progress` -> `paused` -> `completed`), cancellation, and invalid state transition rejection (409).
3. **Defect Suite** (`tests/test_defects.py`): 11 tests covering defect creation, missing inspection 404, confidence bounds validation [0.0, 1.0], invalid class rejection, BoundingBox2D conversion, dual-ID lookup, 404 handling, multi-criteria filtering, review status updating with alias normalization (`verified` -> `confirmed`, `dismissed` -> `rejected`), soft-delete, and inspection defect count synchronization.
4. **Database Integrity Suite** (`tests/test_integrity.py`): 8 tests covering restrictive foreign key prevention of destructive deletion, service-level permanent deletion prohibition, defect evidence survival across inspection archival, retrievability of archived inspections via API, rejection of DELETE requests with 409 Conflict, unique constraints on `inspection_id` and `defect_id`, and transaction rollbacks.
5. **Timestamp Suite** (`tests/test_timestamps.py`): 6 tests covering exact UTC normalization of offset-aware timestamps, naive timestamp interpretation policy, SQLite `UtcDateTime` persistence with guaranteed `tzinfo=timezone.utc`, API ISO 8601 `Z` suffix serialization, `frameCaptureTimestamp` alias support, and strict separation between capture, inference, and record creation timestamps.
6. **Telemetry Ingestion Suite** (`tests/test_telemetry.py`): 12 tests covering baseline disconnected state without fabricated data, encoder ingestion, IMU ingestion, vehicle status ingestion, heartbeat ingestion, rejection of non-finite numbers (NaN, Inf), monotonic sequence tracking, duplicate packet handling, device reboot detection via changed bootId, connection timeout transitions (connected -> stale -> disconnected), optional token authentication (`DEVICE_INGEST_TOKEN`), and inspection log query.
7. **WebSocket Streaming Suite** (`tests/test_websocket.py`): 6 tests covering operator connection, initial snapshot delivery (4 envelopes), route compatibility aliases (`/api/v1/ws/telemetry`, `/ws/telemetry`, `/ws`), ping/pong keepalives, live broadcast on telemetry ingestion, capacity limit enforcement (`WS_MAX_CONNECTIONS`), and clean disconnect handling.
8. **Frame Validation Suite** (`tests/test_frame_validation.py`): 6 tests covering valid JPEG memory decoding to BGR NumPy array, empty frame byte rejection, malformed byte rejection, oversized payload byte rejection (>1MB), oversized spatial dimension rejection (>1920x1080), and bounded queue drop-oldest backpressure accounting.
9. **Camera Lifecycle Suite** (`tests/test_camera.py`): 7 tests covering baseline disconnected state, start with empty URL staying disconnected, stop endpoint, stale detection timeout evaluation, single frame multipart ingestion, empty upload rejection, and client background worker start/stop lifecycle.
10. **Vision Subsystem Suite** (`tests/test_vision.py`): 6 tests covering `UnavailableInferenceProvider` safe fallback behavior, `UltralyticsInferenceProvider` missing weights clean handling, `/api/v1/vision/status` endpoint structure, `BoundingBoxSchema` bounds validation, `InferenceResult` confidence bounds [0.0, 1.0], and `ModelRegistry` factory fallback.
11. **Localization Suite** (`tests/test_localization.py`): 5 tests covering missing capture timestamp remaining unavailable, localization disabled by default without verified hardware clock sync, clock unsynchronized without matching encoder telemetry, successful odometry correlation within timestamp window, and separation between capture and inference timestamps.
12. **Vision Integration Suite** (`tests/test_vision_integration.py`): 4 tests covering defect evidence image cropping (10% margin) and media retrieval, path traversal protection blocking malicious filenames, automated database defect record creation during active inspection, and dynamic system status reflection of camera stream state.
13. **Release QA Suite** (`tests/test_release_qa.py`): 9 tests covering canonical defect taxonomy (Deformation, Misalignment, Obstacle, Rupture) with 0-indexed integer IDs, case-insensitive class parsing, frontend compatibility aliases (`/status`, `/api/v1/status`, `/health`, `/api/v1/defects/inspection/{id}`), camera frame content-type checking, oversized payload rejection, token authentication, and media extension validation.

---

## 8. Stage 5 Scope and Final Status

### Implemented and Verified in Stage 5
- Full backend audit with all 99 tests passing in Python 3.10 virtual environment.
- Canonical defect taxonomy enforced: `Deformation` (0), `Misalignment` (1), `Obstacle` (2), `Rupture` (3).
- Spatial odometry localization safety policy: physical localization strictly suspended until embedded hardware shutter clock synchronization is validated.
- Defensive camera frame security: payload size limits, content-type verification, and optional token authentication.
- Media serving security: extension filtering (`.jpg`, `.jpeg`) and directory traversal blocking.
- Single-process operator WebSocket manager with connection limits, typed envelope schemas, and graceful shutdown.
- Frontend contract compatibility routes: `/status`, `/health`, and `/api/v1/defects/inspection/{id}`.
- Comprehensive release checklist in `docs/backend-release-checklist.md`.
- Exactly 10 logical commits prepared for Git release.

### Deferred to Future Dedicated Engineering Phases
- **AI Training Phase**: Dataset conversion, model training, and YOLO weight export.
- **Embedded Firmware Phase**: ESP32-WROOM-32 motor PWM and ESP32-CAM hardware shutter clock sync.
- **Database Engineering Phase**: Migration to PostgreSQL and Redis pub/sub for horizontal scaling.
