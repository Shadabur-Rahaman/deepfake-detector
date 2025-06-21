# app/models.py
from pydantic import BaseModel
from typing import Optional

class VideoUploadResponse(BaseModel):
    """Response model for video upload."""
    video_id: str
    message: str
    status: str = "received"

class DetectionStatus(BaseModel):
    """Response model for deepfake detection status."""
    video_id: str
    status: str
    result: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None