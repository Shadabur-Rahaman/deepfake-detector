"""
Fixed Detection API Routes - Production Ready

This module provides the corrected detection endpoints that fix the root causes:
1. "read of closed file" - by persisting files immediately and passing file paths
2. "404 Video ID not found" - by using database persistence instead of in-memory dict

Author: Senior Backend Engineer
Date: 2024
"""

import logging
import uuid
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..models.video_job import VideoJob, JobStatus, DetectionMode
from ..services.file_manager import file_manager
from ..services.database import get_db
from ..services.background_worker import process_video_detection_task
from ..auth.dependencies import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/detection", tags=["detection"])

@router.post("/detect")
async def detect_deepfake_fixed(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("traditional"),
    current_user_id: Optional[str] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Fixed deepfake detection endpoint that resolves production bugs.
    
    Key fixes:
    1. Persists file immediately to avoid 'read of closed file' error
    2. Creates database record before scheduling background task
    3. Passes file path (not UploadFile) to background worker
    4. Uses proper error handling and validation
    """
    video_id = str(uuid.uuid4())
    
    try:
        # Validate detection mode
        try:
            detection_mode = DetectionMode(mode)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid detection mode: {mode}. Valid modes: {[m.value for m in DetectionMode]}"
            )
        
        # Save uploaded file immediately (this prevents 'read of closed file' error)
        logger.info(f"Processing video upload: {video_id} (mode: {mode})")
        file_path, file_metadata = await file_manager.save_uploaded_file(file, video_id)
        
        # Create VideoJob record in database BEFORE scheduling background task
        # This prevents '404 Video ID not found' error
        video_job = VideoJob(
            id=video_id,
            user_id=current_user_id,
            status=JobStatus.QUEUED,
            mode=detection_mode.value,
            file_path=file_path,
            original_filename=file_metadata["original_filename"],
            file_size_bytes=file_metadata["file_size_bytes"],
            file_hash=file_metadata["file_hash"],
            metadata=file_metadata
        )
        
        # Commit to database immediately so status endpoint can find the job
        db.add(video_job)
        db.commit()
        db.refresh(video_job)
        
        logger.info(f"Video job created in database: {video_id}")
        
        # Schedule background task with file path (NOT UploadFile object)
        # This prevents the 'read of closed file' error
        background_tasks.add_task(
            process_video_detection_task,
            video_id=video_id,
            file_path=file_path,
            mode=detection_mode.value
        )
        
        logger.info(f"Background task scheduled for video: {video_id}")
        
        return {
            "video_id": video_id,
            "status": "queued",
            "mode": mode,
            "message": f"Detection started using {mode} mode",
            "file_info": {
                "original_filename": file_metadata["original_filename"],
                "file_size_bytes": file_metadata["file_size_bytes"],
                "file_hash": file_metadata["file_hash"]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise
    except Exception as e:
        logger.error(f"Detection endpoint error for {video_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Clean up file if it was saved
        try:
            file_manager.cleanup_file(video_id, "uploads")
        except Exception:
            pass
        
        raise HTTPException(status_code=500, detail="Detection request failed")

@router.get("/detection-status/{video_id}")
async def get_detection_status_fixed(
    video_id: str,
    db: Session = Depends(get_db)
):
    """
    Fixed detection status endpoint that queries database instead of in-memory dict.
    
    This prevents '404 Video ID not found' errors by using persistent storage.
    """
    try:
        # Query database for job status (not in-memory dict)
        video_job = db.query(VideoJob).filter(VideoJob.id == video_id).first()
        
        if not video_job:
            raise HTTPException(
                status_code=404, 
                detail="Video ID not found"
            )
        
        # Return comprehensive status information
        response_data = video_job.to_dict()
        
        # Add additional status information
        response_data.update({
            "message": _get_status_message(video_job.status),
            "can_retry": video_job.can_retry(),
            "is_final": video_job.is_final_status()
        })
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status endpoint error for {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detection status")

@router.post("/retry/{video_id}")
async def retry_detection(
    video_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Retry a failed detection job."""
    try:
        video_job = db.query(VideoJob).filter(VideoJob.id == video_id).first()
        
        if not video_job:
            raise HTTPException(status_code=404, detail="Video ID not found")
        
        if not video_job.can_retry():
            raise HTTPException(
                status_code=400, 
                detail="Job cannot be retried (not failed or max retries reached)"
            )
        
        # Reset job status for retry
        video_job.status = JobStatus.QUEUED
        video_job.error_message = None
        video_job.error_code = None
        video_job.traceback = None
        video_job.progress_percentage = 0
        video_job.current_stage = None
        
        db.commit()
        
        # Schedule retry
        background_tasks.add_task(
            process_video_detection_task,
            video_id=video_id,
            file_path=video_job.file_path,
            mode=video_job.mode
        )
        
        logger.info(f"Retry scheduled for video: {video_id}")
        
        return {
            "video_id": video_id,
            "status": "queued",
            "message": "Detection retry scheduled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retry error for {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Retry failed")

@router.delete("/cancel/{video_id}")
async def cancel_detection(
    video_id: str,
    db: Session = Depends(get_db)
):
    """Cancel a queued or processing detection job."""
    try:
        video_job = db.query(VideoJob).filter(VideoJob.id == video_id).first()
        
        if not video_job:
            raise HTTPException(status_code=404, detail="Video ID not found")
        
        if video_job.is_final_status():
            raise HTTPException(
                status_code=400, 
                detail="Job is already completed and cannot be cancelled"
            )
        
        # Mark as cancelled
        video_job.status = JobStatus.CANCELLED
        video_job.completed_at = datetime.utcnow()
        video_job.error_message = "Job cancelled by user"
        
        db.commit()
        
        logger.info(f"Detection cancelled for video: {video_id}")
        
        return {
            "video_id": video_id,
            "status": "cancelled",
            "message": "Detection cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel error for {video_id}: {e}")
        raise HTTPException(status_code=500, detail="Cancel failed")

@router.get("/jobs")
async def list_user_jobs(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    current_user_id: Optional[str] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """List user's detection jobs with pagination and filtering."""
    try:
        query = db.query(VideoJob)
        
        # Filter by user if authenticated
        if current_user_id:
            query = query.filter(VideoJob.user_id == current_user_id)
        
        # Filter by status if provided
        if status:
            try:
                status_enum = JobStatus(status)
                query = query.filter(VideoJob.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status filter")
        
        # Apply pagination
        total_count = query.count()
        jobs = query.order_by(VideoJob.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "jobs": [job.to_dict() for job in jobs],
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List jobs error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

def _get_status_message(status: JobStatus) -> str:
    """Get user-friendly status message."""
    messages = {
        JobStatus.QUEUED: "Detection queued and waiting to start",
        JobStatus.PROCESSING: "Detection in progress",
        JobStatus.COMPLETED: "Detection completed successfully",
        JobStatus.FAILED: "Detection failed - check error details",
        JobStatus.CANCELLED: "Detection was cancelled"
    }
    return messages.get(status, "Unknown status")
