"""Media and Defect Evidence Image Retrieval Endpoints."""

import logging
from pathlib import Path
import re
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.core.config import get_settings

logger = logging.getLogger("pipebot.media_endpoint")
router = APIRouter(prefix="/media", tags=["Media Evidence"])

SAFE_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]+$")


@router.get(
    "/{filename}",
    summary="Retrieve Defect Evidence Image",
    description="Serves stored defect evidence crop JPEG images with strict path traversal validation.",
)
async def get_media_file(filename: str) -> FileResponse:
    """Safely return an evidence image file."""
    # 1. Validate filename structure against regex and enforce JPEG extension
    if not SAFE_FILENAME_REGEX.match(filename) or ".." in filename or not filename.lower().endswith((".jpg", ".jpeg")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename or unsupported file extension. Only JPEG images are accessible.",
        )

    settings = get_settings()
    media_dir = settings.media_dir
    file_path = (media_dir / filename).resolve()

    # 2. Prevent directory traversal outside media storage folder
    if not str(file_path).startswith(str(media_dir.resolve())):
        logger.warning("Attempted path traversal access: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to path outside media directory is denied.",
        )

    # 3. Verify file exists
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence image '{filename}' not found.",
        )

    return FileResponse(path=file_path, media_type="image/jpeg")

