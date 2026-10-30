"""Centralized Application Configuration.

Loads configuration from environment variables and .env file using Pydantic Settings.
Ensures safe defaults and dynamic directory resolution within the backend folder.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings schema and environment variable loader."""

    # Project Identity
    APP_NAME: str = "PipeBot Backend"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # API Routing
    API_V1_PREFIX: str = "/api/v1"

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./data/pipebot.db"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # CORS Allowed Origins (Comma-separated string)
    CORS_ORIGINS: str = "http://127.0.0.1:3000,http://localhost:3000"

    # Telemetry and Device Ingestion Configuration
    DEVICE_INGEST_TOKEN: Optional[str] = None
    HEARTBEAT_TIMEOUT_SECONDS: float = 5.0
    TELEMETRY_STALE_TIMEOUT_SECONDS: float = 3.0
    WS_MAX_CONNECTIONS: int = 50

    # Camera Stream Ingestion Configuration
    CAMERA_ID: str = "esp32_cam_01"
    CAMERA_STREAM_URL: str = ""
    CAMERA_STREAM_TYPE: str = "mjpeg"
    CAMERA_CONNECT_TIMEOUT: float = 5.0
    CAMERA_READ_TIMEOUT: float = 5.0
    CAMERA_MAX_FRAME_BYTES: int = 1048576  # 1 MB maximum frame size
    CAMERA_MAX_FRAME_WIDTH: int = 1920
    CAMERA_MAX_FRAME_HEIGHT: int = 1080
    CAMERA_MAX_FPS: float = 30.0
    CAMERA_QUEUE_SIZE: int = 10

    # Media and Defect Evidence Storage
    MEDIA_STORAGE_DIR: str = "data/media"

    # Vision and YOLO Inference Configuration
    INFERENCE_ENABLED: bool = False
    INFERENCE_PROVIDER: str = "unavailable"  # "unavailable" | "ultralytics"
    YOLO_MODEL_PATH: Optional[str] = None
    INFERENCE_CONFIDENCE_THRESHOLD: float = 0.5
    INFERENCE_DEVICE: str = "cpu"  # "cpu" | "cuda"

    # Directory Paths (Relative to backend root)
    BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a sanitized list."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def data_dir(self) -> Path:
        """Ensure and return the path to the backend data directory."""
        directory = self.BACKEND_ROOT / "data"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @property
    def media_dir(self) -> Path:
        """Ensure and return the path to the media evidence storage directory."""
        directory = self.BACKEND_ROOT / self.MEDIA_STORAGE_DIR
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @property
    def logs_dir(self) -> Path:
        """Ensure and return the path to the backend logs directory."""
        directory = self.BACKEND_ROOT / "logs"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @property
    def resolved_database_url(self) -> str:
        """Resolve relative SQLite database URLs to the absolute backend data directory."""
        if self.DATABASE_URL.startswith("sqlite:///./data/"):
            db_filename = self.DATABASE_URL.replace("sqlite:///./data/", "")
            resolved_path = (self.data_dir / db_filename).resolve()
            return f"sqlite:///{resolved_path}"
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """Cached accessor for application settings singleton."""
    return Settings()

