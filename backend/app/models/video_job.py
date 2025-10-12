"""
VideoJob SQLAlchemy Model for Deepfake Detection Service

This module defines the VideoJob model for tracking detection jobs with comprehensive
status tracking, error handling, and audit capabilities.

Author: Senior Backend Engineer
Date: 2024
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid

Base = declarative_base()

class JobStatus(str, Enum):
    """Video job status enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DetectionMode(str, Enum):
    """Detection mode enumeration."""
    TRADITIONAL = "traditional"
    ENHANCED = "enhanced"
    ULTIMATE = "ultimate"
    DETERMINISTIC = "deterministic"
    AI_VIDEO = "ai_video"

class VideoJob(Base):
    """
    VideoJob model for tracking deepfake detection jobs.
    
    This model provides comprehensive tracking of:
    - Job lifecycle (queued -> processing -> completed/failed)
    - File storage and management
    - Error handling and debugging
    - User association and audit trails
    - Performance metrics
    """
    __tablename__ = "video_jobs"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # User association (optional for anonymous uploads)
    user_id = Column(String(36), nullable=True, index=True)
    
    # Job status and mode
    status = Column(String(20), default=JobStatus.QUEUED, nullable=False, index=True)
    mode = Column(String(20), nullable=False, index=True)
    
    # File information
    file_path = Column(String(500), nullable=False)  # Path to saved file
    original_filename = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash for deduplication
    
    # Processing results
    result = Column(JSON, nullable=True)  # Detection results
    confidence = Column(Float, nullable=True)  # Overall confidence score
    processing_time_seconds = Column(Float, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    traceback = Column(Text, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0, nullable=False)
    current_stage = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional job metadata
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Cleanup tracking
    file_cleaned_up = Column(Boolean, default=False, nullable=False)
    cleanup_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<VideoJob(id='{self.id}', status='{self.status}', mode='{self.mode}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses."""
        return {
            "video_id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "mode": self.mode,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "progress_percentage": self.progress_percentage,
            "current_stage": self.current_stage,
            "result": self.result,
            "confidence": self.confidence,
            "processing_time_seconds": self.processing_time_seconds,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    def is_final_status(self) -> bool:
        """Check if job is in a final status (completed, failed, cancelled)."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return (
            self.status == JobStatus.FAILED and 
            self.retry_count < self.max_retries
        )
    
    def mark_started(self):
        """Mark job as started processing."""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.utcnow()
        self.progress_percentage = 0
    
    def mark_completed(self, result: Dict[str, Any], confidence: Optional[float] = None, processing_time: Optional[float] = None):
        """Mark job as completed with results."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100
        self.result = result
        self.confidence = confidence
        if processing_time:
            self.processing_time_seconds = processing_time
    
    def mark_failed(self, error_message: str, error_code: Optional[str] = None, traceback: Optional[str] = None):
        """Mark job as failed with error details."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.error_code = error_code
        self.traceback = traceback
        self.retry_count += 1
    
    def update_progress(self, percentage: int, stage: Optional[str] = None):
        """Update job progress."""
        self.progress_percentage = min(100, max(0, percentage))
        if stage:
            self.current_stage = stage
