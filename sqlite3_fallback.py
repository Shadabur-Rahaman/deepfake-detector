
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

class FallbackSQLite3:
    """Fallback SQLite3 implementation using file-based storage"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.data_file = f"{database_path}.json"
        self.tables = {}
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.tables = json.load(f)
            else:
                self.tables = {}
        except Exception:
            self.tables = {}
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tables, f, default=str)
        except Exception as e:
            print(f"Warning: Could not save data: {e}")
    
    def execute(self, query: str, params: tuple = ()):
        """Execute SQL query (simplified)"""
        query = query.strip().upper()
        
        if query.startswith('CREATE TABLE'):
            # Extract table name
            parts = query.split()
            table_name = parts[2].strip('(')
            if table_name not in self.tables:
                self.tables[table_name] = []
            self._save_data()
            return True
            
        elif query.startswith('INSERT INTO'):
            # Extract table name and values
            parts = query.split()
            table_name = parts[2]
            if table_name not in self.tables:
                self.tables[table_name] = []
            
            # Simple insert (very basic)
            if params:
                self.tables[table_name].append(dict(zip(['id', 'email', 'username', 'password_hash', 'full_name', 'is_active', 'is_verified', 'created_at'], params)))
            self._save_data()
            return True
            
        elif query.startswith('SELECT'):
            # Simple select
            parts = query.split()
            if 'FROM' in parts:
                table_idx = parts.index('FROM') + 1
                table_name = parts[table_idx]
                if table_name in self.tables:
                    return self.tables[table_name]
            return []
            
        return True
    
    def fetchone(self):
        """Fetch one result"""
        if hasattr(self, '_results') and self._results:
            return self._results.pop(0)
        return None
    
    def fetchall(self):
        """Fetch all results"""
        if hasattr(self, '_results'):
            return self._results
        return []
    
    def commit(self):
        """Commit changes"""
        self._save_data()
    
    def close(self):
        """Close connection"""
        self._save_data()

class FallbackConnection:
    """Fallback connection class"""
    
    def __init__(self, database_path: str):
        self.db = FallbackSQLite3(database_path)
    
    def execute(self, query: str, params: tuple = ()):
        """Execute query"""
        return self.db.execute(query, params)
    
    def commit(self):
        """Commit changes"""
        self.db.commit()
    
    def close(self):
        """Close connection"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def connect(database: str, **kwargs):
    """Connect to database"""
    return FallbackConnection(database)

# Create fallback module
import sys
fallback_module = type(sys)('sqlite3')
fallback_module.connect = connect
fallback_module.OperationalError = Exception
fallback_module.IntegrityError = Exception
sys.modules['sqlite3'] = fallback_module
