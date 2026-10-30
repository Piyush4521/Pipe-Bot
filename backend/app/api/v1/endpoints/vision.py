"""Computer Vision and Inference Engine Endpoints."""

from datetime import datetime, timezone
import logging
from fastapi import APIRouter

from app.core.config import get_settings
from app.models.defect import DefectClass
from app.schemas.detection import InferenceStatusResponse
from app.vision.model_registry import get_active_provider

logger = logging.getLogger("pipebot.vision_endpoint")
router = APIRouter(prefix="/vision", tags=["Computer Vision"])


@router.get(
    "/status",
    response_model=InferenceStatusResponse,
    summary="Get Inference Engine Status",
    description="Returns operational state of the YOLO defect detection interface and target taxonomy.",
)
def get_vision_status() -> InferenceStatusResponse:
    """Retrieve computer vision inference provider status."""
    settings = get_settings()
    provider = get_active_provider()
    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    expected_classes = [c.value for c in DefectClass]

    if provider.is_available:
        summary_msg = f"Inference engine active using {provider.provider_name} on {settings.INFERENCE_DEVICE}"
    elif not settings.INFERENCE_ENABLED:
        summary_msg = "Inference is disabled by configuration (INFERENCE_ENABLED=False)"
    else:
        summary_msg = f"Inference provider '{provider.provider_name}' is currently unavailable (no model weights loaded)"

    return InferenceStatusResponse(
        provider=provider.provider_name,
        is_available=provider.is_available,
        model_path=settings.YOLO_MODEL_PATH,
        device=settings.INFERENCE_DEVICE,
        confidence_threshold=settings.INFERENCE_CONFIDENCE_THRESHOLD,
        expected_classes=expected_classes,
        status=summary_msg,
        timestamp=now_utc,
    )

