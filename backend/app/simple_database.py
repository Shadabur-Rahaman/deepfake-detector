"""
Simple Database Module for Deepfake Detection
This module provides basic database functionality without complex dependencies.
"""

import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Create SQLAlchemy Base
Base = declarative_base()

# Global database state
DATABASE_AVAILABLE = False
engine = None
SessionLocal = None

def setup_database():
    """Setup simple SQLite database"""
    global DATABASE_AVAILABLE, engine, SessionLocal
    
    try:
        # Create SQLite database
        database_url = "sqlite:///./detection_jobs.db"
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables if they don't exist
        try:
            from backend.app.db_models import DetectionJob
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.warning(f"⚠️ Table creation failed: {e}")
        
        DATABASE_AVAILABLE = True
        return True, "SQLite database initialized successfully"
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        DATABASE_AVAILABLE = False
        return False, str(e)

def get_db():
    """FastAPI dependency to get database session"""
    if not DATABASE_AVAILABLE or not SessionLocal:
        return None
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_detection_job_record(video_id: str, status: str, mode: str, file_path: str, filename: str):
    """Create a detection job record"""
    if not DATABASE_AVAILABLE:
        return False
    
    try:
        from backend.app.db_models import DetectionJob
        db = SessionLocal()
        job = DetectionJob(
            video_id=video_id,
            status=status,
            mode=mode,
            file_path=file_path,
            original_filename=filename  # Fixed: use original_filename instead of filename
        )
        db.add(job)
        db.commit()
        db.close()
        return True
    except Exception as e:
        logger.error(f"Failed to create detection job record: {e}")
        return False

def get_detection_job_record(video_id: str):
    """Get a detection job record"""
    if not DATABASE_AVAILABLE:
        return None
    
    try:
        from backend.app.db_models import DetectionJob
        db = SessionLocal()
        job = db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
        db.close()
        return job
    except Exception as e:
        logger.error(f"Failed to get detection job record: {e}")
        return None

def update_detection_job_record(video_id: str, **updates):
    """Update a detection job record"""
    if not DATABASE_AVAILABLE:
        return False
    
    try:
        from backend.app.db_models import DetectionJob
        db = SessionLocal()
        job = db.query(DetectionJob).filter(DetectionJob.video_id == video_id).first()
        if job:
            for key, value in updates.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            db.commit()
        db.close()
        return True
    except Exception as e:
        logger.error(f"Failed to update detection job record: {e}")
        return False
