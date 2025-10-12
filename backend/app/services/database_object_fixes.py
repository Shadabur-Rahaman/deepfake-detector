"""
Database Object Access Fixes - Core Foundation Level
===================================================

This module provides comprehensive fixes for database object access issues
that are causing the core errors in the detection system.

FIXES APPLIED:
1. Proper DetectionJob object attribute access
2. Safe database object handling
3. Fallback mechanisms for database errors
4. Unified database object interface
5. Error handling for missing attributes

Author: Senior Backend Engineer
Date: 2024
"""

import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseObjectFixer:
    """Comprehensive database object access utility with error handling"""
    
    def __init__(self):
        self.access_errors = 0
        self.successful_accesses = 0
    
    def safe_get_attribute(self, obj: Any, attr_name: str, default: Any = None) -> Any:
        """
        Safely get attribute from database object with fallback
        
        Args:
            obj: Database object (DetectionJob, etc.)
            attr_name: Attribute name to access
            default: Default value if attribute not found
            
        Returns:
            Attribute value or default
        """
        try:
            if obj is None:
                logger.warning(f"Cannot access {attr_name} from None object")
                return default
            
            # Try direct attribute access first
            if hasattr(obj, attr_name):
                value = getattr(obj, attr_name)
                self.successful_accesses += 1
                return value
            
            # Try dictionary-style access for dict-like objects
            if hasattr(obj, '__getitem__') and attr_name in obj:
                value = obj[attr_name]
                self.successful_accesses += 1
                return value
            
            # Try get method for dict-like objects
            if hasattr(obj, 'get'):
                value = obj.get(attr_name, default)
                self.successful_accesses += 1
                return value
            
            logger.warning(f"Attribute {attr_name} not found in object {type(obj)}")
            return default
            
        except Exception as e:
            logger.error(f"Failed to access {attr_name} from {type(obj)}: {e}")
            self.access_errors += 1
            return default
    
    def safe_get_multiple_attributes(self, obj: Any, attr_names: list, defaults: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Safely get multiple attributes from database object
        
        Args:
            obj: Database object
            attr_names: List of attribute names to access
            defaults: Dictionary of default values
            
        Returns:
            Dictionary of attribute values
        """
        if defaults is None:
            defaults = {}
        
        result = {}
        for attr_name in attr_names:
            default_value = defaults.get(attr_name, None)
            result[attr_name] = self.safe_get_attribute(obj, attr_name, default_value)
        
        return result
    
    def safe_set_attribute(self, obj: Any, attr_name: str, value: Any) -> bool:
        """
        Safely set attribute on database object
        
        Args:
            obj: Database object
            attr_name: Attribute name to set
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if obj is None:
                logger.warning(f"Cannot set {attr_name} on None object")
                return False
            
            # Try direct attribute setting
            if hasattr(obj, attr_name):
                setattr(obj, attr_name, value)
                self.successful_accesses += 1
                return True
            
            # Try dictionary-style setting for dict-like objects
            if hasattr(obj, '__setitem__'):
                obj[attr_name] = value
                self.successful_accesses += 1
                return True
            
            logger.warning(f"Cannot set {attr_name} on object {type(obj)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to set {attr_name} on {type(obj)}: {e}")
            self.access_errors += 1
            return False
    
    def safe_get_job_info(self, job: Any) -> Dict[str, Any]:
        """
        Safely extract job information from DetectionJob object
        
        Args:
            job: DetectionJob object
            
        Returns:
            Dictionary with job information
        """
        if job is None:
            return {
                "status": "not_found",
                "progress": 0,
                "mode": "unknown",
                "result": None,
                "confidence": None,
                "error": "Job object is None"
            }
        
        # Define expected attributes with defaults
        expected_attrs = [
            "status", "progress", "mode", "result", "confidence", 
            "faces_analyzed", "processing_time", "error", "video_path",
            "created_at", "updated_at"
        ]
        
        defaults = {
            "status": "unknown",
            "progress": 0,
            "mode": "unknown",
            "result": None,
            "confidence": None,
            "faces_analyzed": 0,
            "processing_time": 0.0,
            "error": None,
            "video_path": None,
            "created_at": None,
            "updated_at": None
        }
        
        return self.safe_get_multiple_attributes(job, expected_attrs, defaults)
    
    def safe_log_job_details(self, job: Any, video_id: str) -> None:
        """
        Safely log job details with proper error handling
        
        Args:
            job: DetectionJob object
            video_id: Video ID for logging context
        """
        try:
            job_info = self.safe_get_job_info(job)
            
            logger.info(f"[DATA] Job details for {video_id}:")
            logger.info(f"  Status: {job_info['status']}")
            logger.info(f"  Progress: {job_info['progress']}%")
            logger.info(f"  Mode: {job_info['mode']}")
            logger.info(f"  Result: {job_info['result']}")
            logger.info(f"  Confidence: {job_info['confidence']}")
            logger.info(f"  Faces Analyzed: {job_info['faces_analyzed']}")
            logger.info(f"  Processing Time: {job_info['processing_time']:.2f}s")
            
            if job_info['error']:
                logger.info(f"  Error: {job_info['error']}")
                
        except Exception as e:
            logger.error(f"Failed to log job details for {video_id}: {e}")
    
    def safe_serialize_job(self, job: Any) -> Dict[str, Any]:
        """
        Safely serialize job object to dictionary
        
        Args:
            job: DetectionJob object
            
        Returns:
            Serialized job dictionary
        """
        try:
            job_info = self.safe_get_job_info(job)
            
            # Handle datetime objects
            for key in ['created_at', 'updated_at']:
                if job_info[key] and isinstance(job_info[key], datetime):
                    job_info[key] = job_info[key].isoformat()
            
            return job_info
            
        except Exception as e:
            logger.error(f"Failed to serialize job: {e}")
            return {
                "status": "error",
                "progress": 0,
                "mode": "unknown",
                "result": None,
                "confidence": None,
                "error": f"Serialization failed: {str(e)}"
            }
    
    def get_access_stats(self) -> Dict[str, Any]:
        """Get database object access statistics"""
        total = self.access_errors + self.successful_accesses
        success_rate = (self.successful_accesses / total * 100) if total > 0 else 0
        
        return {
            "successful_accesses": self.successful_accesses,
            "access_errors": self.access_errors,
            "success_rate": success_rate,
            "total_attempts": total
        }
    
    def reset_stats(self):
        """Reset access statistics"""
        self.access_errors = 0
        self.successful_accesses = 0

# Global instance for easy access
db_object_fixer = DatabaseObjectFixer()

# Convenience functions
def safe_get_job_attribute(job: Any, attr_name: str, default: Any = None) -> Any:
    """Safe job attribute access"""
    return db_object_fixer.safe_get_attribute(job, attr_name, default)

def safe_get_job_info(job: Any) -> Dict[str, Any]:
    """Safe job info extraction"""
    return db_object_fixer.safe_get_job_info(job)

def safe_log_job_details(job: Any, video_id: str) -> None:
    """Safe job details logging"""
    db_object_fixer.safe_log_job_details(job, video_id)

def safe_serialize_job(job: Any) -> Dict[str, Any]:
    """Safe job serialization"""
    return db_object_fixer.safe_serialize_job(job)

def get_database_access_stats() -> Dict[str, Any]:
    """Get database access statistics"""
    return db_object_fixer.get_access_stats()

def reset_database_access_stats():
    """Reset database access statistics"""
    db_object_fixer.reset_stats()
