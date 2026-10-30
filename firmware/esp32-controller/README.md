# ESP32-WROOM-32 Motion & Telemetry Controller

This subsystem manages the robotic crawler chassis mobility, rotary wheel encoder odometry, MPU6050 inertial measurement, and vehicle safety interlocks.

## 1. Hardware Specifications

- Microcontroller: ESP32-WROOM-32D / ESP32-WROOM-32U
- Core: Dual-core Xtensa 32-bit LX6 microprocessor @ 240 MHz
- Flash Memory: 4 MB SPI Flash
- SRAM: 520 KB
- Clock Synchronization: Hardware timer interrupts for quadrature encoder pulse decoding
- Supply Voltage: 3.3V Logic (Powered via onboard 5V to 3.3V LDO regulator from 2S/3S LiPo battery)

## 2. GPIO Pinout Allocation Table

| Peripheral | Signal Name | ESP32 GPIO | Pin Type | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Left Encoder** | Channel A (Phase A) | `GPIO 34` | Input only | Hardware interrupt on rising/falling edge |
| **Left Encoder** | Channel B (Phase B) | `GPIO 35` | Input only | Quadrature direction discriminator |
| **Right Encoder** | Channel A (Phase A) | `GPIO 36` (VP) | Input only | Hardware interrupt on rising/falling edge |
| **Right Encoder** | Channel B (Phase B) | `GPIO 39` (VN) | Input only | Quadrature direction discriminator |
| **MPU6050 IMU** | I2C SDA | `GPIO 21` | Bidirectional | External 4.7k ohm pull-up to 3.3V |
| **MPU6050 IMU** | I2C SCL | `GPIO 22` | Output | 400 kHz Fast-Mode I2C clock |
| **Motor Driver** | Left Motor PWM | `GPIO 16` | Output | LEDC PWM channel 0 (20 kHz frequency) |
| **Motor Driver** | Left Motor DIR | `GPIO 17` | Output | H-Bridge direction control |
| **Motor Driver** | Right Motor PWM | `GPIO 18` | Output | LEDC PWM channel 1 (20 kHz frequency) |
| **Motor Driver** | Right Motor DIR | `GPIO 19` | Output | H-Bridge direction control |
| **Safety E-Stop** | Hardware Interlock | `GPIO 23` | Input | Active-low with internal pull-up |
| **Status Indicator** | Built-in LED | `GPIO 2` | Output | Heartbeat and Wi-Fi link blink codes |

## 3. Mathematical Odometry Integration

Linear conduit traversal is accumulated using wheel encoder ticks:

1. Wheel Circumference: `C = pi * wheel_diameter_meters` (Default diameter = 0.065 m, C = 0.2042 m)
2. Encoder Resolution: `PPR = 360` pulses per wheel revolution (or gear ratio equivalent)
3. Distance Per Pulse: `K = C / PPR = 0.2042 / 360 = 0.000567 m/pulse`
4. Left Wheel Traversal: `D_left = ticks_left * K`
5. Right Wheel Traversal: `D_right = ticks_right * K`
6. Center Chassis Traversal: `D_center = (D_left + D_right) / 2.0`

## 4. Telemetry Telemetry Dispatch Formats

The controller periodically posts structured JSON packets to the FastAPI backend:

### Encoder Ingestion (`POST /api/v1/telemetry/encoder`):
```json
{
  "device_id": "ESP32_WROOM_CRAWLER_01",
  "boot_id": "BOOT-A4F1B8-001",
  "sequence_number": 421,
  "inspection_id": 1,
  "left_ticks": 4120,
  "right_ticks": 4118,
  "left_rpm": 42.5,
  "right_rpm": 42.3,
  "speed_mps": 0.14,
  "direction": "forward"
}
```

### IMU Ingestion (`POST /api/v1/telemetry/imu`):
```json
{
  "device_id": "ESP32_WROOM_CRAWLER_01",
  "boot_id": "BOOT-A4F1B8-001",
  "sequence_number": 422,
  "inspection_id": 1,
  "accel_x": 0.02,
  "accel_y": -0.01,
  "accel_z": 0.98,
  "gyro_x": 0.1,
  "gyro_y": -0.2,
  "gyro_z": 0.0,
  "pitch_degrees": 1.8,
  "roll_degrees": -0.4,
  "yaw_degrees": 0.0,
  "temperature_c": 28.5
}
```
