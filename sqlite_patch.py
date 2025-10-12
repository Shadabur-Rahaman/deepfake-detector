#!/usr/bin/env python3
"""
SQLite3 Patch
Patches SQLite3 import issues.
"""

import sys
import logging

logger = logging.getLogger(__name__)

def patch_sqlite3():
    """Patch SQLite3 imports"""
    try:
        # Try pysqlite3 first
        import pysqlite3 as sqlite3
        logger.info("Using pysqlite3 for SQLite3 compatibility")
        sys.modules['sqlite3'] = sqlite3
        sys.modules['sqlite3.dbapi2'] = sqlite3.dbapi2
        return True
    except ImportError:
        try:
            # Fallback to built-in sqlite3
            import sqlite3
            logger.info("Using built-in sqlite3")
            return True
        except ImportError as e:
            logger.error(f"Failed to import any SQLite3 module: {e}")
            return False

# Apply patch
patch_sqlite3()
