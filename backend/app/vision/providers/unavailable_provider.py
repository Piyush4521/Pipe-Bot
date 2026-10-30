"""Unavailable Fallback Inference Provider.

Serves as the safe baseline provider when no trained model weights are configured,
returning zero fabricated detections and an explicit unavailable status.
"""

from typing import List
import numpy as np

from app.schemas.detection import InferenceResult
from app.schemas.frame import FrameMetadata
from app.vision.interfaces import InferenceProvider


class UnavailableInferenceProvider(InferenceProvider):
    """Fallback provider used when model weights are not loaded."""

    def __init__(self) -> None:
        self._is_ready = False

    async def initialize(self) -> bool:
        """Mark provider initialized but explicitly unavailable for inference."""
        self._is_ready = False
        return True

    async def predict(self, frame: np.ndarray, metadata: FrameMetadata) -> List[InferenceResult]:
        """Return zero detections without fabricating synthetic results."""
        return []

    async def shutdown(self) -> None:
        """No hardware allocations to release."""
        self._is_ready = False

    @property
    def is_available(self) -> bool:
        """Always reports false as no model is loaded."""
        return False

    @property
    def provider_name(self) -> str:
        """Identifier string."""
        return "unavailable"

