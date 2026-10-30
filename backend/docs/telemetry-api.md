# PipeBot Telemetry Ingestion and Diagnostics API Specification

## 1. Architectural Overview

The PipeBot telemetry subsystem provides high-frequency ingestion for sensor telemetry originating from the robotic vehicle microcontrollers (ESP32-WROOM and ESP32-CAM). The ingestion layer runs in FastAPI, validates schema integrity, enforces monotonic sequence numbers, tracks boot sessions, evaluates dynamic connection health, and broadcasts typed event envelopes via WebSocket to connected operator dashboards.

Continuous high-frequency telemetry is maintained in memory for sub-millisecond query performance and low-latency distribution, avoiding database lock contention and write amplification during active pipeline inspections.

```text
+-----------------------+           HTTP POST (10-50 Hz)
|  ESP32 Microcontroller| ----------------------------------------+
+-----------------------+                                        |
                                                                  v
+-----------------------+     WebSocket Broadcast      +-------------------------+
| Operator React Client | <=========================== |  FastAPI Ingestion API  |
+-----------------------+      (/ws/telemetry)         +-------------------------+
                                                                  |
                                                                  v
                                                       +-------------------------+
                                                       | TelemetryStateService   |
                                                       | (In-Memory Singleton)   |
                                                       +-------------------------+
```

---

## 2. Authentication and Ingestion Security

Telemetry ingestion endpoints support optional token authentication controlled by the `DEVICE_INGEST_TOKEN` configuration setting:

- **Local Development / Laboratory Mode**: When `DEVICE_INGEST_TOKEN` is unset or empty, endpoints accept incoming packets without requiring authentication headers.
- **Production Mode**: When `DEVICE_INGEST_TOKEN` is defined, incoming requests must provide either:
  1. `X-Device-Token: <token>` header, or
  2. `Authorization: Bearer <token>` header.

Requests failing authentication return `HTTP 401 Unauthorized`:
```json
{
  "detail": "Invalid or missing device ingestion token."
}
```

---

## 3. Telemetry Endpoints Reference

### 3.1. Ingest Rotary Encoder Odometry
- **Route**: `POST /api/v1/telemetry/encoder`
- **Rate**: 10 to 20 Hz
- **Request Body**:
```json
{
  "deviceId": "esp32_wroom_01",
  "bootId": "8f8b5f92-5953-4b68-b7eb-d487f8f90264",
  "sequenceNumber": 142,
  "leftTicks": 3200,
  "rightTicks": 3196,
  "leftRpm": 42.5,
  "rightRpm": 42.4,
  "estimatedDistanceMeters": 4.82,
  "speedMps": 0.24,
  "direction": "forward",
  "timestamp": "2026-10-30T16:00:00.120Z"
}
```
- **Response**: `200 OK`
```json
{
  "leftTicks": 3200,
  "rightTicks": 3196,
  "leftRpm": 42.5,
  "rightRpm": 42.4,
  "estimatedDistanceMeters": 4.82,
  "speedMps": 0.24,
  "direction": "forward",
  "timestamp": "2026-10-30T16:00:00.120Z"
}
```

### 3.2. Ingest MPU6050 Inertial Metrics
- **Route**: `POST /api/v1/telemetry/imu`
- **Rate**: 20 to 50 Hz
- **Request Body**:
```json
{
  "deviceId": "esp32_wroom_01",
  "bootId": "8f8b5f92-5953-4b68-b7eb-d487f8f90264",
  "sequenceNumber": 143,
  "accelX": 0.04,
  "accelY": -0.02,
  "accelZ": 9.81,
  "gyroX": 0.01,
  "gyroY": -0.01,
  "gyroZ": 0.0,
  "pitchDeg": 3.2,
  "rollDeg": -1.4,
  "yawDeg": 182.0,
  "temperatureC": 34.8,
  "timestamp": "2026-10-30T16:00:00.140Z"
}
```
- **Response**: `200 OK`
```json
{
  "accelX": 0.04,
  "accelY": -0.02,
  "accelZ": 9.81,
  "gyroX": 0.01,
  "gyroY": -0.01,
  "gyroZ": 0.0,
  "pitchDegrees": 3.2,
  "rollDegrees": -1.4,
  "yawDegrees": 182.0,
  "temperatureC": 34.8,
  "timestamp": "2026-10-30T16:00:00.140Z"
}
```

### 3.3. Ingest Vehicle Health and Safety State
- **Route**: `POST /api/v1/telemetry/vehicle/status`
- **Rate**: 2 to 5 Hz
- **Safety Boundary**: Read-only status telemetry. No actuator drive commands or motor propulsion endpoints are exposed on this API.
- **Request Body**:
```json
{
  "deviceId": "esp32_wroom_01",
  "bootId": "8f8b5f92-5953-4b68-b7eb-d487f8f90264",
  "sequenceNumber": 144,
  "controllerState": "connected",
  "motorDriverState": "connected",
  "leftMotorState": "forward",
  "rightMotorState": "forward",
  "emergencyStopEngaged": false,
  "commandAckState": "acknowledged",
  "batteryVoltage": 12.35,
  "batteryPercent": 85.0,
  "currentDrawAmperes": 1.45,
  "operatingState": "normal"
}
```
- **Response**: `200 OK`
```json
{
  "controllerState": "connected",
  "motorDriverState": "connected",
  "leftMotorState": "forward",
  "rightMotorState": "forward",
  "emergencyStopEngaged": false,
  "commandAckState": "acknowledged",
  "batteryVoltage": 12.35,
  "batteryPercent": 85.0,
  "currentDrawAmperes": 1.45,
  "lastCommandTimestamp": "2026-10-30T16:00:00.160Z",
  "operatingState": "normal",
  "timestamp": "2026-10-30T16:00:00.160Z"
}
```

### 3.4. Ingest Embedded Device Heartbeat
- **Route**: `POST /api/v1/telemetry/heartbeat`
- **Rate**: 1 Hz (once per second)
- **Request Body**:
```json
{
  "deviceId": "esp32_wroom_01",
  "deviceType": "ESP32_WROOM",
  "bootId": "8f8b5f92-5953-4b68-b7eb-d487f8f90264",
  "sequenceNumber": 145,
  "uptimeSeconds": 3482.0,
  "wifiRssiDbm": -62,
  "freeHeapBytes": 182300,
  "batteryVoltage": 12.34,
  "firmwareVersion": "v1.2.0",
  "status": "ok"
}
```
- **Response**: `200 OK`
```json
{
  "deviceId": "esp32_wroom_01",
  "deviceType": "ESP32_WROOM",
  "connectionStatus": "connected",
  "bootId": "8f8b5f92-5953-4b68-b7eb-d487f8f90264",
  "lastSequenceNumber": 145,
  "lastSeenSecondsAgo": 0.0,
  "uptimeSeconds": 3482.0,
  "wifiRssiDbm": -62,
  "firmwareVersion": "v1.2.0",
  "rebootCount": 0,
  "duplicatePacketsCount": 0,
  "totalPacketsCount": 145
}
```

### 3.5. Get Latest Consolidated Telemetry Snapshot
- **Route**: `GET /api/v1/telemetry/latest`
- **Description**: Returns consolidated encoder, IMU, and vehicle readings. If hardware is offline, returns null measurement fields without fabricated readings.
- **Response**: `200 OK`
```json
{
  "encoder": {
    "leftTicks": 3200,
    "rightTicks": 3196,
    "leftRpm": 42.5,
    "rightRpm": 42.4,
    "estimatedDistanceMeters": 4.82,
    "speedMps": 0.24,
    "direction": "forward",
    "timestamp": "2026-10-30T16:00:00.120Z"
  },
  "imu": {
    "accelX": 0.04,
    "accelY": -0.02,
    "accelZ": 9.81,
    "gyroX": 0.01,
    "gyroY": -0.01,
    "gyroZ": 0.0,
    "pitchDegrees": 3.2,
    "rollDegrees": -1.4,
    "yawDegrees": 182.0,
    "temperatureC": 34.8,
    "timestamp": "2026-10-30T16:00:00.140Z"
  },
  "vehicle": {
    "controllerState": "connected",
    "motorDriverState": "connected",
    "leftMotorState": "forward",
    "rightMotorState": "forward",
    "emergencyStopEngaged": false,
    "commandAckState": "acknowledged",
    "batteryVoltage": 12.35,
    "batteryPercent": 85.0,
    "currentDrawAmperes": 1.45,
    "lastCommandTimestamp": "2026-10-30T16:00:00.160Z",
    "operatingState": "normal",
    "timestamp": "2026-10-30T16:00:00.160Z"
  },
  "timestamp": "2026-10-30T16:00:00.200Z"
}
```

### 3.6. Get Hardware Link Diagnostics
- **Route**: `GET /api/v1/telemetry/status`
- **Description**: Evaluates overall connectivity and per-device link health.
- **Response**: `200 OK`
```json
{
  "overallStatus": "connected",
  "devices": {
    "esp32_wroom_01": {
      "deviceId": "esp32_wroom_01",
      "deviceType": "ESP32_WROOM",
      "connectionStatus": "connected",
      "bootId": "8f8b5f92-5953-4b68-b7eb-d487f8f90264",
      "lastSequenceNumber": 145,
      "lastSeenSecondsAgo": 0.25,
      "uptimeSeconds": 3482.0,
      "wifiRssiDbm": -62,
      "firmwareVersion": "v1.2.0",
      "rebootCount": 0,
      "duplicatePacketsCount": 0,
      "totalPacketsCount": 145
    }
  },
  "activeWsConnections": 2,
  "timestamp": "2026-10-30T16:00:00.250Z"
}
```

---

## 4. Connection State Evaluation Rules

The connection state for each microcontroller is dynamically evaluated using elapsed time since the last valid packet:

1. **Connected** (`elapsed <= 3.0s`): Packets arriving within `TELEMETRY_STALE_TIMEOUT_SECONDS`.
2. **Stale** (`3.0s < elapsed <= 5.0s`): Inactivity exceeded stale threshold but remains under `HEARTBEAT_TIMEOUT_SECONDS`.
3. **Disconnected** (`elapsed > 5.0s`): No packets received within heartbeat threshold, or no packets ever received.

The overall hardware link state reflects:
- `connected` if any microcontroller is active and connected.
- `stale` if no device is connected, but at least one device is stale.
- `disconnected` when all microcontrollers are offline.

