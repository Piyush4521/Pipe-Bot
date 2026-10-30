"""Ultralytics YOLO Inference Provider.

Executes object detection using local custom-trained YOLO weights (.pt),
validates class taxonomy, normalizes bounding box coordinates, and
integrates with RTX 2050 CUDA acceleration with CPU fallback.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import List, Optional
import uuid
import numpy as np

from app.core.config import get_settings
from app.models.defect import (
    PIPE_DEFECT_CLASSES,
    PIPE_DEFECT_CLASS_IDS,
    PIPE_DEFECT_NAME_TO_ID,
    DefectClass,
)
from app.schemas.detection import BoundingBoxSchema, InferenceResult
from app.schemas.frame import FrameMetadata
from app.vision.interfaces import InferenceProvider

logger = logging.getLogger("pipebot.ultralytics_provider")

TARGET_CLASSES = {
    "Deformation": DefectClass.DEFORMATION,
    "Misalignment": DefectClass.MISALIGNMENT,
    "Obstacle": DefectClass.OBSTACLE,
    "Rupture": DefectClass.RUPTURE,
    "deformation": DefectClass.DEFORMATION,
    "misalignment": DefectClass.MISALIGNMENT,
    "obstacle": DefectClass.OBSTACLE,
    "rupture": DefectClass.RUPTURE,
}


class UltralyticsInferenceProvider(InferenceProvider):
    """Inference provider wrapping the Ultralytics YOLO framework."""

    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None) -> None:
        self.settings = get_settings()
        self.model_path = model_path or self.settings.YOLO_MODEL_PATH
        self.requested_device = device or self.settings.INFERENCE_DEVICE
        self.device = "cpu"
        self._model = None
        self._is_ready = False

    async def initialize(self) -> bool:
        """Verify model weights exist, import ultralytics safely, and load the model."""
        if not self.settings.INFERENCE_ENABLED:
            logger.info("Inference engine is disabled by configuration (INFERENCE_ENABLED=False).")
            self._is_ready = False
            return False

        if not self.model_path or not Path(self.model_path).is_file():
            logger.warning(
                "YOLO model weights file not found at: %s. Provider remaining unavailable.",
                self.model_path,
            )
            self._is_ready = False
            return False

        try:
            from ultralytics import YOLO
            import torch

            # Determine compute device with safe CPU fallback
            if self.requested_device == "cuda" and torch.cuda.is_available():
                self.device = "cuda"
                logger.info(
                    "CUDA acceleration enabled on device: %s",
                    torch.cuda.get_device_name(0),
                )
            else:
                self.device = "cpu"
                if self.requested_device == "cuda":
                    logger.warning("CUDA requested but not available. Falling back to CPU.")

            # Load model instance
            self._model = YOLO(self.model_path)

            # Validate model class names against PipeBot taxonomy
            model_names = getattr(self._model, "names", {})
            if isinstance(model_names, dict):
                class_names = [str(name).lower() for name in model_names.values()]
            elif isinstance(model_names, list):
                class_names = [str(name).lower() for name in model_names]
            else:
                class_names = []

            # Check that all authorized target classes exist in model taxonomy
            expected_classes = [c.lower() for c in PIPE_DEFECT_CLASSES]
            missing_classes = set(expected_classes) - set(class_names)
            if missing_classes:
                logger.error(
                    "Model classes %s do not match expected PipeBot taxonomy %s. Provider rejected.",
                    class_names,
                    PIPE_DEFECT_CLASSES,
                )
                self._is_ready = False
                self._model = None
                return False

            self._is_ready = True
            logger.info("Ultralytics YOLO inference provider initialized successfully on %s.", self.device)
            return True

        except ImportError:
            logger.warning(
                "The ultralytics library is not installed in the environment. "
                "YOLO inference provider remains unavailable."
            )
            self._is_ready = False
            return False
        except Exception as exc:
            logger.error("Failed to initialize Ultralytics model: %s", exc)
            self._is_ready = False
            return False

    async def predict(self, frame: np.ndarray, metadata: FrameMetadata) -> List[InferenceResult]:
        """Run YOLO inference and extract normalized detection bounding boxes."""
        if not self._is_ready or self._model is None:
            return []

        try:
            h, w = frame.shape[:2]
            results = self._model.predict(
                source=frame,
                device=self.device,
                conf=self.settings.INFERENCE_CONFIDENCE_THRESHOLD,
                verbose=False,
            )

            detections: List[InferenceResult] = []
            now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    class_name = str(result.names.get(cls_id, "")).lower()

                    if class_name not in TARGET_CLASSES:
                        logger.warning("Encountered unknown defect class from model: %s", class_name)
                        continue

                    # Extract pixel coordinates [x1, y1, x2, y2]
                    xyxy = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = xyxy

                    # Normalize bounding box to [0.0, 1.0]
                    norm_x = max(0.0, min(1.0, x1 / w))
                    norm_y = max(0.0, min(1.0, y1 / h))
                    norm_w = max(0.0, min(1.0, (x2 - x1) / w))
                    norm_h = max(0.0, min(1.0, (y2 - y1) / h))

                    bbox = BoundingBoxSchema(
                        x=round(norm_x, 4),
                        y=round(norm_y, 4),
                        width=round(norm_w, 4),
                        height=round(norm_h, 4),
                    )

                    detections.append(
                        InferenceResult(
                            detection_id=f"det_{uuid.uuid4().hex[:12]}",
                            frame_id=metadata.frame_id,
                            inspection_id=metadata.inspection_id,
                            defect_class=TARGET_CLASSES[class_name],
                            confidence=round(conf, 4),
                            bounding_box=bbox,
                            inference_timestamp=now_utc,
                            capture_timestamp=metadata.capture_timestamp,
                            localization_status="unlocalized",
                        )
                    )

            return detections

        except Exception as exc:
            logger.error("Inference execution exception on frame %s: %s", metadata.frame_id, exc)
            return []

    async def shutdown(self) -> None:
        """Release PyTorch and CUDA memory resources cleanly."""
        self._is_ready = False
        self._model = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        logger.info("Ultralytics inference provider shut down cleanly.")

    @property
    def is_available(self) -> bool:
        """Whether the model is loaded and ready."""
        return self._is_ready

    @property
    def provider_name(self) -> str:
        """Identifier."""
        return "ultralytics"

