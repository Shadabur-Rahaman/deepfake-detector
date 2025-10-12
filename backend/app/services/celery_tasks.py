"""
Celery Tasks for Production Deepfake Detection

This module provides Celery task implementations for scalable background processing.
Use this in production environments where you need distributed task processing.

Author: Senior Backend Engineer
Date: 2024
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional
from datetime import datetime
from celery import Celery
from celery.exceptions import Retry, MaxRetriesExceededError
from sqlalchemy.orm import Session

from ..models.video_job import VideoJob, JobStatus, DetectionMode
from ..services.database import get_db_session
from ..services.file_manager import file_manager
from ..services.detection_engine import DetectionEngine

logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "deepfake_detection",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_routes={
        "deepfake_detection.process_video_detection": {"queue": "detection"},
        "deepfake_detection.cleanup_old_files": {"queue": "maintenance"},
    },
    task_default_queue="detection",
    task_default_exchange="detection",
    task_default_exchange_type="direct",
    task_default_routing_key="detection",
)

@celery_app.task(
    bind=True,
    name="deepfake_detection.process_video_detection",
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def process_video_detection_celery(
    self,
    video_id: str,
    file_path: str,
    mode: str
) -> Dict[str, Any]:
    """
    Celery task for processing video detection.
    
    This task provides:
    - Automatic retries with exponential backoff
    - Progress tracking
    - Error handling and logging
    - Database session management
    
    Args:
        video_id: Unique video identifier
        file_path: Path to saved video file
        mode: Detection mode to use
        
    Returns:
        Dict containing detection results
    """
    # Use our own database session - NEVER reuse request session
    db: Session = next(get_db_session())
    
    try:
        logger.info(f"Starting Celery task for video: {video_id}")
        
        # Get job from database
        video_job = db.query(VideoJob).filter(VideoJob.id == video_id).first()
        if not video_job:
            logger.error(f"Video job not found in database: {video_id}")
            raise ValueError(f"Video job not found: {video_id}")
        
        # Mark job as started
        video_job.mark_started()
        video_job.current_stage = "Initializing detection engine"
        db.commit()
        
        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={
                "video_id": video_id,
                "status": "processing",
                "progress": 10,
                "stage": "Initializing detection engine"
            }
        )
        
        # Verify file exists
        if not file_manager.get_file_path(video_id, "uploads"):
            raise FileNotFoundError(f"Video file not found: {file_path}")
        
        # Move file to processing stage
        if not file_manager.move_file(video_id, "uploads", "processing"):
            logger.warning(f"Could not move file to processing stage: {video_id}")
        
        # Update progress
        video_job.update_progress(20, "Loading video file")
        db.commit()
        
        self.update_state(
            state="PROGRESS",
            meta={
                "video_id": video_id,
                "status": "processing",
                "progress": 20,
                "stage": "Loading video file"
            }
        )
        
        # Process video detection
        start_time = time.time()
        result = _run_detection_with_celery(file_path, mode, video_job, db, self)
        processing_time = time.time() - start_time
        
        # Move file to completed stage
        file_manager.move_file(video_id, "processing", "completed")
        
        # Mark job as completed
        video_job.mark_completed(
            result=result,
            confidence=result.get("confidence"),
            processing_time=processing_time
        )
        db.commit()
        
        logger.info(f"Celery task completed successfully: {video_id} (took {processing_time:.2f}s)")
        
        return {
            "video_id": video_id,
            "status": "completed",
            "result": result,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Celery task failed for {video_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        try:
            # Update job status to failed
            if 'video_job' in locals():
                video_job.mark_failed(
                    error_message=str(e),
                    error_code=type(e).__name__,
                    traceback=traceback.format_exc()
                )
                db.commit()
            
            # Move file to failed stage
            file_manager.move_file(video_id, "processing", "failed")
            
        except Exception as db_error:
            logger.error(f"Failed to update job status in database: {db_error}")
        
        # Retry if possible
        try:
            raise self.retry(countdown=60, exc=e)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for video: {video_id}")
            raise
        
    finally:
        # Always close database session
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")

@celery_app.task(
    name="deepfake_detection.cleanup_old_files",
    ignore_result=True
)
def cleanup_old_files_celery(max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Celery task for cleaning up old files.
    
    Args:
        max_age_hours: Maximum age of files to keep (in hours)
        
    Returns:
        Dict containing cleanup statistics
    """
    try:
        logger.info(f"Starting file cleanup task (max_age: {max_age_hours}h)")
        
        cleaned_count = file_manager.cleanup_old_files(max_age_hours)
        
        logger.info(f"File cleanup completed: {cleaned_count} files cleaned")
        
        return {
            "status": "completed",
            "cleaned_files": cleaned_count,
            "max_age_hours": max_age_hours
        }
        
    except Exception as e:
        logger.error(f"File cleanup task failed: {e}")
        raise

@celery_app.task(
    name="deepfake_detection.health_check",
    ignore_result=True
)
def health_check_celery() -> Dict[str, Any]:
    """Celery task for health checking."""
    try:
        # Test database connection
        db: Session = next(get_db_session())
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {e}"
        finally:
            db.close()
        
        # Test file storage
        try:
            stats = file_manager.get_storage_stats()
            storage_status = "healthy"
        except Exception as e:
            storage_status = f"unhealthy: {e}"
            stats = {"error": str(e)}
        
        return {
            "status": "healthy" if db_status == "healthy" and storage_status == "healthy" else "unhealthy",
            "database": db_status,
            "storage": storage_status,
            "storage_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def _run_detection_with_celery(
    file_path: str,
    mode: str,
    video_job: VideoJob,
    db: Session,
    celery_task
) -> Dict[str, Any]:
    """
    Run detection with Celery progress updates.
    
    This function opens the file from the saved path, preventing
    the 'read of closed file' error.
    """
    try:
        # Update progress
        video_job.update_progress(30, "Opening video file")
        db.commit()
        
        celery_task.update_state(
            state="PROGRESS",
            meta={
                "video_id": video_job.id,
                "status": "processing",
                "progress": 30,
                "stage": "Opening video file"
            }
        )
        
        # Open file from saved path (fresh file handle)
        # This prevents 'read of closed file' error
        with open(file_path, 'rb') as video_file:
            # Verify file is readable
            video_file.seek(0, 2)  # Seek to end
            file_size = video_file.tell()
            video_file.seek(0)  # Reset to beginning
            
            if file_size == 0:
                raise ValueError("Video file is empty")
            
            logger.info(f"Processing video file: {file_path} ({file_size} bytes)")
            
            # Update progress
            video_job.update_progress(40, "Running detection")
            db.commit()
            
            celery_task.update_state(
                state="PROGRESS",
                meta={
                    "video_id": video_job.id,
                    "status": "processing",
                    "progress": 40,
                    "stage": "Running detection"
                }
            )
            
            # Run detection based on mode
            detection_mode = DetectionMode(mode)
            detection_engine = DetectionEngine()
            
            if detection_mode == DetectionMode.TRADITIONAL:
                result = detection_engine.detect_traditional(video_file)
            elif detection_mode == DetectionMode.ENHANCED:
                result = detection_engine.detect_enhanced(video_file)
            elif detection_mode == DetectionMode.ULTIMATE:
                result = detection_engine.detect_ultimate(video_file)
            elif detection_mode == DetectionMode.DETERMINISTIC:
                result = detection_engine.detect_deterministic(video_file)
            elif detection_mode == DetectionMode.AI_VIDEO:
                result = detection_engine.detect_ai_video(video_file)
            else:
                raise ValueError(f"Unsupported detection mode: {mode}")
            
            # Update progress
            video_job.update_progress(80, "Processing results")
            db.commit()
            
            celery_task.update_state(
                state="PROGRESS",
                meta={
                    "video_id": video_job.id,
                    "status": "processing",
                    "progress": 80,
                    "stage": "Processing results"
                }
            )
            
            return result
            
    except Exception as e:
        logger.error(f"Detection processing error for {video_job.id}: {e}")
        raise

# Celery worker configuration
@celery_app.task
def test_celery_connection():
    """Test Celery connection."""
    return {"status": "connected", "timestamp": datetime.utcnow().isoformat()}

# Periodic tasks (if using Celery Beat)
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "cleanup-old-files": {
        "task": "deepfake_detection.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
        "args": (24,)  # Clean files older than 24 hours
    },
    "health-check": {
        "task": "deepfake_detection.health_check",
        "schedule": 300.0,  # Run every 5 minutes
    },
}

# Celery monitoring
@celery_app.task
def get_worker_stats():
    """Get worker statistics."""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active = inspect.active()
        scheduled = inspect.scheduled()
        
        return {
            "stats": stats,
            "active": active,
            "scheduled": scheduled,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get worker stats: {e}")
        return {"error": str(e)}
