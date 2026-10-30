"""Camera Ingestion and Frame Processing Module."""

from app.camera.camera_state import camera_state
from app.camera.frame_validator import FrameValidator

__all__ = ["camera_state", "FrameValidator"]

