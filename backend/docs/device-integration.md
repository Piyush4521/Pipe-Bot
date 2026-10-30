# PipeBot Embedded Device Integration Guide

## 1. Subsystem Architecture and Device Roles

The PipeBot robotic crawler hardware consists of two dedicated Espressif microcontroller nodes connected over local Wi-Fi to the FastAPI backend host:

1. **ESP32-WROOM Node** (Core Vehicle Telemetry):
   - Interfaces with optical rotary wheel encoders (left and right channels).
   - Interfaces with MPU6050 6-axis inertial measurement unit over I2C.
   - Monitors battery bus voltage via precision resistor divider and ADC.
   - Reads motor driver bridge fault flags and current sensing shunt.
   - Dispatches HTTP POST telemetry packets and 1 Hz heartbeats to FastAPI.
2. **ESP32-CAM Node** (Optical Inspection Feed):
   - Captures optical frames from the OV2640 camera sensor.
   - Streams MJPEG video stream directly to operators or backend on port 81.
   - Transmits diagnostic heartbeats (`deviceType: "ESP32_CAM"`) to the backend.

---

## 2. Packet Formats and Transmission Frequencies

| Packet Type | Endpoint | Recommended Rate | Description |
|:---|:---|:---|:---|
| Rotary Encoder | `POST /api/v1/telemetry/encoder` | 10 to 20 Hz | Wheel pulse counts, linear speed, calculated distance |
| IMU Metrics | `POST /api/v1/telemetry/imu` | 20 to 50 Hz | Pitch angle, roll angle, 3-axis acceleration |
| Vehicle Status | `POST /api/v1/telemetry/vehicle/status` | 2 to 5 Hz | Battery voltage, e-stop state, motor bridge health |
| Device Heartbeat | `POST /api/v1/telemetry/heartbeat` | 1 Hz | Uptime, Wi-Fi RSSI, free heap memory, firmware version |

---

## 3. Sequence Tracking and Reboot Detection Rules

To guarantee telemetry ordering and detect power cycle interruptions:

1. **Boot Session Identifier (`bootId`)**:
   - On microcontroller startup, generate a unique session identifier (e.g., UUID v4 string or cryptographic random hex string).
   - Keep this identifier constant in all packets for the duration of that boot session.
   - When the backend observes a new `bootId` from a known `deviceId`, it flags a device reboot, increments `rebootCount`, and resets the expected sequence number.
2. **Monotonic Sequence Numbers (`sequenceNumber`)**:
   - Maintain a 32-bit unsigned integer counter initialized to 0 on device startup.
   - Increment `sequenceNumber` by 1 for every packet sent from that device.
   - If packet drops or duplicates occur over Wi-Fi, the backend logs duplicate or out-of-order occurrences without dropping valid telemetry updates.

---

## 4. Inactivity and Reconnection Policies

The backend continuously monitors elapsed time since the last packet received:

- **Active State** (`< 3.0 seconds`): Device is marked `connected`.
- **Stale State** (`3.0 to 5.0 seconds`): Network jitter or packet loss suspected. Device is marked `stale`.
- **Offline State** (`> 5.0 seconds`): Hardware link severed. Device is marked `disconnected`.

Microcontrollers should handle Wi-Fi disconnections with automatic reconnection loops (exponential backoff between 500ms and 5000ms).

---

## 5. Firmware Implementation Reference (C++ / Arduino / ESP-IDF)

Below is a reference implementation using the Arduino HTTPClient library for ESP32:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* BACKEND_URL = "http://192.168.1.100:8000/api/v1/telemetry";
const char* DEVICE_TOKEN = ""; // Populate if DEVICE_INGEST_TOKEN is configured
const char* DEVICE_ID = "esp32_wroom_01";
String bootId = "";
uint32_t sequenceNumber = 0;

void setup() {
    Serial.begin(115200);
    // Generate unique boot session identifier
    bootId = String(ESP.getEfuseMac(), HEX) + "-" + String(millis());
}

void sendHeartbeat() {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    http.begin(String(BACKEND_URL) + "/heartbeat");
    http.addHeader("Content-Type", "application/json");
    if (strlen(DEVICE_TOKEN) > 0) {
        http.addHeader("X-Device-Token", DEVICE_TOKEN);
    }

    StaticJsonDocument<256> doc;
    doc["deviceId"] = DEVICE_ID;
    doc["deviceType"] = "ESP32_WROOM";
    doc["bootId"] = bootId;
    doc["sequenceNumber"] = sequenceNumber++;
    doc["uptimeSeconds"] = millis() / 1000.0;
    doc["wifiRssiDbm"] = WiFi.RSSI();
    doc["freeHeapBytes"] = ESP.getFreeHeap();
    doc["batteryVoltage"] = 12.4;
    doc["firmwareVersion"] = "v1.2.0";
    doc["status"] = "ok";

    String requestBody;
    serializeJson(doc, requestBody);
    int httpResponseCode = http.POST(requestBody);
    http.end();
}
```

