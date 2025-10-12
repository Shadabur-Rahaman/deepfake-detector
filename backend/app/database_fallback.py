"""
Database Fallback System for SQLite Compatibility Issues

This module provides a file-based fallback when SQLite has compatibility issues
in conda environments, particularly the "undefined symbol: sqlite3_deserialize" error.

Author: Senior ML Engineer
Date: 2024
"""

import os
import json
import pickle
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileBasedDatabase:
    """
    File-based database fallback for when SQLite is not available.
    Uses JSON files for persistence with thread-safe operations.
    """
    
    def __init__(self, db_dir: str = "./file_db"):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)
        self.lock = threading.RLock()
        
        # File paths
        self.jobs_file = self.db_dir / "detection_jobs.json"
        self.results_file = self.db_dir / "detection_results.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        logger.info(f"✅ File-based database initialized at: {self.db_dir}")
    
    def _initialize_files(self):
        """Initialize database files if they don't exist"""
        with self.lock:
            if not self.jobs_file.exists():
                with open(self.jobs_file, 'w') as f:
                    json.dump({}, f)
            
            if not self.results_file.exists():
                with open(self.results_file, 'w') as f:
                    json.dump({}, f)
    
    def _read_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Thread-safe JSON file reading"""
        with self.lock:
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
    
    def _write_json_file(self, file_path: Path, data: Dict[str, Any]):
        """Thread-safe JSON file writing"""
        with self.lock:
            # Write to temporary file first, then rename (atomic operation)
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            temp_file.replace(file_path)
    
    def create_detection_job(self, video_id: str, mode: str, status: str = "processing", 
                           file_path: str = "", created_at: Optional[datetime] = None) -> bool:
        """Create a new detection job record"""
        try:
            jobs = self._read_json_file(self.jobs_file)
            
            job_data = {
                "video_id": video_id,
                "mode": mode,
                "status": status,
                "file_path": file_path,
                "created_at": (created_at or datetime.now()).isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            jobs[video_id] = job_data
            self._write_json_file(self.jobs_file, jobs)
            
            logger.info(f"✅ Created detection job: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create detection job {video_id}: {e}")
            return False
    
    def update_detection_job(self, video_id: str, **updates) -> bool:
        """Update an existing detection job"""
        try:
            jobs = self._read_json_file(self.jobs_file)
            
            if video_id not in jobs:
                logger.warning(f"⚠️ Job {video_id} not found for update")
                return False
            
            jobs[video_id].update(updates)
            jobs[video_id]["updated_at"] = datetime.now().isoformat()
            
            self._write_json_file(self.jobs_file, jobs)
            logger.info(f"✅ Updated detection job: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update detection job {video_id}: {e}")
            return False
    
    def get_detection_job(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get a detection job by ID"""
        try:
            jobs = self._read_json_file(self.jobs_file)
            return jobs.get(video_id)
        except Exception as e:
            logger.error(f"❌ Failed to get detection job {video_id}: {e}")
            return None
    
    def save_detection_result(self, video_id: str, result: Dict[str, Any]) -> bool:
        """Save detection results"""
        try:
            results = self._read_json_file(self.results_file)
            
            result_data = {
                "video_id": video_id,
                "result": result,
                "saved_at": datetime.now().isoformat()
            }
            
            results[video_id] = result_data
            self._write_json_file(self.results_file, results)
            
            logger.info(f"✅ Saved detection result: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save detection result {video_id}: {e}")
            return False
    
    def get_detection_result(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detection results by video ID"""
        try:
            results = self._read_json_file(self.results_file)
            result_data = results.get(video_id)
            return result_data.get("result") if result_data else None
        except Exception as e:
            logger.error(f"❌ Failed to get detection result {video_id}: {e}")
            return None
    
    def list_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List recent detection jobs"""
        try:
            jobs = self._read_json_file(self.jobs_file)
            
            # Sort by created_at and return most recent
            job_list = list(jobs.values())
            job_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return job_list[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to list jobs: {e}")
            return []
    
    def cleanup_old_jobs(self, days_old: int = 7) -> int:
        """Clean up old jobs and results"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            # Clean up jobs
            jobs = self._read_json_file(self.jobs_file)
            jobs_to_remove = []
            
            for video_id, job in jobs.items():
                try:
                    created_at = datetime.fromisoformat(job.get("created_at", ""))
                    if created_at.timestamp() < cutoff_time:
                        jobs_to_remove.append(video_id)
                except (ValueError, TypeError):
                    # If we can't parse the date, remove it
                    jobs_to_remove.append(video_id)
            
            for video_id in jobs_to_remove:
                del jobs[video_id]
                cleaned_count += 1
            
            self._write_json_file(self.jobs_file, jobs)
            
            # Clean up results
            results = self._read_json_file(self.results_file)
            results_to_remove = []
            
            for video_id, result in results.items():
                try:
                    saved_at = datetime.fromisoformat(result.get("saved_at", ""))
                    if saved_at.timestamp() < cutoff_time:
                        results_to_remove.append(video_id)
                except (ValueError, TypeError):
                    results_to_remove.append(video_id)
            
            for video_id in results_to_remove:
                del results[video_id]
            
            self._write_json_file(self.results_file, results)
            
            logger.info(f"✅ Cleaned up {cleaned_count} old jobs and results")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old jobs: {e}")
            return 0

# Global instance
_file_db_instance = None

def get_file_database() -> FileBasedDatabase:
    """Get the global file database instance"""
    global _file_db_instance
    if _file_db_instance is None:
        _file_db_instance = FileBasedDatabase()
    return _file_db_instance

# Compatibility layer for SQLAlchemy-style operations
class FileBasedSession:
    """Compatibility layer that mimics SQLAlchemy session operations"""
    
    def __init__(self):
        self.db = get_file_database()
    
    def add(self, obj):
        """Add an object (compatibility method)"""
        pass  # Not used in our current implementation
    
    def commit(self):
        """Commit changes (compatibility method)"""
        pass  # Changes are committed immediately in file-based system
    
    def close(self):
        """Close session (compatibility method)"""
        pass  # No persistent connection to close
    
    def query(self, model_class):
        """Query method (compatibility method)"""
        return FileBasedQuery(self.db, model_class)

class FileBasedQuery:
    """Compatibility layer for SQLAlchemy query operations"""
    
    def __init__(self, db: FileBasedDatabase, model_class):
        self.db = db
        self.model_class = model_class
    
    def filter(self, condition):
        """Filter method (compatibility method)"""
        return self
    
    def first(self):
        """Get first result (compatibility method)"""
        return None
    
    def all(self):
        """Get all results (compatibility method)"""
        return []

def get_file_based_session():
    """Get a file-based session (compatibility function)"""
    return FileBasedSession()
