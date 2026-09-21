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
            from .db_models import DetectionJob
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Import failed, trying alternative import: {e}")
            try:
                from app.db_models import DetectionJob
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Database tables created successfully with alternative import")
            except Exception as e2:
                logger.warning(f"⚠️ Alternative import also failed: {e2}")
                # Create the table manually
                try:
                    from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
                    from sqlalchemy.sql import func
                    import uuid
                    
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
                    
                    Base.metadata.create_all(bind=engine)
                    logger.info("✅ Database tables created successfully with manual model definition")
                except Exception as e3:
                    logger.error(f"❌ Manual table creation failed: {e3}")
        except Exception as e:
            logger.warning(f"⚠️ Table creation failed: {e}")
        
        DATABASE_AVAILABLE = True
        return True, "SQLite database initialized successfully"
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        DATABASE_AVAILABLE = False
        return False, str(e)

def ensure_detection_jobs_table():
    """Ensure the detection_jobs table exists"""
    if not DATABASE_AVAILABLE or not engine:
        return False
    
    try:
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='detection_jobs'"))
            if result.fetchone():
                return True
        
        # Table doesn't exist, create it
        from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
        from sqlalchemy.sql import func
        import uuid
        
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
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Detection jobs table created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to ensure detection_jobs table: {e}")
        return False

def force_recreate_database():
    """Force recreate the entire database"""
    global DATABASE_AVAILABLE, engine, SessionLocal
    
    try:
        if engine:
            # Drop all tables
            Base.metadata.drop_all(bind=engine)
            logger.info("🗑️ Dropped all existing tables")
        
        # Recreate tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Recreated all database tables")
        
        # Ensure detection_jobs table specifically
        ensure_detection_jobs_table()
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to recreate database: {e}")
        return False

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
        # Ensure table exists first
        ensure_detection_jobs_table()
        
        # Try multiple import paths
        try:
            from .db_models import DetectionJob
        except ImportError:
            try:
                from app.db_models import DetectionJob
            except ImportError:
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
        # Ensure table exists first
        ensure_detection_jobs_table()
        
        # Try multiple import paths
        try:
            from .db_models import DetectionJob
        except ImportError:
            try:
                from app.db_models import DetectionJob
            except ImportError:
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
        # Ensure table exists first
        ensure_detection_jobs_table()
        
        # Try multiple import paths
        try:
            from .db_models import DetectionJob
        except ImportError:
            try:
                from app.db_models import DetectionJob
            except ImportError:
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
