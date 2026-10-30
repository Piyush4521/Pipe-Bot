# PipeBot Operator WebSocket Communication Protocol Specification

## 1. Overview and Endpoint Routing

The PipeBot backend provides a duplex WebSocket streaming endpoint for low-latency transmission of vehicle telemetry, sensor streams, system health, and defect events to connected operator dashboards.

### Supported Connection URLs

To maintain 100% compatibility across frontend environments, configuration templates, and API versioning conventions, three route aliases are mounted to the identical WebSocket handler:

1. `ws://127.0.0.1:8000/api/v1/ws/telemetry` (Standard versioned API route)
2. `ws://127.0.0.1:8000/ws/telemetry` (Frontend service contract specified in docs/frontend-integration.md)
3. `ws://127.0.0.1:8000/ws` (Vite frontend default configured in .env.example)

---

## 2. Typed Envelope Format

All WebSocket messages flowing between the backend and connected operator clients adhere strictly to the typed envelope contract:

```json
{
  "type": "<event_type>",
  "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
  "payload": { ... }
}
```

### Event Types Summary

| Event Type | Direction | Description |
|:---|:---|:---|
| `system_status` | Server to Client | Full subsystem connectivity link matrix (backend, database, hardware, camera, AI) |
| `telemetry_encoder` | Server to Client | Real-time rotary encoder odometry (ticks, distance, velocity, RPM) |
| `telemetry_imu` | Server to Client | Real-time MPU6050 6-axis inertial motion and angular inclination |
| `vehicle_status` | Server to Client | Battery bus voltage, current draw, e-stop flag, and motor driver state |
| `ping` | Client to Server | Client keepalive heart pulse |
| `pong` | Server to Client | Server keepalive acknowledgement |
| `request_snapshot` | Client to Server | Explicit client request for full telemetry snapshot |
| `telemetry_snapshot` | Server to Client | Consolidated snapshot containing encoder, IMU, and vehicle data |

---

## 3. Initial Synchronization on Connect

When an operator frontend establishes a WebSocket connection, the backend automatically performs initial synchronization by transmitting four discrete event envelopes in sequence:

1. **`system_status`**: Current subsystem connectivity matrix.
2. **`telemetry_encoder`**: Latest recorded rotary encoder measurements (or null fields if hardware is offline).
3. **`telemetry_imu`**: Latest recorded inertial measurements (or null fields if offline).
4. **`vehicle_status`**: Latest vehicle health and power state (or disconnected state if offline).

This immediate broadcast guarantees that the operator dashboard does not display uninitialized or stale states while waiting for the next periodic packet.

---

## 4. Message Payloads

### 4.1. System Status Envelope
```json
{
  "type": "system_status",
  "timestamp": "2026-10-30T16:05:00.100Z",
  "payload": {
    "backend": "connected",
    "database": "connected",
    "hardware": "connected",
    "camera": "disconnected",
    "aiProcessing": "not_initialized",
    "lastHeartbeatTimestamp": "2026-10-30T16:05:00.080Z",
    "subsystems": {
      "backend": { "state": "connected", "message": "FastAPI core service active" },
      "database": { "state": "connected", "message": "SQLite operational" },
      "esp32_wroom": { "state": "connected", "message": "Microcontroller telemetry active" },
      "esp32_cam": { "state": "disconnected", "message": "Camera hardware link disconnected" },
      "camera": { "state": "disconnected", "message": "Video ingestion stream disconnected" },
      "ai_processing": { "state": "not_initialized", "message": "YOLO neural network vision pipeline not loaded in Stage 3" }
    }
  }
}
```

### 4.2. Rotary Encoder Envelope
```json
{
  "type": "telemetry_encoder",
  "timestamp": "2026-10-30T16:05:00.120Z",
  "payload": {
    "leftTicks": 4200,
    "rightTicks": 4192,
    "leftRpm": 45.0,
    "rightRpm": 44.8,
    "estimatedDistanceMeters": 6.32,
    "speedMps": 0.23,
    "direction": "forward",
    "timestamp": "2026-10-30T16:05:00.115Z"
  }
}
```

### 4.3. Inertial Measurement Envelope
```json
{
  "type": "telemetry_imu",
  "timestamp": "2026-10-30T16:05:00.140Z",
  "payload": {
    "accelX": 0.02,
    "accelY": -0.01,
    "accelZ": 9.82,
    "gyroX": 0.0,
    "gyroY": 0.0,
    "gyroZ": 0.0,
    "pitchDegrees": 2.8,
    "rollDegrees": -0.9,
    "yawDegrees": 184.2,
    "temperatureC": 35.1,
    "timestamp": "2026-10-30T16:05:00.135Z"
  }
}
```

### 4.4. Vehicle Health and Safety Envelope
```json
{
  "type": "vehicle_status",
  "timestamp": "2026-10-30T16:05:00.160Z",
  "payload": {
    "controllerState": "connected",
    "motorDriverState": "connected",
    "leftMotorState": "forward",
    "rightMotorState": "forward",
    "emergencyStopEngaged": false,
    "commandAckState": "acknowledged",
    "batteryVoltage": 12.38,
    "batteryPercent": 86.0,
    "currentDrawAmperes": 1.32,
    "lastCommandTimestamp": "2026-10-30T16:05:00.150Z",
    "operatingState": "normal",
    "timestamp": "2026-10-30T16:05:00.150Z"
  }
}
```

### 4.5. Keepalive Ping / Pong
Client sends:
```json
{ "type": "ping" }
```
Server responds:
```json
{
  "type": "pong",
  "timestamp": "2026-10-30T16:05:00.180Z",
  "payload": { "status": "active" }
}
```

---

## 5. Capacity Limits and Connection Lifecycle

1. **Connection Ceiling (`WS_MAX_CONNECTIONS`)**: The WebSocket manager tracks all active connections. When the number of active clients reaches `WS_MAX_CONNECTIONS` (default: 50), new connection requests are rejected immediately with close code `1013 Try Again Later`.
2. **Dead Connection Pruning**: When broadcasting events, if any individual client socket fails to deliver, the dead connection is safely discarded from the active registry without halting delivery to other operators.
3. **Graceful Server Shutdown**: During FastAPI application lifespan shutdown, all active WebSocket connections are cleanly closed with close code `1001 Going Away` and reason `"Server shutting down."`.

