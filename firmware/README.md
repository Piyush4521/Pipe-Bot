# PipeBot Embedded Hardware & Firmware Architecture

This directory contains hardware specifications, pinout documentation, schematic references, and firmware architecture for the PipeBot crawler system.

## 1. Dual-Microcontroller Architecture

PipeBot splits robotic responsibilities between two dedicated microcontrollers to isolate high-bandwidth video streaming from mission-critical motion control and odometry calculation:

```text
+-----------------------------------------------------------------+
|                        PipeBot Crawler                          |
|                                                                 |
|   +--------------------------+     +--------------------------+ |
|   |      ESP32-WROOM-32      |     |     AI-Thinker ESP32-CAM | |
|   | (Motion & Telemetry)     |     | (Optical Capture)        | |
|   +------------+-------------+     +------------+-------------+ |
|                |                                |               |
|      I2C / GPIO Encoders               DVP Camera Interface     |
|                |                                |               |
|   +------------v-------------+     +------------v-------------+ |
|   | Dual Rotary Encoders     |     | OV2640 Image Sensor      | |
|   | MPU6050 6-Axis IMU       |     | Internal LED Flash       | |
|   | L298N/DRV8833 Motor Drv  |     | MJPEG Stream @ 15-25 FPS | |
|   +--------------------------+     +--------------------------+ |
+-----------------------------------------------------------------+
                         |                          |
               HTTP JSON Telemetry             HTTP MJPEG Video
             POST /api/v1/telemetry              GET /stream
                         |                          |
                         +------------+-------------+
                                      |
                           Wi-Fi / Ethernet Network
                                      |
                         +------------v-------------+
                         |      FastAPI Backend     |
                         |   (127.0.0.1:8000)       |
                         +--------------------------+
```

## 2. Subsystem Division

### 1. Motion & Telemetry Controller (`firmware/esp32-controller/`)
- Microcontroller: ESP32-WROOM-32 (Dual-core Xtensa LX6 @ 240 MHz)
- Responsibilities:
  - Quadrature pulse counting from Left and Right magnetic wheel encoders
  - 6-axis attitude estimation (pitch, roll, yaw) via MPU6050 over I2C
  - Pulse-Width Modulation (PWM) motor speed control and directional H-bridge actuation
  - Hardware emergency stop (E-stop) fail-safe monitoring
  - Periodic HTTP telemetry broadcast to FastAPI backend (`/api/v1/telemetry/encoder`, `/api/v1/telemetry/imu`, `/api/v1/telemetry/status`)

### 2. Optical Inspection Camera (`firmware/esp32-camera/`)
- Microcontroller: AI-Thinker ESP32-CAM with OV2640 2-Megapixel CMOS sensor
- Responsibilities:
  - Continuous optical capture at 640x480 (VGA) resolution
  - Onboard hardware JPEG compression
  - HTTP multipart/x-mixed-replace MJPEG streaming server at `http://<ip>/stream`
  - High-intensity forward-facing illumination LED control for conduit inspection

## 3. Communication Protocols & Network Topologies

1. Access Point Mode (Field Setup):
   - ESP32-WROOM acts as an independent Wi-Fi Access Point (`PipeBot-Field-AP`).
   - ESP32-CAM and operator laptop connect directly to the vehicle AP.
   - Ideal for underground inspection sites without commercial Wi-Fi coverage.

2. Infrastructure Mode (Lab / Station Setup):
   - Both ESP32 nodes connect to a local base station router with static IP reservations.
   - Laptop connects to the same network running the FastAPI backend server.

3. Authentication & Security:
   - All telemetry and frame upload requests carry a pre-shared device token (`X-Device-Token`) validated by the backend.
