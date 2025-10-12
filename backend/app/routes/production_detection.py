"""
Production-Ready Detection Routes
Enhanced deepfake detection with modern AI algorithms

This module provides:
- Production-grade detection endpoints
- Multi-model ensemble inference
- Comprehensive error handling
- Real-time processing
- Advanced logging

Author: Senior Enterprise AI Developer
Date: 2024
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..services.production_advanced_detector import (
    ProductionAdvancedDetector, DetectionMode, get_production_detector,
    initialize_production_detector
)
from ..services.face_detector import FaceDetector
from ..services.video_processor import extract_faces_from_video
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()

class DetectionJob(Base):
    __tablename__ = "detection_jobs"
    
    id = Column(String, primary_key=True)
    video_id = Column(String, unique=True, index=True)
    status = Column(String, default="created")
    mode = Column(String, default="traditional")
    video_path = Column(String)
    result = Column(Text)
    confidence = Column(Float, default=0.0)
    faces_analyzed = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)
    progress = Column(Integer, default=0)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database engine and session
engine = create_engine("sqlite:///./detection_jobs.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create router
router = APIRouter(prefix="/api/production", tags=["Production Detection"])

# Global detector instance
production_detector = None

@router.on_event("startup")
async def startup_production_detector():
    """Initialize production detector on startup"""
    global production_detector
    try:
        production_detector = await initialize_production_detector(DetectionMode.PRODUCTION_ADVANCED)
        # Reduced logging to avoid duplicates
    except Exception as e:
        logger.error(f"[ERROR] Production detector initialization failed: {e}")
        production_detector = None

@router.post("/detect")
async def detect_deepfake_production(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("production_advanced"),
    db: Session = Depends(get_db)
):
    """
    Production-grade deepfake detection endpoint
    
    Modes:
    - traditional: Uses deepfake_detector_finetuned1.pth (baseline CNN/EfficientNet)
    - modern_ai: Uses advanced AI models with ensemble inference
    - production_advanced: Uses all available models with optimized ensemble
    """
    try:
        # Validate mode
        valid_modes = ["traditional", "modern_ai", "production_advanced"]
        if mode not in valid_modes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid mode. Use one of: {', '.join(valid_modes)}"
            )
        
        # Check if production detector is available
        if not production_detector:
            raise HTTPException(
                status_code=503,
                detail="Production detector not available. Please try again later."
            )
        
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        
        # Save uploaded file
        video_path = await save_uploaded_file(file, video_id)
        
        # Create detection job in database
        detection_mode = DetectionMode(mode)
        job = DetectionJob(
            id=str(uuid.uuid4()),
            video_id=video_id,
            status="created",
            mode=mode,
            video_path=str(video_path)
        )
        db.add(job)
        db.commit()
        
        # Start background detection task
        background_tasks.add_task(
            run_production_detection, 
            video_id, 
            str(video_path), 
            detection_mode
        )
        
        logger.info(f"[OK] Production detection job created: {video_id} (mode: {mode})")
        
        return {
            "video_id": video_id,
            "status": "created",
            "mode": mode,
            "message": "Production detection job created successfully",
            "video_path": str(video_path),
            "detection_type": "production_advanced" if mode == "production_advanced" else mode
        }
        
    except Exception as e:
        logger.error(f"Production detection request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Production detection request failed: {str(e)}")

@router.get("/detection-status/{video_id}")
async def get_production_detection_status(
    video_id: str,
    db: Session = Depends(get_db)
):
    """Get status of production detection job"""
    try:
        job = db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Detection job not found")
        
        return {
            "video_id": video_id,
            "status": job.status,
            "mode": job.mode,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            "result": job.result if job.result else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get detection status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get detection status: {str(e)}")

@router.get("/model-status")
async def get_model_status():
    """Get status of all detection models"""
    try:
        if not production_detector:
            raise HTTPException(
                status_code=503,
                detail="Production detector not available"
            )
        
        status = production_detector.get_model_status()
        return {
            "status": "success",
            "detector_status": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.post("/set-mode")
async def set_detection_mode(
    mode: str = Form(...),
    db: Session = Depends(get_db)
):
    """Set detection mode for the production detector"""
    try:
        valid_modes = ["traditional", "modern_ai", "production_advanced"]
        if mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode. Use one of: {', '.join(valid_modes)}"
            )
        
        if not production_detector:
            raise HTTPException(
                status_code=503,
                detail="Production detector not available"
            )
        
        # Set detection mode
        detection_mode = DetectionMode(mode)
        production_detector.set_detection_mode(detection_mode)
        
        # Reinitialize models for the new mode
        await production_detector.initialize_models(detection_mode)
        
        logger.info(f"[OK] Detection mode set to: {mode}")
        
        return {
            "status": "success",
            "mode": mode,
            "message": f"Detection mode set to {mode} successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to set detection mode: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set detection mode: {str(e)}")

@router.post("/enable-model")
async def enable_model(
    model_name: str = Form(...),
    enabled: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Enable or disable a specific model"""
    try:
        if not production_detector:
            raise HTTPException(
                status_code=503,
                detail="Production detector not available"
            )
        
        production_detector.enable_model(model_name, enabled)
        
        logger.info(f"[OK] Model {model_name} {'enabled' if enabled else 'disabled'}")
        
        return {
            "status": "success",
            "model_name": model_name,
            "enabled": enabled,
            "message": f"Model {model_name} {'enabled' if enabled else 'disabled'} successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to enable/disable model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enable/disable model: {str(e)}")

async def save_uploaded_file(file: UploadFile, video_id: str) -> Path:
    """Save uploaded file and return path"""
    try:
        # Create uploads directory
        uploads_dir = Path("uploaded_videos")
        uploads_dir.mkdir(exist_ok=True)
        
        # Generate filename
        file_extension = Path(file.filename).suffix if file.filename else ".mp4"
        filename = f"{video_id}{file_extension}"
        file_path = uploads_dir / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"[OK] File saved: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"[ERROR] File save failed: {e}")
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

async def run_production_detection(video_id: str, video_path: str, mode: DetectionMode):
    """Run production detection in background"""
    try:
        logger.info(f"[START] Starting production detection for {video_id} (mode: {mode.value})")
        
        # Update job status
        db = SessionLocal()
        job = db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
        if job:
            job.status = "processing"
            db.commit()
        
        # Initialize face detector
        face_detector = FaceDetector()
        
        # Extract faces from video
        logger.info(f"📹 Extracting faces from video: {video_path}")
        faces, _ = await extract_faces_from_video(video_path)
        
        if not faces:
            logger.warning(f"[WARNING] No faces detected in video: {video_path}")
            result = {
                "prediction": "No faces detected",
                "confidence": 0.0,
                "is_deepfake": False,
                "processing_time": 0.0,
                "models_used": [],
                "individual_scores": {},
                "ensemble_confidence": 0.0,
                "metadata": {
                    "faces_detected": 0,
                    "error": "No faces detected in video"
                }
            }
        else:
            logger.info(f"[OK] Extracted {len(faces)} faces from video")
            
            # Run production detection
            detection_result = await production_detector.detect_deepfake(faces, video_path)
            
            # Convert to dict for storage
            result = {
                "prediction": detection_result.prediction,
                "confidence": detection_result.confidence,
                "is_deepfake": detection_result.is_deepfake,
                "processing_time": detection_result.processing_time,
                "models_used": detection_result.models_used,
                "individual_scores": detection_result.individual_scores,
                "ensemble_confidence": detection_result.ensemble_confidence,
                "metadata": detection_result.metadata,
                "error": detection_result.error
            }
        
        # Update job with result
        if job:
            job.status = "completed"
            job.result = result
            db.commit()
        
        logger.info(f"[OK] Production detection completed for {video_id}: {result['prediction']} ({result['confidence']:.3f})")
        
    except Exception as e:
        logger.error(f"[ERROR] Production detection failed for {video_id}: {e}")
        
        # Update job with error
        try:
            db = SessionLocal()
            job = db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
            if job:
                job.status = "failed"
                job.result = {"error": str(e)}
                db.commit()
        except Exception as db_error:
            logger.error(f"[ERROR] Failed to update job status: {db_error}")
    
    finally:
        # Clean up database connection
        try:
            db.close()
        except:
            pass
