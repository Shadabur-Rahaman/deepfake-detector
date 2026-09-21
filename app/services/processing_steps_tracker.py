"""
Processing Steps Tracker Module
Tracks and manages processing steps for deepfake detection tasks
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import numpy as np
import math

logger = logging.getLogger(__name__)

def sanitize_value(value):
    """Sanitize numpy types to Python native types for JSON serialization"""
    if isinstance(value, (np.floating, np.float32, np.float64, np.float16)):
        float_val = float(value.item() if hasattr(value, 'item') else value)
        if math.isnan(float_val) or math.isinf(float_val):
            return 0.0
        return float_val
    elif isinstance(value, (np.integer, np.int32, np.int64, np.int16, np.int8, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(value.item() if hasattr(value, 'item') else value)
    elif isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [sanitize_value(item) for item in value]
    elif isinstance(value, np.ndarray):
        return sanitize_value(value.tolist())
    return value

# Global storage for processing sessions
PROCESSING_SESSIONS: Dict[str, Dict[str, Any]] = {}

def create_processing_session(video_id: str, video_path: str) -> None:
    """
    Create a new processing session for a video
    
    Args:
        video_id: Unique identifier for the video
        video_path: Path to the video file
    """
    PROCESSING_SESSIONS[video_id] = {
        'video_id': video_id,
        'video_path': video_path,
        'start_time': datetime.now().isoformat(),
        'steps': {},
        'current_step': None,
        'overall_progress': 0,
        'status': 'active'
    }
    logger.info(f"📊 Created processing session for {video_id}")

def start_processing_step(video_id: str, step_name: str) -> None:
    """
    Start a new processing step
    
    Args:
        video_id: Unique identifier for the video
        step_name: Name of the processing step
    """
    if video_id not in PROCESSING_SESSIONS:
        logger.warning(f"⚠️ No processing session found for {video_id}")
        return
    
    PROCESSING_SESSIONS[video_id]['current_step'] = step_name
    PROCESSING_SESSIONS[video_id]['steps'][step_name] = {
        'name': step_name,
        'start_time': datetime.now().isoformat(),
        'status': 'running',
        'progress': 0,
        'message': '',
        'data': {}
    }
    logger.info(f"🔄 Started processing step '{step_name}' for {video_id}")

def update_processing_progress(video_id: str, step_name: str, progress: int, message: str = "") -> None:
    """
    Update progress for a processing step
    
    Args:
        video_id: Unique identifier for the video
        step_name: Name of the processing step
        progress: Progress percentage (0-100)
        message: Optional progress message
    """
    if video_id not in PROCESSING_SESSIONS:
        logger.warning(f"⚠️ No processing session found for {video_id}")
        return
    
    if step_name not in PROCESSING_SESSIONS[video_id]['steps']:
        # Create step if it doesn't exist
        start_processing_step(video_id, step_name)
    
    PROCESSING_SESSIONS[video_id]['steps'][step_name]['progress'] = progress
    PROCESSING_SESSIONS[video_id]['steps'][step_name]['message'] = message
    PROCESSING_SESSIONS[video_id]['overall_progress'] = progress
    
    logger.info(f"📈 Updated progress for '{step_name}' in {video_id}: {progress}% - {message}")

def complete_processing_step(video_id: str, step_name: str, data: Dict[str, Any] = None) -> None:
    """
    Mark a processing step as completed
    
    Args:
        video_id: Unique identifier for the video
        step_name: Name of the processing step
        data: Optional data to store with the step
    """
    if video_id not in PROCESSING_SESSIONS:
        logger.warning(f"⚠️ No processing session found for {video_id}")
        return
    
    if step_name not in PROCESSING_SESSIONS[video_id]['steps']:
        start_processing_step(video_id, step_name)
    
    PROCESSING_SESSIONS[video_id]['steps'][step_name].update({
        'status': 'completed',
        'end_time': datetime.now().isoformat(),
        'progress': 100,
        'data': data or {}
    })
    
    logger.info(f"✅ Completed processing step '{step_name}' for {video_id}")

def fail_processing_step(video_id: str, step_name: str, error_message: str) -> None:
    """
    Mark a processing step as failed
    
    Args:
        video_id: Unique identifier for the video
        step_name: Name of the processing step
        error_message: Error message describing the failure
    """
    if video_id not in PROCESSING_SESSIONS:
        logger.warning(f"⚠️ No processing session found for {video_id}")
        return
    
    if step_name not in PROCESSING_SESSIONS[video_id]['steps']:
        start_processing_step(video_id, step_name)
    
    PROCESSING_SESSIONS[video_id]['steps'][step_name].update({
        'status': 'failed',
        'end_time': datetime.now().isoformat(),
        'error': error_message,
        'data': {'error': error_message}
    })
    
    logger.error(f"❌ Failed processing step '{step_name}' for {video_id}: {error_message}")

def skip_processing_step(video_id: str, step_name: str, reason: str) -> None:
    """
    Mark a processing step as skipped
    
    Args:
        video_id: Unique identifier for the video
        step_name: Name of the processing step
        reason: Reason for skipping the step
    """
    if video_id not in PROCESSING_SESSIONS:
        logger.warning(f"⚠️ No processing session found for {video_id}")
        return
    
    if step_name not in PROCESSING_SESSIONS[video_id]['steps']:
        start_processing_step(video_id, step_name)
    
    PROCESSING_SESSIONS[video_id]['steps'][step_name].update({
        'status': 'skipped',
        'end_time': datetime.now().isoformat(),
        'reason': reason,
        'data': {'reason': reason}
    })
    
    logger.info(f"⏭️ Skipped processing step '{step_name}' for {video_id}: {reason}")

def get_processing_markdown(video_id: str) -> str:
    """
    Generate markdown report of processing steps
    
    Args:
        video_id: Unique identifier for the video
        
    Returns:
        Markdown formatted string of processing steps
    """
    if video_id not in PROCESSING_SESSIONS:
        return "No processing session found"
    
    session = PROCESSING_SESSIONS[video_id]
    markdown = f"# Processing Report for {video_id}\n\n"
    markdown += f"**Video Path:** `{session['video_path']}`\n"
    markdown += f"**Start Time:** {session['start_time']}\n"
    markdown += f"**Overall Progress:** {session['overall_progress']}%\n\n"
    
    markdown += "## Processing Steps\n\n"
    
    for step_name, step_data in session['steps'].items():
        status_emoji = {
            'running': '🔄',
            'completed': '✅',
            'failed': '❌',
            'skipped': '⏭️'
        }.get(step_data['status'], '❓')
        
        markdown += f"### {status_emoji} {step_name}\n"
        markdown += f"- **Status:** {step_data['status']}\n"
        markdown += f"- **Progress:** {step_data.get('progress', 0)}%\n"
        
        if step_data.get('start_time'):
            markdown += f"- **Start Time:** {step_data['start_time']}\n"
        
        if step_data.get('end_time'):
            markdown += f"- **End Time:** {step_data['end_time']}\n"
        
        if step_data.get('message'):
            markdown += f"- **Message:** {step_data['message']}\n"
        
        if step_data.get('error'):
            markdown += f"- **Error:** {step_data['error']}\n"
        
        if step_data.get('reason'):
            markdown += f"- **Reason:** {step_data['reason']}\n"
        
        if step_data.get('data'):
            try:
                sanitized_data = sanitize_value(step_data['data'])
                markdown += f"- **Data:** ```json\n{json.dumps(sanitized_data, indent=2)}\n```\n"
            except Exception as e:
                logger.warning(f"Failed to serialize step data: {e}")
                markdown += f"- **Data:** (serialization failed)\n"
        
        markdown += "\n"
    
    return markdown

def get_processing_session(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Get processing session data
    
    Args:
        video_id: Unique identifier for the video
        
    Returns:
        Processing session data or None if not found
    """
    return PROCESSING_SESSIONS.get(video_id)

def cleanup_processing_session(video_id: str) -> None:
    """
    Clean up processing session data
    
    Args:
        video_id: Unique identifier for the video
    """
    if video_id in PROCESSING_SESSIONS:
        del PROCESSING_SESSIONS[video_id]
        logger.info(f"🧹 Cleaned up processing session for {video_id}")

def get_all_processing_sessions() -> Dict[str, Dict[str, Any]]:
    """
    Get all processing sessions
    
    Returns:
        Dictionary of all processing sessions
    """
    return PROCESSING_SESSIONS.copy()
