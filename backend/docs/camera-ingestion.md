# PipeBot Camera Frame Ingestion Subsystem

## 1. Subsystem Overview

The PipeBot camera frame ingestion subsystem is designed to ingest optical video frames from an inspection crawler mounted ESP32-CAM module inside PVC conduits. The subsystem supports two ingestion modalities:

1. **Continuous HTTP MJPEG Stream**: Real-time multipart/x-mixed-replace boundary stream consumed by an asynchronous background client (`CameraClient` and `MJPEGFrameReader`).
2. **Discrete Single-Frame Upload**: Multipart form file upload (`POST /api/v1/camera/frame`) supporting constrained microcontrollers, low-bandwidth networks, and automated test fixtures.

Both pathways converge into a unified frame validation, queue management, and processing pipeline before passing validated BGR NumPy arrays to the computer vision inference engine.

---

## 2. Architecture and Data Flow

```text
[ESP32-CAM Module]
       |
       +---> (HTTP MJPEG Stream: /stream) ---> [CameraClient / MJPEGFrameReader]
       |                                                    |
       +---> (POST /api/v1/camera/frame)                    v
                                               [Frame Validation Pipeline]
                                                    | (OpenCV Decoding)
                                                    v
                                            [Bounded Frame Queue]
                                           (drop-oldest backpressure)
                                                    |
                                                    v
                                        [Frame Processing Service]
                                        /           |           \
                                       v            v            v
                                 [Localization] [AI Vision] [Evidence Storage]
```

---

## 3. Frame Validation Rules

Untrusted frames received from the network are validated against defensive security boundaries before memory allocation or OpenCV processing:

1. **Byte Size Bounds**:
   - Every incoming frame buffer is checked against `CAMERA_MAX_FRAME_BYTES` (default: 1,048,576 bytes / 1 MB).
   - Frames exceeding this threshold are immediately rejected with an explicit validation error without passing to the decoder.
2. **Non-Empty Payload Check**:
   - Payloads with zero bytes are rejected as invalid.
3. **OpenCV Memory Decoding**:
   - Frames are decoded in-memory using `cv2.imdecode(buffer, cv2.IMREAD_COLOR)`.
   - Any corrupt JPEG payload, truncated header, or unparseable byte sequence returns `None` and is safely rejected.
4. **Dimension Bounds**:
   - Decoded matrices must have exactly 3 channels (BGR) and 2 spatial dimensions.
   - Width must not exceed `CAMERA_MAX_FRAME_WIDTH` (default: 1920 pixels).
   - Height must not exceed `CAMERA_MAX_FRAME_HEIGHT` (default: 1080 pixels).
   - Frames violating dimension limits are rejected to protect system memory.

---

## 4. Bounded Queue and Backpressure Handling

To prevent unbounded memory consumption and excessive latency when the server or AI inference pipeline experiences transient load spikes:

- **Bounded Queue**: Frames are enqueued into an `asyncio.Queue` with a fixed capacity defined by `CAMERA_QUEUE_SIZE` (default: 10 frames).
- **Drop-Oldest Strategy**: When the queue reaches capacity and a new frame arrives, the oldest pending frame is discarded (`queue.get_nowait()`) to make room for the latest frame.
- **Dropped Frame Accounting**: Every discarded frame increments `dropped_frames_count` on the `CameraState` singleton, ensuring full operational visibility.
- **Latency Protection**: In robotics inspection, stale frames are worthless for real-time control and obstacle avoidance; drop-oldest ensures the vision model always analyzes the freshest conduit view.

---

## 5. Camera Lifecycle and Connection State Machine

The camera connection state is tracked by the `CameraState` singleton through a 6-state finite state machine:

| State | Description |
|---|---|
| `disconnected` | Default state; no active stream reader or camera client configured. |
| `connecting` | Asynchronous worker is attempting HTTP connection to the camera stream URL. |
| `connected` | HTTP connection established and stream headers validated; awaiting first frame. |
| `streaming` | Valid optical frames are actively arriving within the expected frame interval. |
| `stale` | Connection is open, but no valid frame has been received for longer than `CAMERA_READ_TIMEOUT` (default: 5.0 seconds). |
| `error` | Connection failed, stream terminated unexpectedly, or unrecoverable network failure. |

State transitions trigger instantaneous WebSocket broadcast messages (`camera_status`) to notify connected frontend dashboards.

---

## 6. REST API Endpoints

### 6.1 Camera Status
- **Endpoint**: `GET /api/v1/camera/status`
- **Response**:
```json
{
  "camera_id": "esp32_cam_01",
  "status": "streaming",
  "stream_url": "http://192.168.4.2:81/stream",
  "stream_type": "mjpeg",
  "frames_received": 1420,
  "frames_processed": 1418,
  "frames_dropped": 2,
  "fps": 12.4,
  "last_frame_timestamp": "2026-10-30T16:50:00.120Z",
  "error_message": null
}
```

### 6.2 Start Camera Stream
- **Endpoint**: `POST /api/v1/camera/start`
- **Description**: Starts background `CameraClient` task to read stream from configured or requested URL.
- **Response**: `200 OK` with updated `CameraStatusResponse`.

### 6.3 Stop Camera Stream
- **Endpoint**: `POST /api/v1/camera/stop`
- **Description**: Signals background worker to disconnect cleanly, releases resources, and updates state to `disconnected`.
- **Response**: `200 OK` with updated `CameraStatusResponse`.

### 6.4 Single Frame Ingestion
- **Endpoint**: `POST /api/v1/camera/frame`
- **Security**: Supports optional device authentication via `X-Device-Token` header.
- **Content-Type**: `multipart/form-data` (Payload must be `image/jpeg` or `application/octet-stream`).
- **Form Fields**:
  - `file`: JPEG image file (binary, max `CAMERA_MAX_FRAME_BYTES` = 1 MB).
  - `cameraId` / `camera_id` (optional): Camera device identifier string.
  - `inspectionId` / `inspection_id` (optional): Explicit inspection session identifier.
  - `captureTimestamp` / `capture_timestamp` (optional): ISO 8601 UTC timestamp of frame capture on ESP32-CAM.
  - `uptimeSeconds` / `uptime_seconds` (optional): ESP32-CAM device uptime in seconds.
- **Response**: `FrameMetadata` schema with decoded image dimensions and UTC server receipt timestamp.

---

## 7. Configuration Settings

| Setting | Default | Description |
|---|---|---|
| `CAMERA_ID` | `esp32_cam_01` | Default hardware identifier for the optical camera module. |
| `CAMERA_STREAM_URL` | `""` | Stream URL for ESP32-CAM MJPEG endpoint (e.g. `http://192.168.4.2:81/stream`). |
| `CAMERA_STREAM_TYPE` | `mjpeg` | Protocol format for stream (`mjpeg` or `snapshot`). |
| `CAMERA_CONNECT_TIMEOUT` | `5.0` | Connection timeout in seconds. |
| `CAMERA_READ_TIMEOUT` | `5.0` | Read timeout in seconds before marking stream as `stale`. |
| `CAMERA_MAX_FRAME_BYTES` | `1048576` | Maximum allowed frame size in bytes (1 MB). |
| `CAMERA_MAX_FRAME_WIDTH` | `1920` | Maximum allowed frame width in pixels. |
| `CAMERA_MAX_FRAME_HEIGHT` | `1080` | Maximum allowed frame height in pixels. |
| `CAMERA_MAX_FPS` | `30.0` | Ingestion rate limiter ceiling. |
| `CAMERA_QUEUE_SIZE` | `10` | Bounded memory queue capacity. |

