#!/usr/bin/env python3
"""
SQLite3 Workaround for Linux
Comprehensive workaround for SQLite3 compatibility issues.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

class SQLite3Workaround:
    """Comprehensive SQLite3 workaround"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.db_type = None
        self.is_working = False
        self._patched = False
    
    def patch_sqlite3(self) -> bool:
        """Patch SQLite3 imports"""
        if self._patched:
            return True
            
        try:
            # Try pysqlite3 first
            import pysqlite3 as sqlite3
            logger.info("Using pysqlite3 for SQLite3 compatibility")
            sys.modules['sqlite3'] = sqlite3
            sys.modules['sqlite3.dbapi2'] = sqlite3.dbapi2
            self._patched = True
            return True
        except ImportError:
            try:
                # Try to patch the built-in sqlite3
                import sqlite3
                logger.info("Using built-in sqlite3")
                self._patched = True
                return True
            except ImportError as e:
                logger.error(f"Failed to import any SQLite3 module: {e}")
                return False
    
    def setup_alternative_database(self) -> bool:
        """Setup alternative database when SQLite3 fails"""
        logger.info("Setting up alternative database...")
        
        # Try PostgreSQL first
        postgres_url = os.getenv('POSTGRES_URL', 'postgresql://postgres:password@localhost:5432/ifake_auth')
        try:
            engine = create_engine(postgres_url, echo=False)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("PostgreSQL connection successful")
            self.engine = engine
            self.SessionLocal = sessionmaker(bind=engine)
            self.db_type = "postgresql"
            return True
        except Exception as e:
            logger.warning(f"PostgreSQL failed: {e}")
        
        # Try MySQL
        mysql_url = os.getenv('MYSQL_URL', 'mysql+pymysql://root:password@localhost:3306/ifake_auth')
        try:
            engine = create_engine(mysql_url, echo=False)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("MySQL connection successful")
            self.engine = engine
            self.SessionLocal = sessionmaker(bind=engine)
            self.db_type = "mysql"
            return True
        except Exception as e:
            logger.warning(f"MySQL failed: {e}")
        
        # Try in-memory SQLite with workaround
        try:
            # Use a different approach for in-memory SQLite
            engine = create_engine(
                "sqlite:///:memory:",
                echo=False,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                }
            )
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("In-memory SQLite with workaround successful")
            self.engine = engine
            self.SessionLocal = sessionmaker(bind=engine)
            self.db_type = "sqlite_memory"
            return True
        except Exception as e:
            logger.error(f"All database options failed: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize the workaround"""
        logger.info("Initializing SQLite3 workaround...")
        
        # Try to patch SQLite3 first
        if self.patch_sqlite3():
            self.is_working = True
            return True
        
        # Try alternative databases
        if self.setup_alternative_database():
            self.is_working = True
            return True
        
        logger.error("All SQLite3 workarounds failed")
        return False
    
    def get_database_url(self) -> str:
        """Get the working database URL"""
        if self.db_type == "postgresql":
            return os.getenv('POSTGRES_URL', 'postgresql://postgres:password@localhost:5432/ifake_auth')
        elif self.db_type == "mysql":
            return os.getenv('MYSQL_URL', 'mysql+pymysql://root:password@localhost:3306/ifake_auth')
        else:
            return "sqlite:///:memory:"

# Global workaround instance
sqlite3_workaround = SQLite3Workaround()

def apply_workaround():
    """Apply the SQLite3 workaround"""
    return sqlite3_workaround.initialize()

def get_working_database_config():
    """Get working database configuration"""
    if sqlite3_workaround.is_working:
        return {
            "engine": sqlite3_workaround.engine,
            "SessionLocal": sqlite3_workaround.SessionLocal,
            "db_type": sqlite3_workaround.db_type,
            "database_url": sqlite3_workaround.get_database_url()
        }
    return None

# Apply workaround on import
apply_workaround()
