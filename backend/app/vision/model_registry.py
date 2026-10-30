"""Inference Model Provider Registry and Factory.

Constructs and caches the active inference provider based on centralized configuration,
ensuring safe fallbacks when AI hardware acceleration or weights are unavailable.
"""

import logging
from typing import Optional

from app.core.config import get_settings
from app.vision.interfaces import InferenceProvider
from app.vision.providers.ultralytics_provider import UltralyticsInferenceProvider
from app.vision.providers.unavailable_provider import UnavailableInferenceProvider

logger = logging.getLogger("pipebot.model_registry")

_active_provider: Optional[InferenceProvider] = None


def create_inference_provider() -> InferenceProvider:
    """Factory creating an inference provider based on application configuration."""
    settings = get_settings()

    if not settings.INFERENCE_ENABLED:
        logger.info("Inference is disabled. Using UnavailableInferenceProvider.")
        return UnavailableInferenceProvider()

    provider_name = settings.INFERENCE_PROVIDER.lower().strip()

    if provider_name == "ultralytics":
        return UltralyticsInferenceProvider()
    elif provider_name == "unavailable":
        return UnavailableInferenceProvider()
    else:
        logger.warning(
            "Unrecognized inference provider '%s'. Falling back to UnavailableInferenceProvider.",
            provider_name,
        )
        return UnavailableInferenceProvider()


def get_active_provider() -> InferenceProvider:
    """Return the global active inference provider singleton."""
    global _active_provider
    if _active_provider is None:
        _active_provider = create_inference_provider()
    return _active_provider


def set_active_provider(provider: InferenceProvider) -> None:
    """Override active provider (primarily for isolated test injection)."""
    global _active_provider
    _active_provider = provider

