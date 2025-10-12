"""
Database Models for Deepfake Detection
SQLAlchemy models for the detection system.

Author: Senior Backend Engineer
Date: 2024
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Float, Boolean
from sqlalchemy.sql import func

from .simple_database import Base

class DetectionJob(Base):
    """Database model for detection jobs"""
    __tablename__ = "detection_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), unique=True, nullable=False, index=True)
    status = Column(String(20), default="processing", nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    mode = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=True)
    original_filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    result = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    faces_analyzed = Column(Integer, default=0)
    processing_time = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
