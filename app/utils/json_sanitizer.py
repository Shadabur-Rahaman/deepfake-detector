"""
JSON Sanitizer Module

This module provides functions to sanitize data structures to prevent JSON serialization errors.
It handles various data types and ensures they can be safely serialized to JSON.
"""

import json
import numpy as np
from typing import Any, Dict, List, Union
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


def sanitize_json_data(data: Any) -> Any:
    """
    Recursively sanitize data to ensure it can be safely serialized to JSON.
    
    Args:
        data: The data to sanitize (can be dict, list, or any other type)
        
    Returns:
        Sanitized data that can be safely serialized to JSON
    """
    if data is None:
        return None
    
    if isinstance(data, dict):
        return {str(key): sanitize_json_data(value) for key, value in data.items()}
    
    elif isinstance(data, (list, tuple)):
        return [sanitize_json_data(item) for item in data]
    
    elif isinstance(data, (np.integer, np.floating)):
        return data.item()
    
    elif isinstance(data, np.ndarray):
        return data.tolist()
    
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    
    elif isinstance(data, (int, float, str, bool)):
        return data
    
    elif hasattr(data, '__dict__'):
        # Handle custom objects by converting to dict
        try:
            return sanitize_json_data(data.__dict__)
        except Exception as e:
            logger.warning(f"Failed to serialize object {type(data)}: {e}")
            return str(data)
    
    else:
        # For any other type, try to convert to string
        try:
            # Test if it's JSON serializable
            json.dumps(data)
            return data
        except (TypeError, ValueError):
            logger.warning(f"Converting unsupported type {type(data)} to string")
            return str(data)


def sanitize_detection_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a detection result dictionary to ensure it can be safely serialized.
    
    Args:
        result: The detection result dictionary to sanitize
        
    Returns:
        Sanitized detection result dictionary
    """
    if not isinstance(result, dict):
        logger.warning(f"Expected dict for detection result, got {type(result)}")
        return {"error": "Invalid result format"}
    
    try:
        # Sanitize the entire result
        sanitized = sanitize_json_data(result)
        
        # Ensure required fields exist with safe defaults
        if not isinstance(sanitized, dict):
            return {"error": "Sanitization failed"}
        
        # Add default values for common detection result fields if missing
        defaults = {
            "is_deepfake": False,
            "confidence": 0.0,
            "status": "unknown",
            "message": "Detection completed"
        }
        
        for key, default_value in defaults.items():
            if key not in sanitized:
                sanitized[key] = default_value
        
        # Ensure confidence is a valid float
        if "confidence" in sanitized:
            try:
                sanitized["confidence"] = float(sanitized["confidence"])
                # Clamp confidence to valid range
                sanitized["confidence"] = max(0.0, min(1.0, sanitized["confidence"]))
            except (ValueError, TypeError):
                sanitized["confidence"] = 0.0
        
        # Ensure is_deepfake is a boolean
        if "is_deepfake" in sanitized:
            sanitized["is_deepfake"] = bool(sanitized["is_deepfake"])
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Error sanitizing detection result: {e}")
        return {
            "is_deepfake": False,
            "confidence": 0.0,
            "status": "error",
            "message": f"Sanitization error: {str(e)}"
        }


def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Safely serialize data to JSON string with proper error handling.
    
    Args:
        data: The data to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string representation of the data
    """
    try:
        sanitized_data = sanitize_json_data(data)
        return json.dumps(sanitized_data, **kwargs)
    except Exception as e:
        logger.error(f"JSON serialization failed: {e}")
        return json.dumps({"error": f"Serialization failed: {str(e)}"})


def validate_json_serializable(data: Any) -> bool:
    """
    Check if data can be safely serialized to JSON.
    
    Args:
        data: The data to validate
        
    Returns:
        True if data can be serialized, False otherwise
    """
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False
