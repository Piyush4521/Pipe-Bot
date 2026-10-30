# PipeBot Development Setup & Operational Guide

This document provides complete instructions for configuring, developing, testing, and running the PipeBot robotic inspection system on Windows 11 and WSL Ubuntu 22.04.

## 1. System Requirements

- Operating System: Windows 11 with WSL2 (Ubuntu 22.04 LTS)
- Python: Version 3.10.x (WSL environment recommended)
- Node.js: Version 18.x or 20.x LTS
- GPU Acceleration: NVIDIA GeForce RTX 2050 (or any modern NVIDIA GPU with CUDA support)
- NVIDIA Drivers: Game Ready / Studio Driver with CUDA 12.x support

## 2. Backend Environment Setup

The backend runs on Python 3.10 within WSL Ubuntu 22.04:

```bash
# 1. Navigate to backend directory in WSL
cd /mnt/d/PipeBot/backend

# 2. Create and activate Python 3.10 virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# 3. Upgrade package installer
pip install --upgrade pip setuptools wheel

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Verify database schema revision
alembic current
# Expected output: d4d255efae0c (head)
```

### Launching the Backend Development Server:

```bash
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend server is accessible at:
- API Base: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`
- System Status: `http://127.0.0.1:8000/api/v1/system/status`
- Telemetry WebSocket: `ws://127.0.0.1:8000/ws/telemetry`

## 3. Frontend Environment Setup

The frontend runs on Node.js using Vite:

```powershell
# Open terminal in project root
cd D:\PipeBot

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend dashboard is accessible at `http://localhost:3000`.
Vite is preconfigured to reverse-proxy `/api` and `/ws` traffic to `http://127.0.0.1:8000`.

## 4. Running Automated Verification Suites

### Backend Tests (120 Pytest Test Cases):
```bash
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
pytest -v
```

### Frontend Tests (16 Verification Test Cases):
```powershell
cd D:\PipeBot
npm test
```

### Frontend TypeScript Compilation & Typecheck:
```powershell
cd D:\PipeBot
npm run typecheck
```

### Frontend Production Build:
```powershell
cd D:\PipeBot
npm run build
```

### Character Encoding & Em Dash Verification:
To verify that strictly zero em dashes (`\u2014`) exist in the codebase:
```bash
cd /mnt/d/PipeBot/backend
python scripts/scan_em_dashes.py
```

## 5. Active Database Inspection & Backup Utilities

Inspect the active SQLite database without modifying records:
```bash
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
python scripts/inspect_active_db.py
```

Create an atomic verified backup snapshot:
```bash
python -c "from app.db.backup import backup_sqlite_database; print(backup_sqlite_database())"
```
Snapshots are preserved under `backend/backups/`.
