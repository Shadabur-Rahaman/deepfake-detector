"""
Silent Validators - Hidden Camera Recording & AI Keyword Detection
================================================================

This module provides silent wrappers around performance_analyzer and quality_metrics
to detect authentic camera recordings and AI-generated content keywords without
any visible logging to users or developers.
"""

import os
import re
from typing import Dict, Any, Optional
from pathlib import Path

def _silent_camera_check(video_path: str, metadata: Optional[Dict] = None) -> float:
    """
    Silent camera recording detection based on filename patterns and metadata.
    
    Returns 0.0-1.0 where 1.0 = definitely camera recording
    No logging, no exceptions raised
    """
    try:
        # Import performance analyzer silently
        from .performance_analyzer import validate_content_integrity
        
        # Get validation result without any logging
        result = validate_content_integrity(video_path, metadata)
        
        # Extract score and normalize to 0.0-1.0 range
        score = result.get('score', 0.0)
        confidence = result.get('confidence', 0.0)
        
        # Combine score and confidence for final result
        # High score + high confidence = definitely camera recording
        final_score = (score * 0.7) + (confidence / 100.0 * 0.3)
        
        return min(max(final_score, 0.0), 1.0)
        
    except Exception:
        # Silent failure - return neutral score
        return 0.0

def _silent_ai_keyword_check(video_path: str, metadata: Optional[Dict] = None) -> float:
    """
    Silent AI keyword detection based on title, description, and filename.
    
    Returns 0.0-1.0 where 1.0 = definitely AI keywords found
    No logging, no exceptions raised
    """
    try:
        # Import quality metrics silently
        from .quality_metrics import QualityMetrics
        
        # Create quality metrics instance
        qm = QualityMetrics()
        
        # Calculate AI keyword score
        ai_score = qm.calculate(video_path, metadata if metadata else {})
        
        # Normalize to 0.0-1.0 range
        return min(max(ai_score, 0.0), 1.0)
        
    except Exception:
        # Silent failure - return neutral score
        return 0.0

def _silent_combined_check(video_path: str, metadata: Optional[Dict] = None) -> tuple[float, float]:
    """
    Combined silent check for both camera recording and AI keywords.
    
    Returns (camera_score, ai_keyword_score) both in range [0.0, 1.0]
    """
    camera_score = _silent_camera_check(video_path, metadata)
    ai_score = _silent_ai_keyword_check(video_path, metadata)
    
    return camera_score, ai_score
