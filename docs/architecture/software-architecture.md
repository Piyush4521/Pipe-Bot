# PipeBot Software Architecture Specification

This document details the software design patterns, component hierarchies, state management, and API contracts across the frontend and backend applications.

## 1. Architectural Principles

1. Separation of Concerns: Strict layering between presentation, API transport, business domain logic, and data persistence.
2. Production-Grade Robustness: No silent failures, no hardcoded unverified states, and defensive validation at system boundaries.
3. Strict Zero Em Dash Policy: All code, comments, documentation, and user interfaces strictly avoid em dash characters (`\u2014`) to ensure cross-platform character encoding integrity.
4. Audit-Preserving Data Policy: Critical inspection records and defect evidence must never be destructively cascade-deleted. Restrictive foreign keys protect historical evidence.
5. UTC Timestamp Normalization: Every datetime across API envelopes, database columns, and WebSocket payloads is normalized to UTC ISO 8601 strings with trailing 'Z'.

## 2. Frontend Software Architecture (React 18 + TypeScript)

### Directory Structure:
```text
src/
├── app/
│   ├── App.tsx             # Root application component
│   ├── router.tsx          # React Router v6 route configuration
│   └── providers/
│       ├── AppContext.tsx  # Centralized live/demo application state and WebSocket ingestion
│       └── index.tsx       # Root provider composition (ToastProvider + AppProvider)
├── components/
│   ├── layout/             # DashboardHeader, Sidebar, Navigation, Shell layouts
│   ├── ui/                 # Neo-Brutalist design system (Button, Card, Badge, Table, Toast)
│   ├── inspection/         # PipeTimeline, CameraStreamControls, NewInspectionModal
│   ├── defects/            # DefectDetailDrawer, BoundingBoxCanvas
│   └── shared/             # DemoModeBanner, route utilities
├── constants/
│   ├── config.ts           # Centralized environment configuration and defaults
│   └── routes.ts           # Type-safe route paths
├── services/
│   ├── api/                # apiClient, apiErrors, endpoints
│   ├── connection/         # Health and system status services
│   ├── inspection/         # Inspection session lifecycle operations
│   ├── defects/            # Defect retrieval and review status updates
│   ├── camera/             # Camera worker controls and frame ingestion
│   ├── telemetry/          # Odometry and IMU telemetry fetching
│   ├── websocket/          # Duplex WebSocketClient with exponential backoff
│   └── demo/               # Controlled demo fixture data (strictly isolated)
└── types/                  # Shared TypeScript interfaces matching backend schemas
```

### State Management Pattern:
- `AppContext`: Acts as the unified telemetry and data bus. It orchestrates polling or WebSocket ingestion for live data while maintaining 100% isolation when Demo Mode is toggled.
- Reactivity: When live WebSocket envelopes arrive (`telemetry_encoder`, `defect_detected`), React state hooks trigger targeted re-renders without full-page refreshes.
- Graceful Degradation: If the backend is offline, the UI renders authentic disconnected indicators and clean empty states rather than crashing or showing placeholder numbers.

### Error Handling & Resilience:
- `apiClient`: Normalizes network dropouts and timeouts into typed `ApiError` instances.
- `WebSocketClient`: Features exponential backoff reconnection (1s, 2s, 4s, 8s, capped at 16s) and packet validation.

## 3. Backend Software Architecture (FastAPI + SQLAlchemy 2.0)

### Directory Structure:
```text
backend/app/
├── api/v1/
│   ├── router.py           # Master API v1 router aggregation
│   └── endpoints/          # inspections, defects, telemetry, camera, vision, health, system
├── core/
│   ├── config.py           # Pydantic Settings with .env loading
│   ├── exceptions.py       # Domain exception hierarchy (ResourceNotFoundError, ConflictError)
│   └── lifespan.py         # Startup / shutdown lifecycle orchestration
├── db/
│   ├── base.py             # SQLAlchemy DeclarativeBase, BigIntId, UtcDateTime, TimestampMixin
│   ├── session.py          # Engine and sessionmaker with connection health pre-pings
│   └── backup.py           # Atomic SQLite backup and restore utilities
├── models/                 # 16 SQLAlchemy 2.0 mapped models
├── repositories/           # Data access objects with explicit queries
├── schemas/                # Pydantic v2 validation schemas with camelCase aliases
├── services/               # InspectionService, DefectService, HealthService, TelemetryState
├── camera/                 # CameraClient, CameraState, OpenCV frame validation
└── vision/                 # InferenceProvider base, UltralyticsProvider, mock fallback
```

### Layered Execution Flow:
1. Endpoint Router (`app/api/v1/endpoints/`): Unpacks HTTP request parameters, validates JWT/device tokens, and parses bodies using Pydantic.
2. Domain Service (`app/services/`): Enforces business rules (e.g. valid inspection lifecycle transitions, timestamp normalization).
3. Repository Layer (`app/repositories/`): Executes type-safe SQLAlchemy queries with filtering, sorting, and pagination.
4. Database Session (`app/db/session.py`): Manages relational transactions with automatic commit and rollback.

### Schema Validation & Serialization:
- Pydantic v2 models utilize `alias_generator=to_camel` and `populate_by_name=True`.
- This ensures Python snake_case variables serialize directly to JavaScript camelCase properties (e.g. `pipe_identifier` -> `pipeIdentifier`).
