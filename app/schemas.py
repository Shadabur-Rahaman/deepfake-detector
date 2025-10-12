# app/schemas.py - COMPLETE SCHEMAS FOR DEEPFAKE DETECTOR

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

class YouTubeRequest(BaseModel):
    """Schema for YouTube video analysis requests"""
    url: str = Field(..., description="YouTube video URL")
    
    @validator('url')
    def validate_youtube_url(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('URL is required and must be a string')
        
        v = v.strip()
        youtube_indicators = [
            'youtube.com', 'youtu.be', 'www.youtube.com', 
            'm.youtube.com', '/shorts/', '/watch?v='
        ]
        
        if not any(indicator in v.lower() for indicator in youtube_indicators):
            raise ValueError('Must be a valid YouTube URL')
        
        return v
        
class VideoUploadResponse(BaseModel):
    """Schema for video upload responses"""
    video_id: str = Field(..., description="Unique video identifier")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")
    
class AIAnalysis(BaseModel):
    """Schema for AI analysis details"""
    technical_reasoning: str = Field(..., description="Technical explanation of the analysis")
    confidence_explanation: str = Field(..., description="Explanation of confidence level")
    recommendation: str = Field(..., description="Recommendation based on analysis")
    advantages: Optional[str] = Field(None, description="Advantages of the detection method")
    processing_note: Optional[str] = Field(None, description="Processing notes")
    detection_focus: Optional[str] = Field(None, description="Focus areas of detection")
    artifact_indicators: Optional[List[str]] = Field(None, description="List of artifacts detected")

class ModelContributions(BaseModel):
    """Schema for individual model contributions"""
    efficientnet_result: Optional[str] = Field(None, description="EfficientNet model result")
    efficientnet_confidence: Optional[float] = Field(None, description="EfficientNet confidence")
    temporal_score: Optional[float] = Field(None, description="Temporal analysis score")
    spatial_score: Optional[float] = Field(None, description="Spatial analysis score")
    frequency_score: Optional[float] = Field(None, description="Frequency analysis score")
    model_type: Optional[str] = Field(None, description="Model type used")
    error: Optional[str] = Field(None, description="Error message if any")

class DetectionResponse(BaseModel):
    """Schema for detection analysis responses"""
    video_id: str = Field(..., description="Unique video identifier")
    prediction: str = Field(..., description="Detection result prediction")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage (0-100)")
    status: str = Field(..., description="Processing status")
    faces_detected: Optional[int] = Field(None, ge=0, description="Number of faces detected")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    
    # Additional fields
    metadata: Optional[Dict[str, Any]] = Field(None, description="Video metadata")
    video_url: Optional[str] = Field(None, description="URL to access the video file")
    analysis_method: Optional[str] = Field(None, description="Analysis method used")
    error: Optional[str] = Field(None, description="Error message if analysis failed")
    
class FeedbackRequest(BaseModel):
    """Schema for user feedback submission"""
    feedback: str = Field(..., description="User feedback (correct/incorrect/uncertain)")
    confidence_rating: Optional[int] = Field(None, ge=1, le=5, description="User confidence rating (1-5)")
    expert_validation: Optional[str] = Field(None, description="Expert validation if available")
    comments: Optional[str] = Field(None, max_length=500, description="Additional comments")
    
    @validator('feedback')
    def validate_feedback(cls, v):
        valid_feedback = ['correct', 'incorrect', 'uncertain']
        if v.lower() not in valid_feedback:
            raise ValueError(f'Feedback must be one of: {valid_feedback}')
        return v.lower()

class AnalyticsResponse(BaseModel):
    """Schema for analytics data"""
    total_detections_24h: int = Field(..., ge=0, description="Total detections in last 24 hours")
    avg_processing_time: float = Field(..., ge=0, description="Average processing time in seconds")
    content_distribution: Dict[str, int] = Field(..., description="Distribution of content types detected")
    model_performance: Dict[str, Dict[str, Union[float, int]]] = Field(..., description="Performance by model")
    error: Optional[str] = Field(None, description="Error message if analytics failed")

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="System health status")
    timestamp: float = Field(..., description="Current timestamp")
    active_detections: int = Field(..., ge=0, description="Number of active detections")
    system_capabilities: Optional[Dict[str, bool]] = Field(None, description="System capabilities")

class RealTimeRequest(BaseModel):
    """Schema for real-time detection requests"""
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    
class RealTimeResponse(BaseModel):
    """Schema for real-time detection responses"""
    prediction: str = Field(..., description="Detection result")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    faces_detected: int = Field(..., ge=0, description="Number of faces detected")
    processing_time: str = Field(..., description="Processing time")
    face_coordinates: Optional[Dict[str, int]] = Field(None, description="Face bounding box coordinates")
    error: Optional[str] = Field(None, description="Error message if analysis failed")

class YouTubeDownloadResponse(BaseModel):
    """Schema for YouTube download responses"""
    video_id: str = Field(..., description="Unique video identifier")
    status: str = Field(..., description="Download status")
    message: str = Field(..., description="Status message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Video metadata")

class DetectionStatusResponse(BaseModel):
    """Schema for detection status responses"""
    video_id: str = Field(..., description="Video identifier")
    status: str = Field(..., description="Current status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    
    # Result data (when completed)
    prediction: Optional[str] = Field(None, description="Final prediction")
    confidence: Optional[float] = Field(None, ge=0, le=100, description="Final confidence")
    faces_detected: Optional[int] = Field(None, ge=0, description="Number of faces detected")
    processing_time: Optional[float] = Field(None, ge=0, description="Total processing time")
    video_url: Optional[str] = Field(None, description="URL to access processed video")
    
    # Error handling
    error: Optional[str] = Field(None, description="Error message if failed")

class SystemCapabilities(BaseModel):
    """Schema for system capabilities"""
    enhanced_detection: bool = Field(..., description="Enhanced detection available")
    free_ai_ensemble: bool = Field(..., description="Free AI ensemble available")
    youtube_support: bool = Field(..., description="YouTube support available")
    real_time_detection: bool = Field(..., description="Real-time detection available")
    specialized_detectors: bool = Field(..., description="Specialized detectors available")

class RootResponse(BaseModel):
    """Schema for root endpoint response"""
    message: str = Field(..., description="Welcome message")
    status: str = Field(..., description="System status")
    capabilities: SystemCapabilities = Field(..., description="System capabilities")

# Export all schemas for easy importing
__all__ = [
    'YouTubeRequest',
    'VideoUploadResponse', 
    'DetectionResponse',
    'FeedbackRequest',
    'AnalyticsResponse',
    'HealthResponse',
    'RealTimeRequest',
    'RealTimeResponse',
    'YouTubeDownloadResponse',
    'DetectionStatusResponse',
    'AIAnalysis',
    'ModelContributions',
    'SystemCapabilities',
    'RootResponse'
    
]
