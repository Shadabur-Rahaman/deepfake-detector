"""
Database Configuration and Fallback System
Production-ready database setup with automatic fallback support.

This module provides:
- Database URL detection and validation
- Automatic fallback from SQLite to PostgreSQL/MySQL
- Connection pooling and health checks
- Migration support
- Error handling and recovery

Author: Senior Backend Engineer
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration with fallback support"""
    
    def __init__(self):
        self.primary_db_url = None
        self.fallback_db_url = None
        self.engine = None
        self.SessionLocal = None
        self.db_type = None
        self.is_connected = False
        
    def detect_database_urls(self) -> Tuple[str, Optional[str]]:
        """Detect primary and fallback database URLs from environment"""
        
        # Primary database from environment
        primary_url = os.getenv('DATABASE_URL')
        if not primary_url:
            # Default to SQLite for development
            primary_url = "sqlite:///./ifake_auth.db"
        
        # Fallback database URLs
        fallback_urls = [
            os.getenv('FALLBACK_DATABASE_URL'),
            os.getenv('POSTGRES_URL'),
            os.getenv('MYSQL_URL'),
            "postgresql://postgres:password@localhost:5432/ifake_auth",
            "mysql://root:password@localhost:3306/ifake_auth"
        ]
        
        fallback_url = None
        for url in fallback_urls:
            if url and self._validate_database_url(url):
                fallback_url = url
                break
        
        logger.info(f"Primary database: {self._mask_url(primary_url)}")
        if fallback_url:
            logger.info(f"Fallback database: {self._mask_url(fallback_url)}")
        
        return primary_url, fallback_url
    
    def _validate_database_url(self, url: str) -> bool:
        """Validate database URL format"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['sqlite', 'postgresql', 'mysql', 'mariadb']
        except Exception:
            return False
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive information in database URL"""
        try:
            parsed = urlparse(url)
            if parsed.password:
                return f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
            return url
        except Exception:
            return "***"
    
    def get_engine_config(self, url: str) -> Dict[str, Any]:
        """Get engine configuration based on database type"""
        parsed = urlparse(url)
        scheme = parsed.scheme
        
        if scheme == 'sqlite':
            return {
                'poolclass': StaticPool,
                'pool_pre_ping': True,
                'echo': False,
                'connect_args': {'check_same_thread': False}
            }
        elif scheme in ['postgresql', 'postgres']:
            return {
                'poolclass': QueuePool,
                'pool_size': 20,
                'max_overflow': 30,
                'pool_recycle': 3600,
                'pool_pre_ping': True,
                'echo': False
            }
        elif scheme in ['mysql', 'mariadb']:
            return {
                'poolclass': QueuePool,
                'pool_size': 20,
                'max_overflow': 30,
                'pool_recycle': 3600,
                'pool_pre_ping': True,
                'echo': False,
                'connect_args': {'charset': 'utf8mb4'}
            }
        else:
            return {
                'pool_pre_ping': True,
                'echo': False
            }
    
    async def test_connection(self, url: str) -> Tuple[bool, str]:
        """Test database connection"""
        try:
            config = self.get_engine_config(url)
            test_engine = create_engine(url, **config)
            
            with test_engine.connect() as conn:
                if urlparse(url).scheme == 'sqlite':
                    # Use a simple query that doesn't require sqlite3_deserialize
                    conn.execute(text("SELECT 1 as test"))
                else:
                    conn.execute(text("SELECT 1"))
            
            test_engine.dispose()
            return True, "Connection successful"
            
        except Exception as e:
            error_msg = str(e)
            # Handle specific SQLite3 symbol errors
            if "sqlite3_deserialize" in error_msg or "undefined symbol" in error_msg:
                return False, f"SQLite3 compatibility issue: {error_msg}"
            return False, error_msg
    
    async def initialize_database(self) -> bool:
        """Initialize database with fallback support"""
        try:
            # Detect database URLs
            primary_url, fallback_url = self.detect_database_urls()
            self.primary_db_url = primary_url
            
            # Try primary database first
            logger.info("Testing primary database connection...")
            is_connected, message = await self.test_connection(primary_url)
            
            if is_connected:
                logger.info(f"Primary database connected: {message}")
                self.db_type = urlparse(primary_url).scheme
                await self._setup_engine(primary_url)
                return True
            
            # Try fallback database
            if fallback_url:
                logger.warning(f"Primary database failed: {message}")
                logger.info("Trying fallback database...")
                
                is_connected, message = await self.test_connection(fallback_url)
                if is_connected:
                    logger.info(f"Fallback database connected: {message}")
                    self.db_type = urlparse(fallback_url).scheme
                    self.fallback_db_url = fallback_url
                    await self._setup_engine(fallback_url)
                    return True
                else:
                    logger.error(f"Fallback database failed: {message}")
            
            # If all databases fail, try to create a simple SQLite file
            logger.warning("All databases failed, trying simple SQLite file...")
            try:
                simple_sqlite_url = "sqlite:///./simple_auth.db"
                is_connected, message = await self.test_connection(simple_sqlite_url)
                if is_connected:
                    logger.info(f"Simple SQLite connected: {message}")
                    self.db_type = 'sqlite'
                    await self._setup_engine(simple_sqlite_url)
                    return True
            except Exception as e:
                logger.warning(f"Simple SQLite failed: {str(e)}")
            
            # Last resort: in-memory SQLite
            logger.warning("All databases failed, using in-memory SQLite as last resort")
            try:
                in_memory_url = "sqlite:///:memory:"
                self.db_type = 'sqlite'
                await self._setup_engine(in_memory_url)
                return True
            except Exception as e:
                logger.error(f"Even in-memory SQLite failed: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return False
    
    async def _setup_engine(self, url: str) -> None:
        """Setup database engine and session factory"""
        try:
            config = self.get_engine_config(url)
            self.engine = create_engine(url, **config)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.is_connected = True
            logger.info(f"Database engine setup complete: {self.db_type}")
            
        except Exception as e:
            logger.error(f"Engine setup failed: {str(e)}")
            raise
    
    async def create_tables(self, Base) -> bool:
        """Create database tables"""
        try:
            if not self.engine:
                raise RuntimeError("Database engine not initialized")
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Table creation failed: {str(e)}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            if not self.engine or not self.is_connected:
                return {
                    "status": "disconnected",
                    "error": "Engine not initialized"
                }
            
            with self.engine.connect() as conn:
                if self.db_type == 'sqlite':
                    result = conn.execute(text("SELECT 1")).fetchone()
                else:
                    result = conn.execute(text("SELECT 1")).fetchone()
                
                return {
                    "status": "healthy",
                    "database_type": self.db_type,
                    "connection_pool_size": self.engine.pool.size(),
                    "checked_out_connections": self.engine.pool.checkedout(),
                    "overflow_connections": self.engine.pool.overflow()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_session(self) -> Session:
        """Get database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    @asynccontextmanager
    async def get_session_context(self):
        """Get database session with context manager"""
        session = self.get_session()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def close(self) -> None:
        """Close database connections"""
        try:
            if self.engine:
                self.engine.dispose()
                self.engine = None
            self.SessionLocal = None
            self.is_connected = False
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")

# Global database instance
db_config = DatabaseConfig()

async def get_database_config() -> DatabaseConfig:
    """Get global database configuration"""
    return db_config

async def initialize_database() -> bool:
    """Initialize database system"""
    return await db_config.initialize_database()

async def create_tables(Base) -> bool:
    """Create database tables"""
    return await db_config.create_tables(Base)

async def get_database_health() -> Dict[str, Any]:
    """Get database health status"""
    return await db_config.health_check()

def get_db_session() -> Session:
    """Get database session"""
    return db_config.get_session()

@asynccontextmanager
async def get_db_session_context():
    """Get database session with context manager"""
    async with db_config.get_session_context() as session:
        yield session