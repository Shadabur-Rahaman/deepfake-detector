"""
JSON Sanitization Utility for Deepfake Detection API
==================================================

This module provides utilities to sanitize data before JSON serialization,
preventing "Out of range float values are not JSON compliant" errors.

The error occurs when NaN, Infinity, or -Infinity values are present in the data.
"""

import math
import numpy as np
from typing import Any, Dict, List, Union
import logging

logger = logging.getLogger(__name__)

def sanitize_float(value: Union[float, int, np.number]) -> float:
    """
    Sanitize a single float value to be JSON-compliant.
    
    Args:
        value: The float value to sanitize
        
    Returns:
        JSON-compliant float value
    """
    try:
        # Handle numpy types
        if hasattr(value, 'item'):
            value = value.item()
        
        # Convert to float
        float_value = float(value)
        
        # Check for problematic values
        if math.isnan(float_value):
            logger.warning(f"NaN value detected and replaced with 0.0: {value}")
            return 0.0
        elif math.isinf(float_value):
            if float_value > 0:
                logger.warning(f"Positive infinity detected and replaced with 1.0: {value}")
                return 1.0
            else:
                logger.warning(f"Negative infinity detected and replaced with 0.0: {value}")
                return 0.0
        else:
            # Return the value as-is (don't clamp all floats to [0,1])
            return float_value
            
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid float value detected and replaced with 0.0: {value}, error: {e}")
        return 0.0

def sanitize_json_data(data: Any) -> Any:
    """
    Recursively sanitize data structure to be JSON-compliant.
    
    Args:
        data: The data structure to sanitize
        
    Returns:
        Sanitized data structure
    """
    try:
        if isinstance(data, dict):
            return {key: sanitize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [sanitize_json_data(item) for item in data]
        elif isinstance(data, (float, int, np.number)):
            return sanitize_float(data)
        elif isinstance(data, np.ndarray):
            # Convert numpy array to list and sanitize each element
            return [sanitize_float(item) for item in data.flatten()]
        elif isinstance(data, tuple):
            return tuple(sanitize_json_data(item) for item in data)
        else:
            # For other types (str, bool, None), return as-is
            return data
            
    except Exception as e:
        logger.error(f"Error sanitizing data: {e}")
        return None

def sanitize_detection_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize detection result specifically for deepfake detection API.
    
    Args:
        result: The detection result dictionary
        
    Returns:
        Sanitized detection result
    """
    try:
        sanitized = sanitize_json_data(result)
        
        # Ensure critical fields are present and valid
        if isinstance(sanitized, dict):
            # Ensure confidence is a valid float (clamp to [0,1] for confidence only)
            if 'confidence' in sanitized:
                conf = sanitized['confidence']
                if isinstance(conf, (int, float, np.number)):
                    conf_float = float(conf)
                    if math.isnan(conf_float) or math.isinf(conf_float):
                        sanitized['confidence'] = 0.0
                    else:
                        sanitized['confidence'] = max(0.0, min(1.0, conf_float))
            
            # Ensure processing_time is valid (don't clamp to [0,1])
            if 'processing_time' in sanitized:
                time_val = sanitized['processing_time']
                if isinstance(time_val, (int, float, np.number)):
                    time_float = float(time_val)
                    if math.isnan(time_float) or math.isinf(time_float):
                        sanitized['processing_time'] = 0.0
                    else:
                        sanitized['processing_time'] = max(0.0, time_float)  # Only ensure non-negative
            
            # Ensure faces_detected is valid (don't clamp to [0,1])
            if 'faces_detected' in sanitized:
                faces = sanitized['faces_detected']
                if isinstance(faces, (int, float, np.number)):
                    faces_float = float(faces)
                    if math.isnan(faces_float) or math.isinf(faces_float):
                        sanitized['faces_detected'] = 0
                    else:
                        sanitized['faces_detected'] = max(0, int(faces_float))  # Only ensure non-negative
            
            # Sanitize nested structures
            for key in ['ai_analysis', 'ensemble_score', 'final_composite_score']:
                if key in sanitized and isinstance(sanitized[key], dict):
                    sanitized[key] = sanitize_json_data(sanitized[key])
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Error sanitizing detection result: {e}")
        # Return a safe fallback result
        return {
            'video_id': result.get('video_id', 'unknown'),
            'status': 'completed',
            'prediction': 'Error',
            'confidence': 0.0,
            'faces_detected': 0,
            'processing_time': 0.0,
            'message': 'Analysis completed with sanitization',
            'error': 'Data sanitization applied'
        }

def validate_json_compliance(data: Any) -> bool:
    """
    Validate that data is JSON-compliant.
    
    Args:
        data: The data to validate
        
    Returns:
        True if data is JSON-compliant, False otherwise
    """
    try:
        import json
        json.dumps(data)
        return True
    except (ValueError, TypeError):
        return False
