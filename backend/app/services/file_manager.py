"""
File Management Service for Deepfake Detection

This module provides secure file handling, storage, and cleanup utilities
for the deepfake detection service.

Author: Senior Backend Engineer
Date: 2024
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid
from fastapi import UploadFile, HTTPException
import aiofiles

logger = logging.getLogger(__name__)

class FileManager:
    """Secure file management service for video uploads and processing."""
    
    def __init__(self, storage_dir: str = "storage", max_file_size_mb: int = 500):
        self.storage_dir = Path(storage_dir)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.flv'}
        self.allowed_mime_types = {
            'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
            'video/x-matroska', 'video/webm', 'video/x-m4v', 'video/x-flv'
        }
        
        # Create storage directories
        self.ensure_storage_dirs()
    
    def ensure_storage_dirs(self):
        """Create necessary storage directories."""
        directories = [
            self.storage_dir,
            self.storage_dir / "uploads",
            self.storage_dir / "processing",
            self.storage_dir / "completed",
            self.storage_dir / "failed",
            self.storage_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            # Ensure directory is not executable for security
            os.chmod(directory, 0o755)
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded file for security and compatibility.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check file size
            if hasattr(file, 'size') and file.size and file.size > self.max_file_size_bytes:
                return False, f"File too large. Maximum size: {self.max_file_size_bytes // (1024*1024)}MB"
            
            # Check file extension
            if not file.filename:
                return False, "No filename provided"
            
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                return False, f"Unsupported file type. Allowed: {', '.join(self.allowed_extensions)}"
            
            # Check MIME type if available
            if hasattr(file, 'content_type') and file.content_type:
                if file.content_type not in self.allowed_mime_types:
                    return False, f"Unsupported MIME type: {file.content_type}"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False, f"File validation failed: {str(e)}"
    
    async def save_uploaded_file(self, file: UploadFile, video_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Save uploaded file to secure storage location.
        
        Args:
            file: FastAPI UploadFile object
            video_id: Unique video identifier
            
        Returns:
            Tuple[str, Dict[str, Any]]: (file_path, file_metadata)
        """
        try:
            # Validate file first
            is_valid, error_msg = self.validate_file(file)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Generate secure filename
            file_ext = Path(file.filename).suffix.lower()
            secure_filename = f"{video_id}{file_ext}"
            file_path = self.storage_dir / "uploads" / secure_filename
            
            # Save file using stream copy to avoid memory issues
            file_size = 0
            file_hash = hashlib.sha256()
            
            async with aiofiles.open(file_path, 'wb') as f:
                # Reset file pointer to beginning
                await file.seek(0)
                
                # Stream copy with size and hash calculation
                while chunk := await file.read(8192):  # 8KB chunks
                    if file_size + len(chunk) > self.max_file_size_bytes:
                        # Clean up partial file
                        if file_path.exists():
                            file_path.unlink()
                        raise HTTPException(status_code=400, detail="File too large")
                    
                    await f.write(chunk)
                    file_size += len(chunk)
                    file_hash.update(chunk)
            
            # Verify file was saved correctly
            if not file_path.exists() or file_path.stat().st_size == 0:
                raise HTTPException(status_code=500, detail="File save failed")
            
            # Prepare metadata
            metadata = {
                "original_filename": file.filename,
                "file_size_bytes": file_size,
                "file_hash": file_hash.hexdigest(),
                "file_extension": file_ext,
                "mime_type": file.content_type,
                "saved_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"File saved successfully: {video_id} -> {file_path} ({file_size} bytes)")
            return str(file_path), metadata
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File save error for {video_id}: {e}")
            # Clean up partial file
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
    
    def get_file_path(self, video_id: str, stage: str = "uploads") -> Optional[str]:
        """Get file path for a video ID in a specific stage."""
        stage_dir = self.storage_dir / stage
        if not stage_dir.exists():
            return None
        
        # Look for file with video_id prefix
        for file_path in stage_dir.glob(f"{video_id}.*"):
            if file_path.is_file():
                return str(file_path)
        
        return None
    
    def move_file(self, video_id: str, from_stage: str, to_stage: str) -> bool:
        """Move file between storage stages."""
        try:
            source_path = self.get_file_path(video_id, from_stage)
            if not source_path:
                logger.warning(f"Source file not found for {video_id} in {from_stage}")
                return False
            
            # Ensure destination directory exists
            dest_dir = self.storage_dir / to_stage
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file
            dest_path = dest_dir / Path(source_path).name
            shutil.move(source_path, dest_path)
            
            logger.info(f"File moved: {video_id} from {from_stage} to {to_stage}")
            return True
            
        except Exception as e:
            logger.error(f"File move error for {video_id}: {e}")
            return False
    
    def cleanup_file(self, video_id: str, stage: str = "uploads") -> bool:
        """Safely delete file from storage."""
        try:
            file_path = self.get_file_path(video_id, stage)
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
                logger.info(f"File cleaned up: {video_id} from {stage}")
                return True
            return False
        except Exception as e:
            logger.error(f"File cleanup error for {video_id}: {e}")
            return False
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Clean up files older than specified age."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for stage_dir in [self.storage_dir / "temp", self.storage_dir / "failed"]:
                if not stage_dir.exists():
                    continue
                
                for file_path in stage_dir.iterdir():
                    if file_path.is_file():
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_mtime < cutoff_time:
                            try:
                                file_path.unlink()
                                cleaned_count += 1
                                logger.debug(f"Cleaned up old file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Failed to clean up {file_path}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = {
                "total_files": 0,
                "total_size_bytes": 0,
                "by_stage": {}
            }
            
            for stage in ["uploads", "processing", "completed", "failed", "temp"]:
                stage_dir = self.storage_dir / stage
                if not stage_dir.exists():
                    stats["by_stage"][stage] = {"files": 0, "size_bytes": 0}
                    continue
                
                stage_files = 0
                stage_size = 0
                
                for file_path in stage_dir.iterdir():
                    if file_path.is_file():
                        stage_files += 1
                        stage_size += file_path.stat().st_size
                
                stats["by_stage"][stage] = {
                    "files": stage_files,
                    "size_bytes": stage_size
                }
                stats["total_files"] += stage_files
                stats["total_size_bytes"] += stage_size
            
            return stats
            
        except Exception as e:
            logger.error(f"Storage stats error: {e}")
            return {"error": str(e)}

# Global file manager instance
file_manager = FileManager()
