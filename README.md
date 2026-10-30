# PipeBot: AI-Powered Robotic PVC Pipeline Inspection System

> **Frontend Status**: Stage 5 of 5 Completed (Complete Frontend QA, Visual Polish, Security, Accessibility & Release Readiness).  
> **Backend Status**: Stage 5 of 5 Completed (Backend Integration QA, Security, Performance, Documentation and 10-Commit GitHub Release).  
> The PipeBot system pairs a production-grade React/TypeScript operator dashboard with a modular Python FastAPI backend service, SQLite database persistence, Alembic migrations, thread-safe in-memory telemetry ingestion, duplex operator WebSocket streaming, ESP32-CAM MJPEG stream parsing, OpenCV frame validation, pluggable AI inference abstraction, temporal-spatial localization safety policies, and automated defect persistence with 99 passing tests. Real hardware bench validation, YOLO model training, and production database migration are scheduled for subsequent engineering phases.

---

## 1. Project Overview

PipeBot is an AI-powered robotic pipeline inspection platform engineered to inspect the internal condition of rigid PVC conduits (150 mm to 300 mm). The system combines:
- An internal crawler chassis driven by dual DC gearmotors.
- An ESP32-WROOM-32 microcontroller handling motor control, encoder odometry, and telemetry.
- An ESP32-CAM module transmitting live pipeline video over local Wi-Fi.
- A custom YOLO neural network detecting pipeline defects (`Deformation`, `Misalignment`, `Obstacle`, `Rupture`).
- Dual optical encoder distance tracking for estimating defect locations.
- An operator dashboard with automated inspection report management.

---

## 2. Technology Stack

- **Framework**: React 18 (`react`, `react-dom`)
- **Bundler & Dev Server**: Vite 6
- **Language**: TypeScript 5 (Strict Mode enabled, zero `any` types)
- **Styling**: Tailwind CSS 3.4 with custom industrial design tokens
- **Routing**: React Router DOM 6.28 (`createBrowserRouter`)
- **State Management**: Centralized React Context (`AppContext`) with domain hooks
- **Service Layer**: AbortController-backed Fetch client, typed WebSocket client with backoff
- **Icons**: Lucide React (`lucide-react`)
- **Utilities**: `clsx`, `tailwind-merge`

---

## 3. Directory Structure

```text
D:\PipeBot
├── backend/                         # Python FastAPI backend service
│   ├── app/                         # Core application, API endpoints, db, schemas, services
│   ├── data/                        # Local SQLite persistent storage (gitignored)
│   ├── logs/                        # Rotating application log outputs (gitignored)
│   ├── migrations/                  # Alembic database migration scripts
│   ├── tests/                       # Pytest automated test suite
│   ├── .env.example                 # Example backend environment variables
│   ├── pyproject.toml               # Project metadata and pytest configuration
│   ├── requirements.txt             # Pinned backend Python dependencies
│   └── README.md                    # Backend architecture and setup instructions
├── docs/
│   ├── ARCHITECTURE.md              # Hardware & system architecture specifications
│   ├── frontend-integration.md      # Service layer, WebSocket, & API integration manual
│   └── frontend-release-checklist.md # Quality assurance & release verification matrix
├── public/
│   ├── favicon.svg                  # Custom PipeBot brand mark SVG icon
│   └── assets/                      # Public static assets
├── scripts/
│   ├── verify-frontend.mjs          # Complete unit & integration test suite (Node test runner)
│   └── run-browser-audit.mjs        # Browser-level QA script executing headless Google Chrome
├── src/
│   ├── app/
│   │   ├── App.tsx                  # Root app component with router & provider wrapper
│   │   ├── router.tsx               # React Router route definitions
│   │   └── providers/               # AppContext state provider and domain hooks
│   ├── components/
│   │   ├── ui/                      # Reusable UI component library (Button, Card, Badge, Table, etc.)
│   │   ├── layout/                  # Header, Sidebar, Navigation, and DashboardLayout shell
│   │   └── shared/                  # Shared domain components (DemoModeBanner, VerificationBanner)
│   ├── features/                    # Domain models and feature logic
│   │   ├── inspection/              # Mission models and inspection contracts
│   │   ├── vehicle/                 # Motor commands and propulsion types
│   │   ├── telemetry/               # Sensor and odometry packet structures
│   │   ├── defects/                 # YOLO inference detections and bounding boxes
│   │   ├── reports/                 # Compliance reports and export models
│   │   └── settings/                # Hardware connection configurations
│   ├── hooks/                       # Custom React hooks (useDocumentTitle)
│   ├── pages/                       # Application route views
│   │   ├── landing/                 # Public landing portal
│   │   ├── legal/                   # Legal drafts (/privacy, /terms)
│   │   ├── dashboard/               # 8 modular operator dashboard views
│   │   └── not-found/               # Error 404 Route Not Found page
│   ├── services/                    # Typed API client & domain service layer
│   │   ├── api/                     # Base API client, error normalizer, and endpoints
│   │   ├── camera/                  # Camera stream probe abstraction
│   │   ├── connection/              # Subsystem connection health service
│   │   ├── defects/                 # Defect retrieval & review service
│   │   ├── demo/                    # Isolated demo simulation dataset
│   │   ├── inspection/              # Mission lifecycle management service
│   │   ├── reports/                 # Report generation & retrieval service
│   │   ├── telemetry/               # Odometry & IMU telemetry polling service
│   │   └── websocket/               # Typed WebSocket client with exponential backoff
│   ├── types/                       # Shared TypeScript definitions & domain contracts
│   ├── utils/                       # Helper utilities (cn, formatters)
│   ├── constants/                   # System config, environment validation, routes
│   ├── styles/
│   │   ├── tokens.css               # CSS design tokens
│   │   └── globals.css              # Tailwind base & global styles
│   ├── vite-env.d.ts                # Vite environment variable type declarations
│   └── main.tsx                     # Application entry point
├── .env.example                     # Example backend & camera stream configuration
├── .gitignore
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── README.md
```

---

## 4. Configured Application Routes

| Route | Destination | Document Title | Status |
| :--- | :--- | :--- | :--- |
| `/` | Public Landing Page | `PipeBot \| Intelligent Pipeline Inspection` | Production Verified |
| `/privacy` | Privacy Policy Draft | `PipeBot \| Privacy Policy (Draft)` | Production Verified |
| `/terms` | Terms of Use Draft | `PipeBot \| Terms of Use (Draft)` | Production Verified |
| `/dashboard` | Operational Overview | `PipeBot \| Console Overview` | Production Verified |
| `/dashboard/inspection` | Live Inspection Studio | `PipeBot \| Live Inspection` | Production Verified |
| `/dashboard/vehicle` | Vehicle Propulsion Control | `PipeBot \| Vehicle Control` | Production Verified |
| `/dashboard/telemetry` | Sensor & Encoder Telemetry | `PipeBot \| Odometry & Telemetry` | Production Verified |
| `/dashboard/defects` | Defect Records & AI Registry | `PipeBot \| Defect Registry` | Production Verified |
| `/dashboard/history` | Past Mission Archives | `PipeBot \| Inspection History` | Production Verified |
| `/dashboard/reports` | Inspection Reports | `PipeBot \| Inspection Reports` | Production Verified |
| `/dashboard/settings` | System Settings | `PipeBot \| System Settings` | Production Verified |
| `*` | 404 Route Not Found | `PipeBot \| Page Not Found` | Production Verified |

---

## 5. Development, Verification & Build Commands

All commands must be executed strictly from `D:\PipeBot`:

### Install Dependencies
```powershell
npm install
```

### Start Local Development Server
```powershell
npm run dev
```
The server will start at `http://127.0.0.1:3000`.

### Type-Check TypeScript
```powershell
npm run typecheck
```
Executes `tsc --noEmit` across all modules. Must exit with code 0.

### Run Automated Unit & Integration Tests
```powershell
npm test
```
Executes Node.js test runner against `scripts/verify-frontend.mjs` verifying routing, state isolation, filtering, API errors, WebSocket contracts, and odometry physics.

### Run Real Browser QA Audit
```powershell
node scripts/run-browser-audit.mjs
```
Launches headless Google Chrome to verify DOM rendering and titles across all 11 routes and 5 responsive viewports.

### Production Build
```powershell
npm run build
```
Type checks and bundles minified production assets into `D:\PipeBot\dist`.

### Preview Production Build
```powershell
npm run preview
```
Serves the bundled production distribution locally at `http://localhost:4173`.

---

## 6. Backend Setup & Execution Commands (Stage 1 Foundation)

All backend commands are executed inside `D:\PipeBot\backend`:

### Install Backend Dependencies (WSL / Linux)
```bash
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Backend Automated Tests
```bash
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
pytest -v
```

### Start Backend Development Server
```bash
cd /mnt/d/PipeBot/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI documentation will be accessible at `http://127.0.0.1:8000/docs`.

---

## 7. Environment Configuration

Copy `.env.example` to create your local `.env`:

```bash
# Backend REST API endpoint (Python FastAPI server)
VITE_API_BASE_URL=http://127.0.0.1:8000/api

# Backend WebSocket endpoint for duplex telemetry stream
VITE_WS_URL=ws://127.0.0.1:8000/ws

# ESP32-CAM MJPEG optical feed stream URL
VITE_CAMERA_STREAM_URL=http://192.168.4.1/stream

# Initial application runtime mode: "disconnected" | "demo"
VITE_APP_MODE=disconnected
```

### Safe Fallbacks
If environment variables are omitted, the application defaults safely to disconnected modes:
- `apiBaseUrl`: defaults to `""` (no unconfigured requests).
- `wsUrl`: defaults to `""` (no unsolicited connections).
- `cameraStreamUrl`: defaults to `""` (offline reticle shown).
- `defaultMode`: defaults to `'disconnected'`.

---

## 8. Operating Modes: Disconnected Mode vs. Demo Mode

The frontend includes a toggleable mode switcher accessible via the top navigation bar or the Settings page:

### Disconnected Mode (Default Production Setting)
- Designed for authentic deployment before backend linkup.
- Hardware statuses accurately report `disconnected`.
- Telemetry displays `null` or awaiting telemetry metrics.
- Defect and inspection arrays return strictly empty `[]`.
- Camera viewport renders an industrial disconnected reticle.
- Vehicle propulsion controls are genuinely disabled with safety notices.

### Demo Mode (Controlled Simulation Setting)
- Designed for interface evaluation, workflow testing, and operator training.
- Displays a prominent, high-visibility yellow warning banner across all dashboard views.
- Populates exactly 4 representative defect records covering all target classes (`deformation`, `misalignment`, `obstacle`, `rupture`).
- Every demo object is explicitly tagged with `isDemo: true`.
- Allows client-side multi-criteria filtering by class, review status, and search query.
- Toggling back to Disconnected Mode flushes all demo data from memory immediately.
- **Safety Guarantee**: Propulsion controls remain genuinely disabled in Demo Mode. Demo Mode never simulates false vehicle locomotion.

---

## 9. Current Implementation Limitations

1. **Hardware Actuation**: Vehicle propulsion buttons and motor sliders are locked and disabled. No physical motor control signals are transmitted.
2. **Video Streaming**: Camera feeds display disconnected test patterns. Live optical streaming requires the physical ESP32-CAM module and vision ingestion server.
3. **Backend Service Layer**: Backend development (Stages 1 through 5) is complete with 99 passing automated tests. Automated PDF report generation, PostgreSQL migration, and distributed scaling are deferred to dedicated future milestones.
4. **Dual-MCU Synchronization**: Associating ESP32-CAM frame capture timestamps with ESP32-WROOM-32 encoder counts requires a validated hardware clock synchronization protocol. Physical localization is safely suspended until embedded synchronization is calibrated.
5. **Report Exports**: PDF export buttons are locked until the server-side report compilation pipeline is deployed.
6. **Legal Status**: Privacy Policy and Terms of Use documents are engineering drafts and require legal review prior to commercial deployment.

---

## 10. Future Integration Roadmap

- **Backend Integration**: Python FastAPI REST API (`/api/v1/*`) and WebSocket telemetry ingestion.
- **Microcontroller Firmware**: ESP32-WROOM-32 motor PWM control, quadrature encoder interrupts, and MPU6050 I2C reading.
- **Computer Vision**: Custom YOLO model weights for real-time inference and bounding box extraction.
- **Synchronization**: Precise hardware shutter synchronization linking optical capture timestamps with encoder pulses.
- **Database**: PostgreSQL / SQLite persistent inspection database.
- **Reporting Engine**: Headless PDF report compilation and export service.
- **Field Deployment**: Encrypted HTTPS/WSS communication and ruggedized tablet deployment.
