"""
Background Worker Service for Deepfake Detection

This module provides robust background processing for video detection tasks
with proper error handling, database session management, and status tracking.

Key fixes:
1. Uses its own database session (not request session)
2. Opens file from saved path (not UploadFile object)
3. Comprehensive error handling and logging
4. Proper status updates throughout processing

Author: Senior Backend Engineer
Date: 2024
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.video_job import VideoJob, JobStatus, DetectionMode
from ..services.database import get_db_session
from ..services.file_manager import file_manager
from ..services.detection_engine import DetectionEngine

logger = logging.getLogger(__name__)

class BackgroundWorker:
    """Robust background worker for video detection tasks."""
    
    def __init__(self):
        self.detection_engine = DetectionEngine()
    
    async def process_video_detection_task(
        self, 
        video_id: str, 
        file_path: str, 
        mode: str
    ) -> None:
        """
        Process video detection task in background.
        
        This function fixes the 'read of closed file' error by:
        1. Using its own database session (not request session)
        2. Opening file from saved path (not UploadFile object)
        3. Proper error handling and status updates
        
        Args:
            video_id: Unique video identifier
            file_path: Path to saved video file
            mode: Detection mode to use
        """
        # Use our own database session - NEVER reuse request session
        db: Session = next(get_db_session())
        
        try:
            logger.info(f"Starting background processing for video: {video_id}")
            
            # Get job from database
            video_job = db.query(VideoJob).filter(VideoJob.id == video_id).first()
            if not video_job:
                logger.error(f"Video job not found in database: {video_id}")
                return
            
            # Mark job as started
            video_job.mark_started()
            video_job.current_stage = "Initializing detection engine"
            db.commit()
            
            logger.info(f"Video job marked as processing: {video_id}")
            
            # Verify file exists and is accessible
            if not file_manager.get_file_path(video_id, "uploads"):
                raise FileNotFoundError(f"Video file not found: {file_path}")
            
            # Move file to processing stage
            if not file_manager.move_file(video_id, "uploads", "processing"):
                logger.warning(f"Could not move file to processing stage: {video_id}")
            
            # Update progress
            video_job.update_progress(10, "Loading video file")
            db.commit()
            
            # Process video detection
            start_time = time.time()
            result = await self._run_detection(file_path, mode, video_job, db)
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
            
            logger.info(f"Video processing completed successfully: {video_id} (took {processing_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"Background processing failed for {video_id}: {e}")
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
        
        finally:
            # Always close database session
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
    
    async def _run_detection(
        self, 
        file_path: str, 
        mode: str, 
        video_job: VideoJob, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Run the actual detection process.
        
        This method opens the file from the saved path, preventing
        the 'read of closed file' error.
        """
        try:
            # Update progress
            video_job.update_progress(20, "Opening video file")
            db.commit()
            
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
                video_job.update_progress(30, "Extracting frames")
                db.commit()
                
                # Run detection based on mode
                detection_mode = DetectionMode(mode)
                
                if detection_mode == DetectionMode.TRADITIONAL:
                    result = await self._run_traditional_detection(video_file, video_job, db)
                elif detection_mode == DetectionMode.ENHANCED:
                    result = await self._run_enhanced_detection(video_file, video_job, db)
                elif detection_mode == DetectionMode.ULTIMATE:
                    result = await self._run_ultimate_detection(video_file, video_job, db)
                elif detection_mode == DetectionMode.DETERMINISTIC:
                    result = await self._run_deterministic_detection(video_file, video_job, db)
                elif detection_mode == DetectionMode.AI_VIDEO:
                    result = await self._run_ai_video_detection(video_file, video_job, db)
                else:
                    raise ValueError(f"Unsupported detection mode: {mode}")
                
                return result
                
        except Exception as e:
            logger.error(f"Detection processing error for {video_job.id}: {e}")
            raise
    
    async def _run_traditional_detection(
        self, 
        video_file, 
        video_job: VideoJob, 
        db: Session
    ) -> Dict[str, Any]:
        """Run traditional deepfake detection."""
        try:
            video_job.update_progress(40, "Running traditional detection")
            db.commit()
            
            # Simulate traditional detection process
            # In real implementation, this would use your detection models
            result = await self.detection_engine.detect_traditional(video_file)
            
            video_job.update_progress(80, "Processing results")
            db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Traditional detection error: {e}")
            raise
    
    async def _run_enhanced_detection(
        self, 
        video_file, 
        video_job: VideoJob, 
        db: Session
    ) -> Dict[str, Any]:
        """Run enhanced deepfake detection."""
        try:
            video_job.update_progress(40, "Running enhanced detection")
            db.commit()
            
            result = await self.detection_engine.detect_enhanced(video_file)
            
            video_job.update_progress(80, "Processing results")
            db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced detection error: {e}")
            raise
    
    async def _run_ultimate_detection(
        self, 
        video_file, 
        video_job: VideoJob, 
        db: Session
    ) -> Dict[str, Any]:
        """Run ultimate ensemble detection."""
        try:
            video_job.update_progress(40, "Running ultimate ensemble detection")
            db.commit()
            
            result = await self.detection_engine.detect_ultimate(video_file)
            
            video_job.update_progress(80, "Processing results")
            db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Ultimate detection error: {e}")
            raise
    
    async def _run_deterministic_detection(
        self, 
        video_file, 
        video_job: VideoJob, 
        db: Session
    ) -> Dict[str, Any]:
        """Run deterministic detection."""
        try:
            video_job.update_progress(40, "Running deterministic detection")
            db.commit()
            
            result = await self.detection_engine.detect_deterministic(video_file)
            
            video_job.update_progress(80, "Processing results")
            db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Deterministic detection error: {e}")
            raise
    
    async def _run_ai_video_detection(
        self, 
        video_file, 
        video_job: VideoJob, 
        db: Session
    ) -> Dict[str, Any]:
        """Run AI video detection."""
        try:
            video_job.update_progress(40, "Running AI video detection")
            db.commit()
            
            result = await self.detection_engine.detect_ai_video(video_file)
            
            video_job.update_progress(80, "Processing results")
            db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"AI video detection error: {e}")
            raise

# Global worker instance
background_worker = BackgroundWorker()

# Convenience function for FastAPI background tasks
async def process_video_detection_task(video_id: str, file_path: str, mode: str):
    """Convenience function for FastAPI background tasks."""
    await background_worker.process_video_detection_task(video_id, file_path, mode)
