"""
Database Configuration and Management
Production-ready database setup with comprehensive SQLite fallback support.

This module provides:
- SQLite compatibility fixes for conda environments
- Automatic fallback from SQLite to file-based storage
- Proper SQLAlchemy Base setup
- Connection pooling and health checks
- Error handling and recovery

Author: Senior Backend Engineer
Date: 2024
"""

import os
import sys
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

# SQLite compatibility fixes
try:
    # Try to use pysqlite3 if available (better conda compatibility)
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
    logger = logging.getLogger(__name__)
    logger.info("✅ Using pysqlite3 for better SQLite compatibility")
except ImportError:
    # Fall back to system sqlite3
    logger = logging.getLogger(__name__)
    logger.info("ℹ️ Using system sqlite3")

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# Create SQLAlchemy Base - this should NEVER be None
Base = declarative_base()

class DatabaseManager:
    """Database manager with comprehensive fallback support"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self.db_type: Optional[str] = None
        self.is_connected = False
        self.fallback_mode = False
        
    def setup_database(self) -> Tuple[bool, str]:
        """
        Setup database with comprehensive fallback support.
        Returns (success, message)
        """
        try:
            # Try SQLite first
            success, message = self._try_sqlite()
            if success:
                return True, message
            
            # Try in-memory SQLite
            logger.warning(f"⚠️ SQLite connection failed: {message}")
            logger.info("🔄 Falling back to in-memory storage...")
            
            success, message = self._try_memory_sqlite()
            if success:
                return True, message
            
            # Try file-based fallback
            logger.warning(f"⚠️ In-memory SQLite also failed: {message}")
            logger.info("🔄 Using file-based fallback...")
            
            success, message = self._setup_file_fallback()
            if success:
                return True, message
            
            # All options failed
            logger.error("❌ All database options failed")
            return False, "All database initialization options failed"
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False, str(e)
    
    def _try_sqlite(self) -> Tuple[bool, str]:
        """Try to setup SQLite database"""
        try:
            # Try different SQLite URLs
            sqlite_urls = [
                os.getenv("DATABASE_URL", "sqlite:///./detection_jobs.db"),
                "sqlite:///./detection_jobs.db",
                "sqlite:///detection_jobs.db"
            ]
            
            for url in sqlite_urls:
                try:
                    logger.info(f"🔍 Trying SQLite URL: {url}")
                    
                    # Create engine with SQLite-specific settings
                    engine = create_engine(
                        url,
                        poolclass=StaticPool,
                        connect_args={"check_same_thread": False},
                        echo=False
                    )
                    
                    # Test connection
                    with engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    
                    # Success!
                    self.engine = engine
                    self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                    self.db_type = "sqlite"
                    self.is_connected = True
                    
                    logger.info(f"✅ SQLite database connection successful: {url}")
                    return True, f"SQLite database connected successfully: {url}"
                    
                except Exception as e:
                    logger.debug(f"SQLite URL {url} failed: {e}")
                    continue
            
            return False, "All SQLite URLs failed - likely sqlite3_deserialize symbol missing"
            
        except Exception as e:
            return False, f"SQLite setup failed: {e}"
    
    def _try_memory_sqlite(self) -> Tuple[bool, str]:
        """Try to setup in-memory SQLite database"""
        try:
            engine = create_engine("sqlite:///:memory:", echo=False)
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.engine = engine
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.db_type = "sqlite_memory"
            self.is_connected = True
            
            logger.info("✅ In-memory SQLite database initialized")
            return True, "In-memory SQLite database connected successfully"
            
        except Exception as e:
            return False, f"In-memory SQLite failed: {e}"
    
    def _setup_file_fallback(self) -> Tuple[bool, str]:
        """Setup file-based fallback database"""
        try:
            from .database_fallback import get_file_database
            
            # Get file-based database instance
            file_db = get_file_database()
            
            # Create a mock engine that delegates to file database
            class FileBasedEngine:
                def __init__(self, file_db):
                    self.file_db = file_db
                    self._create_detection_job = file_db.create_detection_job
                    self._update_detection_job = file_db.update_detection_job
                    self._get_detection_job = file_db.get_detection_job
                    self._save_detection_result = file_db.save_detection_result
                
                def create_detection_job(self, **kwargs):
                    return self._create_detection_job(**kwargs)
                
                def update_detection_job(self, video_id, **kwargs):
                    return self._update_detection_job(video_id, **kwargs)
                
                def get_detection_job(self, video_id):
                    return self._get_detection_job(video_id)
                
                def save_detection_result(self, video_id, result):
                    return self._save_detection_result(video_id, result)
            
            self.engine = FileBasedEngine(file_db)
            self.SessionLocal = None  # Not used in file-based mode
            self.db_type = "file_based"
            self.is_connected = True
            self.fallback_mode = True
            
            logger.info("✅ File-based database fallback initialized")
            return True, "File-based database fallback connected successfully"
            
        except Exception as e:
            return False, f"File-based fallback failed: {e}"
    
    def create_tables(self):
        """Create database tables if using SQLAlchemy"""
        if not self.is_connected or self.fallback_mode:
            logger.warning("⚠️ Database not available - tables not created")
            return
        
        try:
            if self.engine and hasattr(self.engine, 'connect'):
                Base.metadata.create_all(bind=self.engine)
                logger.info("✅ Database tables created successfully")
            else:
                logger.warning("⚠️ Engine not available for table creation")
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
    
    def get_session(self):
        """Get database session"""
        if self.fallback_mode or not self.SessionLocal:
            from .database_fallback import get_file_based_session
            return get_file_based_session()
        else:
            return self.SessionLocal()

# Global database manager instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def setup_database() -> Tuple[bool, str]:
    """Setup database and return success status"""
    manager = get_database_manager()
    return manager.setup_database()

def get_engine():
    """Get database engine"""
    manager = get_database_manager()
    return manager.engine

def get_session_local():
    """Get session factory"""
    manager = get_database_manager()
    return manager.SessionLocal

def is_database_available() -> bool:
    """Check if database is available"""
    manager = get_database_manager()
    return manager.is_connected

def is_fallback_mode() -> bool:
    """Check if running in fallback mode"""
    manager = get_database_manager()
    return manager.fallback_mode

def create_tables():
    """Create database tables"""
    manager = get_database_manager()
    manager.create_tables()

# Database operation helpers
def create_detection_job_record(video_id: str, mode: str, file_path: str, 
                               original_filename: str, file_size: int):
    """Create detection job record using appropriate database"""
    manager = get_database_manager()
    
    if manager.fallback_mode:
        # File-based database
        return manager.engine.create_detection_job(
            video_id=video_id,
            mode=mode,
            file_path=file_path,
            status="processing"
        )
    else:
        # SQLAlchemy database
        db = manager.get_session()
        try:
            from .db_models import DetectionJob
            job = DetectionJob(
                video_id=video_id,
                mode=mode,
                file_path=file_path,
                original_filename=original_filename,
                file_size=file_size
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            return job
        finally:
            db.close()

def get_detection_job_record(video_id: str):
    """Get detection job record using appropriate database"""
    manager = get_database_manager()
    
    if manager.fallback_mode:
        # File-based database
        return manager.engine.get_detection_job(video_id)
    else:
        # SQLAlchemy database
        db = manager.get_session()
        try:
            from .db_models import DetectionJob
            return db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
        finally:
            db.close()

def update_detection_job_record(video_id: str, **updates):
    """Update detection job record using appropriate database"""
    manager = get_database_manager()
    
    if manager.fallback_mode:
        # File-based database
        return manager.engine.update_detection_job(video_id, **updates)
    else:
        # SQLAlchemy database
        db = manager.get_session()
        try:
            from .db_models import DetectionJob
            job = db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
            if job:
                for key, value in updates.items():
                    setattr(job, key, value)
                db.commit()
                return True
            return False
        finally:
            db.close()

def save_detection_result_record(video_id: str, result: dict):
    """Save detection result using appropriate database"""
    manager = get_database_manager()
    
    if manager.fallback_mode:
        # File-based database
        return manager.engine.save_detection_result(video_id, result)
    else:
        # SQLAlchemy database
        db = manager.get_session()
        try:
            from .db_models import DetectionJob
            job = db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
            if job:
                job.result = result
                db.commit()
                return True
            return False
        finally:
            db.close()

# FastAPI dependency for get_db
def get_db():
    """FastAPI dependency to get database session"""
    manager = get_database_manager()
    db = manager.get_session()
    try:
        yield db
    finally:
        if hasattr(db, 'close'):
            db.close()