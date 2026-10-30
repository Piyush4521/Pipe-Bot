# PipeBot: AI-Powered Robotic PVC Pipeline Inspection System

[![Backend Test Suite](https://img.shields.io/badge/Backend%20Pytest-120%20Passed-brightgreen)](file:///D:/PipeBot/backend)
[![Frontend Test Suite](https://img.shields.io/badge/Frontend%20Tests-16%20Passed-brightgreen)](file:///D:/PipeBot/scripts/verify-frontend.mjs)
[![TypeScript Strict](https://img.shields.io/badge/TypeScript-Strict%20Mode-blue)](file:///D:/PipeBot/tsconfig.json)
[![Database](https://img.shields.io/badge/Database-SQLite%20(Alembic%20Head)-orange)](file:///D:/PipeBot/backend/data/pipebot.db)
[![Target AI Model](https://img.shields.io/badge/AI%20Model-YOLOv8%20(4%20Classes)-purple)](file:///D:/PipeBot/ai-model)

> **Current Milestone**: Architecture Refinement, Codebase Cleanup, UI/UX Enhancements & Database Verification Completed.  
> PipeBot combines a production-grade React/TypeScript operator dashboard with a modular Python FastAPI backend service, SQLite/PostgreSQL persistence, real-time WebSocket telemetry broadcasting, ESP32-CAM video stream consumption, and an Ultralytics YOLOv8 defect detection architecture.

---

## 1. System Overview

PipeBot is an autonomous robotic crawler engineered to inspect rigid municipal and residential PVC drainage conduits (150 mm to 300 mm internal diameter).

### Core Capabilities:
- **Crawler Chassis**: Low-profile tracked crawler driven by dual DC gearmotors.
- **Embedded Motion Subsystem**: ESP32-WROOM-32 microcontroller executing quadrature encoder pulse decoding and MPU6050 6-axis inertial attitude tracking.
- **Optical Inspection Node**: AI-Thinker ESP32-CAM (OV2640 sensor) transmitting continuous MJPEG video over local Wi-Fi.
- **Computer Vision Pipeline**: Ultralytics YOLOv8 neural network trained to detect 4 canonical defect classes:
  - `0: Deformation` (cross-sectional ovality crushing)
  - `1: Misalignment` (conduit joint offset)
  - `2: Obstacle` (roots, debris, mechanical blockage)
  - `3: Rupture` (fractures, shear tears, punctures)
- **Spatial Localization**: Correlates optical frame detections with wheel encoder odometry to record exact defect locations along the conduit invert.
- **Operator Console**: Neo-Brutalist industrial dashboard providing real-time telemetry gauges, longitudinal conduit defect timelines, camera ingestion controls, and evidence review workflows.

---

## 2. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend Console** | React 18, TypeScript 5, Vite 6, Tailwind CSS 3.4, React Router 6, Lucide Icons |
| **Backend Service** | Python 3.10, FastAPI, Uvicorn, Pydantic v2 Settings & Schemas, OpenCV (headless) |
| **Persistence Layer** | SQLAlchemy 2.0 ORM, Alembic Migrations, SQLite 3 (WAL mode), PostgreSQL 16 ready |
| **Computer Vision** | Ultralytics YOLOv8, PyTorch 2.x, CUDA 12.x on NVIDIA GeForce RTX 2050 (4 GB VRAM) |
| **Microcontrollers** | ESP32-WROOM-32 (motor control, odometry, IMU), AI-Thinker ESP32-CAM (video stream) |
| **Protocols** | Duplex WebSocket (`/ws/telemetry`), REST HTTP JSON (`/api/v1`), MJPEG Video (`/stream`) |

---

## 3. Repository Organization

```text
D:\PipeBot
├── ai-model/               # Dedicated AI workspace: configs, dataset splits, training, weights
│   ├── configs/            # Ultralytics YOLOv8 dataset configuration (yolov8_pipebot.yaml)
│   ├── dataset/            # Training/validation splits (Pipe Defect Detection.v7)
│   ├── weights/            # Trained weights (best.pt, best.onnx)
│   └── README.md           # Model architecture, training recipes, and VRAM guidelines
├── backend/                # Python FastAPI backend service
│   ├── app/                # Routers, services, repositories, models, camera, vision
│   ├── data/               # Persistent SQLite database (pipebot.db)
│   ├── migrations/         # Alembic database migrations
│   ├── scripts/            # Database inspection, benchmarking, and em dash scan utilities
│   ├── tests/              # 120 passing pytest test cases
│   └── requirements.txt    # Pinned backend Python dependencies
├── database/               # Database engineering guide, operational runbooks, and recovery
├── docs/                   # System architecture, software design, and development setup
│   ├── architecture/       # System and software architecture specifications
│   ├── database/           # Complete database design reports and schema blueprints
│   └── development/        # Setup guides, audit reports, and milestone assessments
├── firmware/               # Microcontroller pinouts, schematics, and firmware specs
│   ├── esp32-controller/  # ESP32-WROOM-32 motion, odometry, and IMU firmware docs
│   └── esp32-camera/      # AI-Thinker ESP32-CAM video streaming firmware docs
├── media/                  # Evidence snapshot archives and PDF compliance reports
├── public/                 # Static assets and brand marks
├── scripts/                # Frontend verification test runner (Node.js test suite)
├── src/                    # React 18 / TypeScript operator dashboard source code
│   ├── app/                # Root App, React Router, AppContext, ToastProvider
│   ├── components/         # Neo-Brutalist UI components, Timeline, Camera Controls
│   ├── constants/          # Application configuration, API endpoints, routes
│   ├── pages/              # Overview, Inspection, Vehicle, Telemetry, Defects, History
│   ├── services/           # apiClient, WebSocketClient, cameraService, defectService
│   └── types/              # TypeScript interface definitions matching backend schemas
└── package.json            # Node.js project configuration and scripts
```

---

## 4. Quick Start & Development Setup

### Backend Service (FastAPI):
```bash
# 1. Navigate to backend in WSL Ubuntu
cd /mnt/d/PipeBot/backend

# 2. Activate Python 3.10 virtual environment
source .venv/bin/activate

# 3. Start development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Endpoint: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Subsystem Status: `http://127.0.0.1:8000/api/v1/system/status`
- Telemetry WebSocket: `ws://127.0.0.1:8000/ws/telemetry`

### Frontend Operator Console (React + Vite):
```powershell
# 1. Open terminal in project root
cd D:\PipeBot

# 2. Start Vite development server
npm run dev
```
- Operator Console: `http://localhost:3000` (proxies `/api` and `/ws` to FastAPI)

---

## 5. Automated Verification Suites

The repository enforces complete regression testing before releases:

```bash
# Run all 120 Backend Pytest Tests
cd /mnt/d/PipeBot/backend && pytest -v

# Run Frontend Verification Suite (16 Tests)
npm test

# Run TypeScript Strict Compilation
npm run typecheck

# Run Production Bundle Build
npm run build

# Run Em Dash Encoding Audit (Strict Zero Unicode \u2014)
python backend/scripts/scan_em_dashes.py
```

---

## 6. Next Immediate Phase: AI Model Training

The codebase cleanup and architecture refinement phase is complete. The next engineering phase is:
1. Ingest `Pipe Defect Detection.v7 Dataset Pipe.yolov8` into `ai-model/dataset/`.
2. Train YOLOv8 on the NVIDIA RTX 2050 using `ai-model/configs/yolov8_pipebot.yaml`.
3. Validate detection accuracy across the 4 canonical anomaly classes.
4. Export weights to `ai-model/weights/best.pt` for live backend inference.
