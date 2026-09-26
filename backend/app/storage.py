import os
import uuid
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

try:
    import aiofiles  # type: ignore
    _AIOFILES_AVAILABLE = True
except ImportError:
    _AIOFILES_AVAILABLE = False
    logger.warning(
        "aiofiles not installed — using synchronous file I/O fallback for uploads. "
        "Install with: pip install aiofiles"
    )


async def save_uploaded_video(video_file: UploadFile):
    """Save uploaded video and return video_id and path.

    Uses aiofiles for async I/O when available, otherwise falls back to
    synchronous writes so the app still starts on incomplete installs.
    """
    video_id = str(uuid.uuid4())
    safe_name = (video_file.filename or "upload.bin").replace("/", "_").replace("\\", "_")
    filename = f"{video_id}_{safe_name}"
    video_path = os.path.join(UPLOAD_DIR, filename)

    if _AIOFILES_AVAILABLE:
        async with aiofiles.open(video_path, "wb") as f:  # type: ignore[attr-defined]
            content = await video_file.read()
            await f.write(content)
    else:
        content = await video_file.read()
        with open(video_path, "wb") as f:
            f.write(content)

    return video_id, video_path


def delete_video_file(video_path: str):
    """Delete the video file after processing"""
    try:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
    except Exception as e:
        logger.debug("Failed to delete %s: %s", video_path, e)
