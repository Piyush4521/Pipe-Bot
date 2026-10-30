# PipeBot Frontend Integration Architecture & Service Layer Specification

This document provides a comprehensive technical reference for the PipeBot frontend service layer, communication protocols, data contracts, and integration readiness ahead of backend (Python FastAPI) and microcontroller (ESP32) deployment.

---

## 1. Environment Configuration

The frontend dynamically loads its integration targets through Vite environment variables defined in `.env.example`:

```bash
# Backend REST API endpoint (FastAPI)
VITE_API_BASE_URL=http://127.0.0.1:8000

# Backend WebSocket telemetry & event streaming endpoint
VITE_WS_URL=ws://127.0.0.1:8000/ws/telemetry

# ESP32-CAM MJPEG or HLS raw video stream URL
VITE_CAMERA_STREAM_URL=http://192.168.4.1/stream

# Initial application runtime mode: "disconnected" | "demo"
VITE_APP_MODE=disconnected
```

### Safety and Configuration Fallbacks
All environment variables are validated at startup via `src/constants/config.ts`. If variables are omitted or invalid, the application falls back safely to disconnected localhost parameters:
- `apiBaseUrl`: defaults to `http://127.0.0.1:8000`
- `wsUrl`: defaults to `ws://127.0.0.1:8000/ws/telemetry`
- `cameraStreamUrl`: defaults to empty string `""` (preventing unsolicited network connections)
- `defaultAppMode`: defaults to `'disconnected'`
- `requestTimeoutMs`: defaults to `8000` ms

---

## 2. System Architecture & Information Flow

PipeBot's architecture strictly decouples video streaming, telemetry ingestion, motor control, and AI inference:

```text
               +-----------------------------+
               |        ESP32-CAM            |
               |  (Dedicated Video Module)   |
               +--------------+--------------+
                              |
                              | Local Wi-Fi HTTP Stream (MJPEG / HLS)
                              v
               +-----------------------------+
               |     Python Vision Server    |
               |       (YOLO Inference)      |
               +--------------+--------------+
                              |
                              | Frame Inferences + Defect Bounding Boxes
                              v
+------------------+   +-----------------------------+   +------------------------+
|  ESP32-WROOM-32  |-->|    FastAPI Local Backend    |<--| PipeBot React Frontend |
| (Odometry & IMU) |   |    (REST API & WebSocket)   |   | (Operator Dashboard)   |
+------------------+   +-----------------------------+   +------------------------+
```

### Key Architectural Rules
1. **Decoupled Optical Pipeline**: Camera video frames are transmitted directly from the ESP32-CAM to the OpenCV / YOLO processing pipeline. Video frames are never routed through relational databases, Firebase, or the ESP32-WROOM-32 motor microcontroller.
2. **Server-Side Inference**: Neural network detection runs entirely on the Python vision server, keeping microcontrollers lightweight and responsive.
3. **Structured Event Delivery**: The frontend receives structured telemetry envelopes and defect detection events from FastAPI via WebSocket, while historical records are retrieved via REST.

---

## 3. Data Contracts & Model Specifications

All contracts are strictly typed in `src/types/index.ts` with complete type safety (zero `any`).

### 3.1. Optical Frame Metadata & Timestamp Association
Physical distance cannot be reliably calculated using server-side inference timestamps due to network transport and GPU processing latency. Therefore, optical frames must carry capture-time encoder odometry:

```typescript
export interface FrameMetadata {
  frameId: string;
  captureTimestamp: string;               // High-resolution timestamp from ESP32-CAM
  encoderLeftTicks: number | null;        // Pulse count recorded at shutter release
  encoderRightTicks: number | null;       // Pulse count recorded at shutter release
  estimatedDistanceMeters: number | null; // Correlated distance at optical capture
}
```

### 3.2. Target Defect Classifications
The pipeline detection model targets 4 specific PVC conduit anomaly classes:

```typescript
export type DefectClass = 'deformation' | 'misalignment' | 'obstacle' | 'rupture';
export type DefectReviewStatus = 'unreviewed' | 'verified' | 'dismissed';

export interface BoundingBox {
  x: number;      // Bounding box origin X (pixels or normalized 0-1)
  y: number;      // Bounding box origin Y
  width: number;  // Width
  height: number; // Height
}

export interface DefectDetection extends BaseEntity {
  inspectionId: string;
  defectClass: DefectClass;
  confidence: number | null;              // 0.0 to 1.0 confidence score
  frameId: string;
  captureTimestamp: string;               // ESP32-CAM capture timestamp
  inferenceTimestamp: string | null;      // YOLO evaluation timestamp
  estimatedDistanceMeters: number | null; // Odometry correlated at capture time
  reviewStatus: DefectReviewStatus;
  boundingBox?: BoundingBox;
  snapshotUrl?: string;
  notes?: string;
  isDemo?: boolean;                       // Flag guaranteeing demo isolation
}
```

### 3.3. Rotary Encoder Odometry
Wheel odometry tracks crawler penetration depth inside the conduit:

```typescript
export interface EncoderTelemetry {
  leftTicks: number | null;
  rightTicks: number | null;
  leftRpm: number | null;
  rightRpm: number | null;
  estimatedDistanceMeters: number | null;
  timestamp: string | null;
}
```

**Odometry Physics Formula**:
```text
Revolutions = (LeftTicks + RightTicks) / (2 * PulsesPerRevolution)
Circumference_mm = PI * WheelDiameter_mm
Distance_meters = (Revolutions * Circumference_mm) / 1000
```

### 3.4. Inertial Measurement Unit (IMU - MPU6050)
The 6-axis gyroscope/accelerometer measures crawler attitude and conduit slope:

```typescript
export interface IMUTelemetry {
  accelX: number | null;
  accelY: number | null;
  accelZ: number | null;
  gyroX: number | null;
  gyroY: number | null;
  gyroZ: number | null;
  pitchDegrees: number | null; // Pipe slope / gradient
  rollDegrees: number | null;  // Vehicle tilt
  timestamp: string | null;
}
```

---

## 4. REST API Client Specification

The frontend encapsulates all HTTP communication through `ApiClient` (`src/services/api/apiClient.ts`).

### 4.1. Proposed Backend Endpoints
```text
GET  /api/v1/system/status             # Query hardware and subsystem health
GET  /api/v1/inspection/current        # Get currently active inspection metadata
POST /api/v1/inspection/start          # Start new inspection mission
POST /api/v1/inspection/stop           # Conclude current mission
GET  /api/v1/inspection/history        # List historical inspection sessions
GET  /api/v1/telemetry/latest          # Get latest encoder & IMU snapshot
GET  /api/v1/defects                   # List detected defects (supports query filters)
GET  /api/v1/defects/{id}              # Retrieve specific defect record
PATCH /api/v1/defects/{id}/review      # Update defect review status (verified/dismissed)
GET  /api/v1/reports                   # List generated inspection reports
GET  /api/v1/reports/{id}              # Retrieve report details
POST /api/v1/reports/generate          # Trigger compliance report generation
```

### 4.2. Error Normalization (`ApiError`)
All failed network requests, non-2xx HTTP responses, and timeouts are normalized into `ApiError` instances (`src/services/api/apiErrors.ts`):
- `isNetworkError`: indicates DNS resolution, offline network, or backend down.
- `isTimeout`: indicates request exceeded the configured threshold (default 8s).
- `statusCode`: HTTP status code (e.g. 404, 500) if a response was received.

---

## 5. WebSocket Telemetry Protocol

Real-time telemetry and defect events are delivered via WebSocket client (`src/services/websocket/webSocketClient.ts`).

### 5.1. Message Envelope Structure
Every WebSocket payload follows a standardized typed envelope:

```json
{
  "type": "telemetry_encoder",
  "timestamp": "2026-10-30T10:30:00.000Z",
  "payload": {
    "leftTicks": 4120,
    "rightTicks": 4118,
    "leftRpm": 42.5,
    "rightRpm": 42.3,
    "estimatedDistanceMeters": 14.52,
    "timestamp": "2026-10-30T10:30:00.000Z"
  }
}
```

### 5.2. Supported Message Types
- `system_status`: Subsystem connection heartbeat
- `telemetry_encoder`: Dual-encoder odometry pulses and computed distance
- `telemetry_imu`: MPU6050 pitch, roll, and accelerations
- `vehicle_status`: Motor controller, voltage, and current metrics
- `inspection_status`: Mission status transitions (started, paused, completed)
- `defect_detected`: Real-time YOLO detection event with bounding box
- `connection_error`: Server-side socket diagnostic warnings

### 5.3. Resilience & Exponential Backoff
The client incorporates an automatic reconnection strategy:
- Initial delay: 1,000 ms
- Backoff multiplier: 1.5x with ceiling at 16,000 ms
- Max reconnection attempts: 5 before transitioning to persistent `disconnected` state
- Clean socket tear-down during intentional disconnect or page unmount

---

## 6. Application Modes & Demo Isolation

The frontend operates in two distinct execution modes:

```text
+--------------------------------------------------------------------------+
|                            APP MODE SWITCHER                             |
+------------------------------------+-------------------------------------+
|         Disconnected Mode          |              Demo Mode              |
|        (Production Default)        |        (Operator Simulation)        |
+------------------------------------+-------------------------------------+
| Hardware state: Disconnected       | Hardware state: Simulated           |
| Camera: Offline / No Signal        | Camera: Disconnected / Reticle test |
| Telemetry: Null / 0.0              | Telemetry: Realistic conduit run    |
| Defect records: Empty []           | Defect records: 4 target anomalies  |
| Inspection history: Empty []       | Inspection history: 1 completed run |
| Controls: Disabled (Safety lock)   | Controls: Disabled (Safety lock)    |
| Banner: Hidden                     | Banner: Prominent Warning Banner    |
+------------------------------------+-------------------------------------+
```

### Demo Data Isolation Rules
1. **No Data Bleed**: Switching to Disconnected mode immediately flushes all simulation objects from memory.
2. **Explicit Flagging**: All demo defects possess `isDemo: true` in their entity model.
3. **Visual Transparency**: When Demo Mode is active, an industrial yellow banner (`DemoModeBanner.tsx`) is rendered persistently across all dashboard views.
4. **Motor Invariance**: Propulsion controls are genuinely disabled with HTML `disabled={true}` attributes in **both** modes. Demo Mode never simulates false vehicle movement or transmits motor commands.

---

## 7. Safety Interlocks & Hardware Guardrails

To prevent hardware damage and operator hazard:
1. **Hardware Propulsion Interlock**: Directional D-pad buttons and motor sliders on the Vehicle Control page remain disabled with explicit safety messages indicating that backend firmware communication is not yet active.
2. **Emergency Stop Lock**: The emergency stop engagement interface defaults to engaged or read-only during development.
3. **No Phantom Video**: No decorative stock video or canned loops are rendered as fake live video feeds. The camera viewport displays genuine signal loss indicators until real hardware streams are established.
4. **Isolated Network Footprint**: The application does not attempt uncontrolled polling loops or unauthenticated outbound cloud requests.

