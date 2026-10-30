# PipeBot Spatial Defect Localization and Odometry Correlation

## 1. Physical Foundations and Spatial Problem Definition

In robotic pipeline inspection, accurately localizing structural defects along the conduit axis is critical for remediation planning. A common pitfall in pipeline inspection systems is associating the defect position with the server's CPU timestamp at the moment neural network inference finishes.

In real-world operations, this approach is physically invalid:
1. **Network Latency and Jitter**: Wi-Fi packets transmitted through PVC conduits or over tether cables experience variable transmission delays (10 ms to 500+ ms).
2. **Buffer Queuing**: Frames wait in network socket buffers and bounded application queues (`CAMERA_QUEUE_SIZE`).
3. **Inference Latency**: Neural network execution on edge or server GPUs introduces variable inference delays (15 ms to 80+ ms).

If a crawler moves at a nominal speed of 0.15 m/s, an uncorrected time delay of 600 ms results in a spatial localization error of:

$$\Delta s = v \cdot \Delta t = 0.15 \text{ m/s} \times 0.6 \text{ s} = 0.09 \text{ m} \ (9.0 \text{ cm})$$

Under stop-and-go inspection or speed surges, the localization error can exceed 25 cm, placing excavation and trenchless repair crews at incorrect pipe coordinates.

---

## 2. Distinction Between Capture and Inference Timestamps

PipeBot strictly isolates two distinct temporal domains across all data contracts and database models:

| Field | Temporal Origin | Purpose | Physical Guarantee |
|---|---|---|---|
| `capture_timestamp` | ESP32-CAM module | Optical image acquisition | Represents the physical instant photons entered the camera sensor inside the conduit. |
| `inference_timestamp` | Backend server | Neural network execution | Represents the instant AI detection finished; purely an audit timestamp. Never used for spatial correlation. |

---

## 3. The Spatial Correlation Engine (TimestampAssociator)

Spatial localization is performed by the `TimestampAssociator` engine (`app/localization/timestamp_associator.py`) which correlates optical capture timestamps with rotary encoder odometry telemetry:

```text
[ESP32-CAM]                        [ESP32-Chassis]
     |                                    |
(capture_timestamp)              (encoder telemetry)
     |                                    |
     v                                    v
[Frame Validation]             [Telemetry Ring Buffer]
     |                                    |
     +--------------> [TimestampAssociator] <-----+
                             |
             +---------------+---------------+
             |                               |
       (Within Window)                 (Outside Window / Missing)
             v                               v
   Interpolated Distance         estimated_distance_meters = None
   localization_status="ok"      localization_status="unavailable"
```

### 3.1 Odometry Ring Buffer
The `TelemetryState` singleton maintains an in-memory chronological ring buffer of recent encoder measurements (up to 1,000 samples, covering at least 100 seconds of motion history).

### 3.2 Correlation Policy and Unverified Clock Synchronization
In physical reality, the ESP32-CAM and ESP32-WROOM-32 are separate microcontrollers operating on distinct hardware crystal oscillators without a synchronized shutter clock protocol.
1. The server receipt time or inference completion time must never be used as physical location time.
2. Because no verified hardware clock synchronization mechanism exists between the camera module and chassis motion controller, physical localization is strictly disabled by default (`allow_unverified_sync=False`).
3. Detections receive `estimated_distance_meters = None` and `localization_status = "unavailable"`.
4. The explicit explanatory reason `unverified_clock_synchronization` is assigned and broadcast via WebSockets.
5. Raw frame capture timestamps are preserved unmodified for future synchronization analysis once hardware shutter synchronization firmware is validated.

---

## 4. The Non-Extrapolation Guarantee

PipeBot adheres to a strict engineering policy: **Never extrapolate or fabricate conduit distance.**

If verified clock synchronization or valid telemetry is not available:
- The system never estimates position by dead reckoning, constant-velocity assumption, server arrival proximity, or inference latency.
- The defect record is created with `estimated_distance_meters = None`.
- The system broadcasts a `localization_unavailable` event via WebSocket to warn operators immediately that optical frames are moving without synchronized distance logging.

---

## 5. Physical Limitations in PVC Conduit Inspection

Operators and engineers must account for real-world physical constraints inherent to PVC conduit inspections:

1. **Wheel Slippage**: PVC pipe interiors can be lubricated by water, grease, biological slime, or condensation. Wheel encoders measure wheel rotation, not true ground travel. Slippage accumulates forward error.
2. **Tether Drag**: As the crawler penetrates deeper into conduits (e.g. beyond 15 meters), cable friction against PVC walls increases, causing wheels to slip during torque peaks.
3. **Slope and Ovalization**: Grade variations and pipe deformation alter normal forces on drive wheels, modifying the effective rolling radius.

For these reasons, the PipeBot API deliberately names this field `estimated_distance_meters` rather than `distance_meters`, acknowledging that encoder odometry is an engineering estimate subject to mechanical slippage.

