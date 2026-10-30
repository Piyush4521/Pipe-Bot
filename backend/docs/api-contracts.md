# PipeBot Frontend/Backend API Contract & Compatibility Matrix

> **Stage**: Stage 2 Implementation Completed  
> **Document Purpose**: Audits contract alignment between the Python FastAPI backend and the React/TypeScript frontend (`D:\PipeBot\src`).

---

## 1. Contract Alignment Summary

During Stage 2 implementation, backend schemas were engineered to natively deserialize and serialize camelCase JSON payloads to guarantee 100% interoperability with frontend TypeScript interfaces without requiring frontend modifications.

---

## 2. Model Compatibility Analysis

### 2.1. Inspection Session (`InspectionRecord` / `InspectionMission`)

| Frontend TypeScript Field (`InspectionRecord`) | Backend Python Field (`Inspection`) | Type Compatibility | Mapping Status |
| :--- | :--- | :--- | :--- |
| `id` (string) | `id` (int, primary key) | Number / String | Serialized as integer primary key; frontend can use either numeric or public ID |
| `inspectionId` (string) | `inspection_id` (string, unique) | Exact match | Directly matched |
| `pipeIdentifier` (string) | `pipe_identifier` (string) | Exact match | CamelCase alias supported |
| `pipeDiameterMm` (number) | `pipe_diameter_mm` (int) | Exact match | CamelCase alias supported |
| `operatorId` (string) | `operator_id` (string) | Exact match | CamelCase alias supported |
| `status` (`InspectionStatus`) | `status` (`InspectionStatus`) | Controlled Enum | Compatible with semantic mapping: `created` = `idle`, `cancelled` = `aborted` |
| `startedAt` (string ISO) | `started_at` (DateTime UTC) | Exact match | Formatted as ISO 8601 UTC string |
| `completedAt` (string ISO, optional) | `completed_at` (DateTime UTC, optional) | Exact match | Nullable until session concludes |
| `totalDistanceMeters` (number) | `total_distance_meters` (Float, optional) | Exact match | Nullable until validated from encoder pulses |
| `defectCount` (number) | `defect_count` (computed property) | Exact match | Dynamic count of non-deleted defects |
| `isArchived` (boolean) | `is_archived` (Boolean) | Exact match | Archival flag preserving history without destroying defect evidence |

#### Lifecycle State Semantic Mapping

| Backend Lifecycle State | Frontend Status Equivalent | Meaning |
| :--- | :--- | :--- |
| `created` | `idle` | Mission registered, crawler not yet started |
| `in_progress` | `running` / `in_progress` | Crawler traversing conduit, recording optical frames |
| `paused` | `paused` | Locomotion suspended temporarily |
| `completed` | `completed` | Run concluded with final odometry summary |
| `cancelled` | `aborted` | Run aborted before conclusion |
| `failed` | `aborted` | Run failed due to hardware error |

---

### 2.2. Defect Detection Record (`DefectDetection`)

| Frontend TypeScript Field (`DefectDetection`) | Backend Python Field (`Defect`) | Type Compatibility | Mapping Status |
| :--- | :--- | :--- | :--- |
| `id` (string) | `id` (int) | Number / String | Serialized as integer ID |
| `defectId` (string) | `defect_id` (string, unique) | Exact match | CamelCase alias supported |
| `inspectionId` (string) | `inspection_id` (int foreign key) | Compatible | Backend also exposes `inspectionPublicId` |
| `frameId` (string) | `frame_id` (string) | Exact match | CamelCase alias supported |
| `defectClass` (`DefectClass`) | `defect_class` (`DefectClass`) | Exact match | 4 target classes: `deformation`, `misalignment`, `obstacle`, `rupture` |
| `confidence` (number 0.0 - 1.0) | `confidence` (Float) | Exact match | Statistical confidence bounded between 0.0 and 1.0 |
| `boundingBox` (`BoundingBox`) | `bounding_box` (JSON) | Exact match | Dual support for `{x, y, width, height}` and `{xMin, yMin, xMax, yMax}` |
| `captureTimestamp` (string ISO) | `capture_timestamp` (DateTime UTC) | Exact match | Recorded frame capture timestamp from ESP32-CAM |
| `inferenceTimestamp` (string ISO, optional) | `inference_timestamp` (DateTime UTC, optional) | Exact match | Server YOLO processing timestamp |
| `estimatedDistanceMeters` (number, optional) | `estimated_distance_meters` (Float, optional) | Exact match | Correlated from rotary encoder ticks at optical capture |
| `reviewStatus` (`DefectReviewStatus`) | `review_status` (`DefectReviewStatus`) | Controlled Enum | Aliases supported: `unreviewed` -> `pending`, `verified` -> `confirmed`, `dismissed` -> `rejected` |
| `snapshotUrl` / `snapshotPath` | `snapshot_path` (string, optional) | Exact match | Stored as relative path / URL |
| `notes` (string, optional) | `notes` (text, optional) | Exact match | Operator review notes |

---

## 3. Review Status Alias Translation

To guarantee that the frontend review interface functions out of the box, the backend `DefectReviewUpdate` schema transparently normalizes frontend action terms:

```text
Frontend Action Term       Backend Database Enum
--------------------       ---------------------
'unreviewed'          ->   'pending'
'verified'            ->   'confirmed'
'dismissed'           ->   'rejected'
```

---

## 4. Bounding Box Format Compatibility

The frontend defines two distinct bounding box representations across its codebase:
1. `BoundingBox`: `{ x: number, y: number, width: number, height: number }` (used in `src/types/index.ts`).
2. `BoundingBox2D`: `{ xMin: number, yMin: number, xMax: number, yMax: number }` (used in `src/features/defects/types.ts`).

### Backend Resolution
The backend `BoundingBoxSchema` accepts both formats. When incoming JSON contains `xMin`, `yMin`, `xMax`, `yMax`, the Pydantic pre-validator computes:
```python
x = xMin
y = yMin
width = max(0.001, xMax - xMin)
height = max(0.001, yMax - yMin)
```
Responses are serialized as standardized `{ x, y, width, height }`.

---

## 5. Pagination Contract

### Backend Contract
All list endpoints (`/api/v1/inspections`, `/api/v1/defects`, `/api/v1/inspections/{id}/defects`) return a paginated envelope:
```json
{
  "items": [...],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

### Frontend Alignment
Existing frontend services (`inspectionService.ts`, `defectService.ts`) currently expect direct arrays or unpack `.items`. When integrating frontend live mode in Stage 5, the frontend services will consume `response.items` and utilize `response.total` for dashboard table pagination.

---

## 6. Optical Capture vs. Encoder Telemetry Synchronization Limitation

### The Hardware Reality
The PipeBot crawler features two discrete microcontrollers:
1. **ESP32-CAM**: Captures optical video frames and transmits an MJPEG or HLS stream over Wi-Fi.
2. **ESP32-WROOM-32**: Controls dual DC gearmotors, reads quadrature rotary encoder interrupts, and polls MPU6050 accelerometer/gyroscope over I2C.

### The Synchronization Challenge
Because these two microcontrollers operate on separate clock crystals and separate network sockets, the ESP32-CAM does not intrinsically know the rotary encoder count at the exact moment a video frame is captured.

### Future Protocol Requirement
In Stage 3 (ESP32 telemetry) and Stage 4 (Video pipeline), a dedicated synchronization mechanism must be implemented:
- Either hardware trigger pulses between GPIO pins connecting ESP32-CAM and ESP32-WROOM-32;
- Or optical frame timestamps cross-referenced with time-indexed odometry logs on the FastAPI server.

The backend strictly avoids inventing encoder counts or computing defect distances from GPU inference completion times.

