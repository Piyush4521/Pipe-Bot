"""Abstract Base Interface for Computer Vision Inference Providers.

Establishes the contract for model lifecycle management, frame prediction,
and structured defect detection extraction.
"""

from abc import ABC, abstractmethod
from typing import List
import numpy as np

from app.schemas.detection import InferenceResult
from app.schemas.frame import FrameMetadata


class InferenceProvider(ABC):
    """Abstract interface for pluggable defect detection inference engines."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the model provider and allocate required hardware resources."""
        pass

    @abstractmethod
    async def predict(self, frame: np.ndarray, metadata: FrameMetadata) -> List[InferenceResult]:
        """Perform visual defect detection on a decoded OpenCV BGR image frame.

        Returns an empty list if no defects are identified or if the provider is unavailable.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Release allocated inference engine resources and hardware buffers."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Whether the provider is currently operational and ready to process frames."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier."""
        pass

