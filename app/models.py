# app/models.py
from pydantic import BaseModel
from typing import Optional

class VideoUploadResponse(BaseModel):
    """Response model for a successful video upload."""
    video_id: str
    message: str

class DetectionStatus(BaseModel):
    """Response model for the status of a detection task."""
    video_id: str
    status: str
    result: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
