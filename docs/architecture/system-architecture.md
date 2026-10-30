# PipeBot System Architecture Blueprint

This document defines the end-to-end system architecture of PipeBot, an AI-powered robotic inspection crawler for municipal and industrial PVC pipelines.

## 1. System Mission & Context

Traditional sewer and drainage pipeline inspection relies on bulky push-rod cameras or tractor crawlers with manual video review. PipeBot introduces an agile, autonomous robotic crawler equipped with dual wheel odometry, inertial tilt measurement, wireless video streaming, and real-time YOLOv8 neural network inference to classify pipeline anomalies instantly.

Target conduit profiles:
- Conduit Material: Polyvinyl Chloride (PVC), High-Density Polyethylene (HDPE), Concrete
- Diameter Range: 150 mm to 300 mm internal diameter
- Operational Environment: Hazardous drainage conduits with low light and wet surfaces

## 2. High-Level Multi-Tier Topology

```text
+-----------------------------------------------------------------------------------+
|                              1. ROBOTIC HARDWARE TIER                             |
|                                                                                   |
|  +-------------------------------------+   +------------------------------------+ |
|  |     ESP32-WROOM-32 Microcontroller  |   |    AI-Thinker ESP32-CAM Node       | |
|  |  - Dual Rotary Magnetic Encoders    |   |  - OmniVision OV2640 Image Sensor  | |
|  |  - MPU6050 6-Axis Accelerometer/Gyro|   |  - Hardware JPEG Compression       | |
|  |  - L298N/DRV8833 Motor H-Bridge     |   |  - High-Intensity White LED Flash  | |
|  |  - Hardware Emergency Stop Relay    |   |  - HTTP MJPEG Video Server /stream | |
|  +------------------+------------------+   +------------------+-----------------+ |
+---------------------|-----------------------------------------|-------------------+
                      |                                         |
           HTTP POST Telemetry JSON                  HTTP GET MJPEG Stream
        /api/v1/telemetry/{encoder,imu}                   Port 80 /stream
                      |                                         |
+---------------------v-----------------------------------------v-------------------+
|                              2. PROCESSING BACKEND TIER                           |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   |                       FastAPI Asynchronous Gateway                        |   |
|   |                    (Python 3.10, Uvicorn, REST & WebSocket)              |   |
|   +---------------------+-------------------------------+---------------------+   |
|                         |                               |                         |
|   +---------------------v-------+             +---------v---------------------+   |
|   |   Camera Ingestion Client   |             |   Telemetry Ingestion Service |   |
|   |   (OpenCV Frame Decoding)   |             |   (Tick Math, Drift Filter)   |   |
|   +---------------------+-------+             +---------+---------------------+   |
|                         |                               |                         |
|   +---------------------v-------+                       |                         |
|   |  Ultralytics YOLOv8 Engine  |                       |                         |
|   |  (4 Canonical Defect Classes)                       |                         |
|   +---------------------+-------+                       |                         |
|                         |                               |                         |
|   +---------------------v-------------------------------v---------------------+   |
|   |               SQLAlchemy 2.0 ORM & Alembic Migration Engine               |   |
|   |              - Active: SQLite 3 with Write-Ahead Logging (WAL)            |   |
|   |              - Scalable Target: PostgreSQL 16 Relational Engine           |   |
|   +---------------------+-------------------------------+---------------------+   |
|                         |                               |                         |
+-------------------------|-------------------------------|-------------------------+
                          |                               |
                Duplex WebSocket Stream               REST API Responses
                 ws://127.0.0.1:8000/ws              http://127.0.0.1:8000/api
                          |                               |
+-------------------------v-------------------------------v-------------------------+
|                              3. OPERATOR INTERFACE TIER                           |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   |            React 18 Single-Page Application (TypeScript, Vite)            |   |
|   |  - Light Industrial Bento-Grid / Neo-Brutalist Engineering Design         |   |
|   |  - Live Optical Viewport with Anomaly Bounding Overlays                   |   |
|   |  - Real-Time Encoder Odometry & Pitch/Roll Gyro Orientation Gauges        |   |
|   |  - Longitudinal Pipe Conduit Defect Distance Timeline                     |   |
|   |  - Defect Evidence Drawer with Operator Verification Workflow             |   |
|   |  - Dual State Isolation: Verified Live Backend vs. Isolated Demo Mode     |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
```

## 3. Core Data & Control Flows

### 1. Telemetry Ingestion Flow:
1. ESP32-WROOM counts quadrature encoder pulses on hardware timer interrupts.
2. Every 100 ms, odometry and MPU6050 readings are packaged into a JSON payload and posted to `/api/v1/telemetry/encoder` and `/api/v1/telemetry/imu`.
3. The backend validates payloads with Pydantic, evaluates crawler speed, updates the in-memory telemetry state, and commits rows to the database.
4. The backend broadcasts a `telemetry_encoder` and `telemetry_imu` envelope across all active WebSocket connections.
5. The React dashboard updates live pulse counts, traversal distance, and tilt angles without polling.

### 2. Video Capture & Defect Detection Flow:
1. ESP32-CAM streams 640x480 MJPEG video over HTTP.
2. The FastAPI `CameraClient` background worker ingests the multipart stream, extracting raw JPEG buffers and decoding them with OpenCV into NumPy arrays.
3. Every sampled frame is passed to the Ultralytics YOLOv8 model (`best.pt`).
4. If a defect (Deformation, Misalignment, Obstacle, Rupture) exceeds the confidence threshold (default 0.25):
   - The bounding box coordinates and classification are normalized.
   - The snapshot frame is saved to `media/inspections/`.
   - A `defects` record is committed to the relational database.
   - A `defect_detected` event is broadcast over WebSocket to the operator console.
5. The operator console immediately displays an alert pin on the longitudinal pipe timeline and adds the record to the Defect Registry for verification.

### 3. Mission Session Control Flow:
1. Operator opens "New Inspection Session" modal on the dashboard.
2. A `POST /api/v1/inspections` request initializes the mission with conduit metadata (ID, diameter, material, technician).
3. The inspection starts in `created` status and transitions to `running`.
4. As the crawler moves, all defects and telemetry samples carry the foreign key referencing this active inspection.
5. When the mission completes, final encoder distance is recorded and the session transitions to `completed`.
