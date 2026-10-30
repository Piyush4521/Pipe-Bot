# PipeBot AI Computer Vision Inference Subsystem

## 1. Subsystem Overview

The PipeBot computer vision subsystem provides an extensible, modular inference interface designed to detect structural anomalies in PVC conduits from optical video frames captured by the robotic crawler.

The architecture decouples the core backend ingestion and database logic from specific machine learning models or inference engines via an abstract provider pattern.

---

## 2. Pluggable Inference Provider Interface

All vision inference backends implement the abstract base class `InferenceProvider` (`app/vision/interfaces.py`):

```python
class InferenceProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Return True if model weights are loaded and ready for inference."""
        ...

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return provider metadata, backend type, weights path, and device."""
        ...

    @abstractmethod
    async def infer(
        self,
        frame: np.ndarray,
        metadata: FrameMetadata,
    ) -> List[InferenceResult]:
        """Execute anomaly detection on a decoded BGR image matrix."""
        ...
```

### 2.1 Provided Implementations

1. **`UnavailableInferenceProvider` (Default Safe Fallback)**:
   - Active whenever `INFERENCE_ENABLED=False` or valid model weights cannot be found on disk.
   - Always reports `is_available() -> False`.
   - Safely returns an empty list (`[]`) without throwing exceptions or crashing camera streaming.
   - Prevents the inspection crawler from failing when AI hardware is absent or offline.
2. **`UltralyticsInferenceProvider`**:
   - Concrete provider for YOLO models executed via the `ultralytics` runtime.
   - Dynamically loads weights specified by `YOLO_MODEL_PATH`.
   - Validates model file existence and tests model loading on initialization.
   - Translates raw bounding box outputs to normalized relative coordinates (`0.0` to `1.0`) and filters detections by `INFERENCE_CONFIDENCE_THRESHOLD`.

---

## 3. Canonical Defect Anomaly Classes

The AI vision subsystem strictly adheres to the four canonical defect classes defined in the PipeBot domain specification:

| Class ID | Class Name | Python Enum Identifier | Typical Conduit Manifestation |
|---|---|---|---|
| 0 | `Deformation` | `DefectClass.DEFORMATION` | Ovalization, radial flattening, or compressive buckling under soil load. |
| 1 | `Misalignment` | `DefectClass.MISALIGNMENT` | Joint displacement, angular offset, or axial separation between PVC segments. |
| 2 | `Obstacle` | `DefectClass.OBSTACLE` | Root intrusion, gravel/silt buildup, construction debris, or solid blockage. |
| 3 | `Rupture` | `DefectClass.RUPTURE` | Longitudinal cracking, shear puncture, wall fracture, or perforation. |

Detections outside these four canonical classes are rejected by schema validation. Canonical TitleCase is preserved across database persistence, API responses, and frontend integration. Case-insensitive parsing is supported on input for backwards compatibility.

---

## 4. Hardware Acceleration and Device Management

The subsystem is configured to leverage NVIDIA GeForce RTX 2050 Mobile hardware acceleration when available:

- **CUDA Auto-Detection**: If `INFERENCE_DEVICE="cuda"` or `"auto"` and PyTorch reports `torch.cuda.is_available()`, inference executes on the GPU.
- **Graceful CPU Fallback**: If CUDA drivers or GPU hardware are unavailable, execution falls back cleanly to `"cpu"` with appropriate logging.
- **No Hard Crashes**: Hardware detection errors never cause uncaught exceptions during server startup.

---

## 5. Defect Evidence Extraction and Media Serving

When a valid defect is detected on an optical frame:

1. **Evidence Cropping**:
   - The region of interest is cropped from the original BGR frame using the detected bounding box.
   - A **10% contextual margin** is applied around the bounding box boundaries to provide surrounding conduit context for human review.
   - Margin coordinates are clamped to ensure they remain strictly within the frame boundary `[0, frame_width]` and `[0, frame_height]`.
2. **Evidence Persistence**:
   - The cropped region is encoded to JPEG format and saved to the media directory (`backend/data/media/`).
   - Filenames follow the deterministic format: `defect_{detection_id}_{timestamp_ms}.jpg`.
3. **Path Traversal Protection**:
   - The media endpoint (`GET /api/v1/media/{filename}`) enforces strict path validation:
     - Rejects any filename containing `..`, `/`, or `\\`.
     - Resolves the absolute path and verifies it resides strictly inside the configured `media_dir`.
     - Returns `404 Not Found` for non-existent files or invalid traversal attempts.
4. **Database Record Creation**:
   - When an inspection is actively `IN_PROGRESS`, detections are automatically persisted as records in the `defects` table via `DefectService.create_defect()`.
   - The stored `snapshot_path` references the relative URI `/api/v1/media/{filename}`.
5. **WebSocket Broadcasting**:
   - Each detected defect triggers a real-time `defect_detected` event broadcast over WebSocket connections to update connected UI clients instantly.

---

## 6. Vision API Endpoints

### 6.1 Vision Subsystem Status
- **Endpoint**: `GET /api/v1/vision/status`
- **Response**:
```json
{
  "provider": "unavailable",
  "is_available": false,
  "model_path": null,
  "device": "cpu",
  "confidence_threshold": 0.5,
  "target_classes": [
    "deformation",
    "misalignment",
    "obstacle",
    "rupture"
  ],
  "error_message": "Vision inference is disabled or no model weights configured."
}
```

---

## 7. Configuration Settings

| Setting | Default | Description |
|---|---|---|
| `INFERENCE_ENABLED` | `False` | Master switch for automated computer vision inference. |
| `INFERENCE_PROVIDER` | `unavailable` | Provider implementation name (`unavailable` or `ultralytics`). |
| `YOLO_MODEL_PATH` | `None` | File path to trained YOLO `.pt` model weights. |
| `INFERENCE_CONFIDENCE_THRESHOLD` | `0.5` | Minimum statistical confidence score to register a defect detection. |
| `INFERENCE_DEVICE` | `cpu` | Target execution device (`cpu` or `cuda`). |
| `MEDIA_STORAGE_DIR` | `data/media` | Filesystem directory for defect evidence snapshots. |

