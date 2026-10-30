# AI-Thinker ESP32-CAM Optical Capture Subsystem

This subsystem manages the onboard optical camera, forward conduit illumination, and video streaming for PipeBot.

## 1. Hardware Specifications

- Module: AI-Thinker ESP32-CAM
- Image Sensor: OmniVision OV2640 (2-Megapixel Color CMOS Sensor)
- Field of View (FOV): 68 degrees (or wide-angle 120-degree lens option)
- Onboard PSRAM: 4 MB External SPI Pseudo-SRAM (Essential for high-resolution double-buffered frame capture)
- Illumination: Onboard high-intensity white flash LED (`GPIO 4`) with PWM dimming control
- Supply Voltage: 5.0V regulated input (Current draw spikes up to 310 mA during Wi-Fi transmission with flash LED enabled)

## 2. Sensor Settings & Video Stream Profile

| Parameter | Selected Value | Justification |
| :--- | :--- | :--- |
| **Pixel Format** | `PIXFORMAT_JPEG` | Hardware-compressed frames conserve ESP32 heap and Wi-Fi bandwidth |
| **Frame Size** | `FRAMESIZE_VGA` (640 x 480) | Standard input dimension for YOLOv8 neural network inference |
| **JPEG Quality** | `10` | High image clarity while keeping frame payloads under 45 KB |
| **Frame Buffers** | `2` (`fb_count=2`) | Ping-pong double buffering in external PSRAM for tear-free streaming |
| **Target Frame Rate** | `15 - 25 FPS` | Balanced between optical smoothness and local inference throughput |

## 3. Streaming HTTP Server Architecture

The ESP32-CAM firmware runs an asynchronous HTTP server listening on port 80:

1. MJPEG Video Stream:
   - Endpoint: `GET /stream`
   - Content-Type: `multipart/x-mixed-replace; boundary=123456789000000000000987654321`
   - Consumed continuously by the FastAPI backend camera worker (`backend/app/camera/camera_client.py`).

2. Still Snapshot Capture:
   - Endpoint: `GET /capture`
   - Content-Type: `image/jpeg`
   - Single-frame diagnostic image retrieval.

3. Illumination Brightness Control:
   - Endpoint: `GET /control?var=led_intensity&val=<0-255>`
   - Adjusts LED brightness using 5 kHz PWM on `GPIO 4`.

## 4. Optical Frame Pipeline Flow

```text
[OV2640 Sensor]
       | (DVP 8-bit Parallel Bus)
[ESP32 DMA Controller] -> [4MB PSRAM Buffer]
                                | (JPEG Compression)
                       [HTTP MJPEG Server /stream]
                                |
                     (Wi-Fi 802.11 b/g/n)
                                |
             [FastAPI Backend: CameraClient Worker]
                                |
         [OpenCV Decoded BGR Frame: 640x480x3 uint8]
                                |
            [Ultralytics YOLOv8 Defect Detection Head]
```
