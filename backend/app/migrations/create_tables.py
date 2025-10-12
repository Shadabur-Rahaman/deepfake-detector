#!/usr/bin/env python3
"""
Database Migration Script - Create Tables

This script creates all necessary database tables for the deepfake detection service.
Run this script after setting up your database connection.

Author: Senior Backend Engineer
Date: 2024
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Import models to ensure they're registered
from app.models.video_job import Base, VideoJob, JobStatus, DetectionMode

logger = logging.getLogger(__name__)

def create_database_tables():
    """Create all database tables."""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "sqlite:///./deepfake_detection.db")
        
        logger.info(f"Creating database tables using: {database_url}")
        
        # Create engine
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Verify tables were created
        with engine.connect() as conn:
            if database_url.startswith("sqlite"):
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
            else:
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                tables = [row[0] for row in result]
            
            logger.info(f"Created tables: {tables}")
            
            # Check if video_jobs table exists and has correct structure
            if "video_jobs" in tables:
                logger.info("[OK] video_jobs table created successfully")
                
                # Show table structure
                if database_url.startswith("sqlite"):
                    result = conn.execute(text("PRAGMA table_info(video_jobs)"))
                    columns = [row[1] for row in result]
                else:
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'video_jobs'
                    """))
                    columns = [row[0] for row in result]
                
                logger.info(f"video_jobs columns: {columns}")
            else:
                logger.error("[ERROR] video_jobs table not found")
                return False
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def create_indexes():
    """Create additional indexes for performance."""
    try:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./deepfake_detection.db")
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status)",
                "CREATE INDEX IF NOT EXISTS idx_video_jobs_user_id ON video_jobs(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_video_jobs_mode ON video_jobs(mode)",
                "CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_video_jobs_status_created ON video_jobs(status, created_at)"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    logger.info(f"Created index: {index_sql}")
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
        
        logger.info("Database indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Index creation failed: {e}")
        return False

def verify_setup():
    """Verify the database setup is correct."""
    try:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./deepfake_detection.db")
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # Test basic queries
            result = conn.execute(text("SELECT COUNT(*) FROM video_jobs"))
            count = result.scalar()
            logger.info(f"video_jobs table has {count} records")
            
            # Test insert/select
            from app.models.video_job import VideoJob, JobStatus, DetectionMode
            from sqlalchemy.orm import sessionmaker
            
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            try:
                # Create a test record
                test_job = VideoJob(
                    id="test-migration-123",
                    status=JobStatus.QUEUED,
                    mode=DetectionMode.TRADITIONAL.value,
                    file_path="/test/path/video.mp4",
                    original_filename="test.mp4"
                )
                
                db.add(test_job)
                db.commit()
                
                # Verify it was created
                retrieved_job = db.query(VideoJob).filter(VideoJob.id == "test-migration-123").first()
                if retrieved_job:
                    logger.info("[OK] Database setup verification successful")
                    
                    # Clean up test record
                    db.delete(retrieved_job)
                    db.commit()
                    logger.info("Test record cleaned up")
                else:
                    logger.error("[ERROR] Database setup verification failed")
                    return False
                    
            finally:
                db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False

def main():
    """Main migration function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting database migration...")
    
    # Create tables
    if not create_database_tables():
        logger.error("Failed to create database tables")
        sys.exit(1)
    
    # Create indexes
    if not create_indexes():
        logger.error("Failed to create database indexes")
        sys.exit(1)
    
    # Verify setup
    if not verify_setup():
        logger.error("Database setup verification failed")
        sys.exit(1)
    
    logger.info("[OK] Database migration completed successfully!")
    logger.info("You can now start the deepfake detection service.")

if __name__ == "__main__":
    main()
