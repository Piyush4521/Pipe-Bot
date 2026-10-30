# PipeBot Frontend Architecture Documentation

## 1. System Overview

PipeBot is an AI-powered robotic PVC pipeline inspection system designed to operate autonomously inside subterranean conduits, pipelines, and industrial sewers. The complete platform combines:

1. **Crawler Chassis & Propulsion**: Driven by dual DC gearmotors.
2. **Microcontroller Telemetry**: ESP32-WROOM-32 handling motor PWM, encoder odometry, and health telemetry.
3. **Vision Payload**: ESP32-CAM module (OV2640) streaming real-time video.
4. **AI Inference**: Custom YOLO defect detection model detecting cracks, deformations, joint displacements, and blockages.
5. **Backend Server**: Python FastAPI backend mediating WebSocket telemetry and REST reporting.
6. **Operator Frontend**: Modern React + TypeScript + Tailwind CSS dashboard.

---

## 2. Five-Stage Development Lifecycle

- **Stage 1 (Current)**: Project Initialization, Architecture & Design System Foundation.
- **Stage 2**: Public Landing Page & Editorial Pipeline Showcase.
- **Stage 3**: Core Operational Dashboard & Sensor Telemetry Streams.
- **Stage 4**: Live Inspection Studio, Vision Stream & Defect Records.
- **Stage 5**: Automated Inspection Reports, System Settings & Backend Integration.

---

## 3. Directory Layout

```text
D:\PipeBot
├── docs/
│   └── ARCHITECTURE.md          # Architectural documentation and design specifications
├── public/
│   ├── favicon.svg              # Scalable SVG brand mark
│   └── assets/                  # Static assets
├── src/
│   ├── app/
│   │   ├── App.tsx              # Application root component
│   │   ├── router.tsx           # React Router v6 browser route definitions
│   │   └── providers/           # Global context providers
│   ├── components/
│   │   ├── ui/                  # Reusable design system primitives (Button, Card, Badge, etc.)
│   │   ├── layout/              # RootLayout, Navigation header, footer
│   │   └── shared/              # Common shared domain components
│   ├── pages/
│   │   ├── landing/             # Public landing portal
│   │   ├── dashboard/           # Dashboard views (Overview, Inspection, Telemetry, etc.)
│   │   └── not-found/           # 404 Route handler
│   ├── features/                # Domain-driven feature modules
│   │   ├── inspection/          # Mission models and inspection contracts
│   │   ├── vehicle/             # Motor commands and propulsion state
│   │   ├── telemetry/           # Odometry and sensor packet models
│   │   ├── defects/             # YOLO inference detections and bounding boxes
│   │   ├── reports/             # Compliance reports and export models
│   │   └── settings/            # Hardware connection configurations
│   ├── hooks/                   # Reusable React hooks
│   ├── services/                # API client and network protocols
│   ├── types/                   # Shared TypeScript definitions
│   ├── utils/                   # Helper functions (cn, formatters)
│   ├── constants/               # Route paths and system hardware constants
│   ├── styles/
│   │   ├── tokens.css           # CSS custom property design tokens
│   │   └── globals.css          # Tailwind base & global styles
│   └── main.tsx                 # Vite React application entry point
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

## 4. Design System Specification

### Color Tokens

- **Page Background**: `#F8F9FA` (Off-white industrial slate)
- **Surfaces**: `#FFFFFF` with `#E2E8F0` / `#CBD5E1` neutral borders
- **Primary Typography**: `#0F172A` (Slate 900)
- **Secondary Typography**: `#475569` (Slate 600) / `#64748B` (Slate 500)
- **Industrial Accent**: `#EA580C` (Safety Orange)
- **Status Indicators**:
  - Healthy: `#16A34A`
  - Warning: `#D97706`
  - Critical: `#DC2626`
  - Offline / Idle: `#64748B`

### Visual Constraints

- Square or moderately rounded corners (`rounded-sm` / `2px` - `4px`).
- Rectangular buttons with crisp borders.
- No pill-shaped buttons or excessively rounded cards.
- No purple gradients or generic AI-generated hero visuals.
- Technical figures formatted in high-contrast monospaced typography.

