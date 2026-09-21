"""
Processing Stage Tracker Module
Tracks processing stages for hybrid detection
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Global storage for processing stages
PROCESSING_STAGES: Dict[str, Dict[str, Any]] = {}

class ProcessingStageTracker:
    """
    Tracks processing stages for hybrid detection
    """
    
    def __init__(self, video_id: str):
        """
        Initialize processing stage tracker
        
        Args:
            video_id: Unique identifier for the video
        """
        self.video_id = video_id
        self.stages = {}
        self.current_stage = None
        self.start_time = datetime.now()
        
        # Initialize in global storage
        PROCESSING_STAGES[video_id] = {
            'video_id': video_id,
            'stages': self.stages,
            'current_stage': self.current_stage,
            'start_time': self.start_time.isoformat(),
            'status': 'active'
        }
        
        logger.info(f"📊 Processing stage tracker initialized for {video_id}")
    
    def start_stage(self, stage_name: str, description: str = "") -> None:
        """
        Start a new processing stage
        
        Args:
            stage_name: Name of the stage
            description: Optional description
        """
        self.current_stage = stage_name
        self.stages[stage_name] = {
            'name': stage_name,
            'description': description,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'progress': 0,
            'message': '',
            'data': {}
        }
        
        # Update global storage
        PROCESSING_STAGES[self.video_id]['current_stage'] = stage_name
        PROCESSING_STAGES[self.video_id]['stages'] = self.stages
        
        logger.info(f"🔄 Started stage '{stage_name}' for {self.video_id}")
    
    def update_stage_progress(self, stage_name: str, progress: int, message: str = "") -> None:
        """
        Update progress for a stage
        
        Args:
            stage_name: Name of the stage
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        if stage_name not in self.stages:
            self.start_stage(stage_name)
        
        self.stages[stage_name]['progress'] = progress
        self.stages[stage_name]['message'] = message
        
        # Update global storage
        PROCESSING_STAGES[self.video_id]['stages'] = self.stages
        
        logger.info(f"📈 Updated stage '{stage_name}' progress: {progress}% - {message}")
    
    def complete_stage(self, stage_name: str, data: Dict[str, Any] = None) -> None:
        """
        Mark a stage as completed
        
        Args:
            stage_name: Name of the stage
            data: Optional data to store with the stage
        """
        if stage_name not in self.stages:
            self.start_stage(stage_name)
        
        self.stages[stage_name].update({
            'status': 'completed',
            'end_time': datetime.now().isoformat(),
            'progress': 100,
            'data': data or {}
        })
        
        # Update global storage
        PROCESSING_STAGES[self.video_id]['stages'] = self.stages
        
        logger.info(f"✅ Completed stage '{stage_name}' for {self.video_id}")
    
    def fail_stage(self, stage_name: str, error_message: str) -> None:
        """
        Mark a stage as failed
        
        Args:
            stage_name: Name of the stage
            error_message: Error message describing the failure
        """
        if stage_name not in self.stages:
            self.start_stage(stage_name)
        
        self.stages[stage_name].update({
            'status': 'failed',
            'end_time': datetime.now().isoformat(),
            'error': error_message,
            'data': {'error': error_message}
        })
        
        # Update global storage
        PROCESSING_STAGES[self.video_id]['stages'] = self.stages
        
        logger.error(f"❌ Failed stage '{stage_name}' for {self.video_id}: {error_message}")
    
    def skip_stage(self, stage_name: str, reason: str) -> None:
        """
        Mark a stage as skipped
        
        Args:
            stage_name: Name of the stage
            reason: Reason for skipping the stage
        """
        if stage_name not in self.stages:
            self.start_stage(stage_name)
        
        self.stages[stage_name].update({
            'status': 'skipped',
            'end_time': datetime.now().isoformat(),
            'reason': reason,
            'data': {'reason': reason}
        })
        
        # Update global storage
        PROCESSING_STAGES[self.video_id]['stages'] = self.stages
        
        logger.info(f"⏭️ Skipped stage '{stage_name}' for {self.video_id}: {reason}")
    
    def get_stage_info(self, stage_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific stage
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            Stage information or None if not found
        """
        return self.stages.get(stage_name)
    
    def get_all_stages(self) -> Dict[str, Any]:
        """
        Get information about all stages
        
        Returns:
            Dictionary of all stages
        """
        return self.stages.copy()
    
    def get_current_stage(self) -> Optional[str]:
        """
        Get the current stage name
        
        Returns:
            Current stage name or None
        """
        return self.current_stage
    
    def get_overall_progress(self) -> int:
        """
        Calculate overall progress across all stages
        
        Returns:
            Overall progress percentage
        """
        if not self.stages:
            return 0
        
        total_progress = sum(stage.get('progress', 0) for stage in self.stages.values())
        return total_progress // len(self.stages)
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the processing stages
        
        Returns:
            Processing summary
        """
        completed_stages = sum(1 for stage in self.stages.values() if stage.get('status') == 'completed')
        failed_stages = sum(1 for stage in self.stages.values() if stage.get('status') == 'failed')
        skipped_stages = sum(1 for stage in self.stages.values() if stage.get('status') == 'skipped')
        running_stages = sum(1 for stage in self.stages.values() if stage.get('status') == 'running')
        
        return {
            'video_id': self.video_id,
            'total_stages': len(self.stages),
            'completed_stages': completed_stages,
            'failed_stages': failed_stages,
            'skipped_stages': skipped_stages,
            'running_stages': running_stages,
            'overall_progress': self.get_overall_progress(),
            'current_stage': self.current_stage,
            'start_time': self.start_time.isoformat(),
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'stages': self.stages  # Add the missing 'stages' key
        }
    
    def cleanup(self) -> None:
        """
        Clean up processing stage data
        """
        if self.video_id in PROCESSING_STAGES:
            del PROCESSING_STAGES[self.video_id]
        logger.info(f"🧹 Cleaned up processing stages for {self.video_id}")

def get_processing_tracker(video_id: str) -> ProcessingStageTracker:
    """
    Get or create a processing stage tracker for a video
    
    Args:
        video_id: Unique identifier for the video
        
    Returns:
        ProcessingStageTracker instance
    """
    if video_id not in PROCESSING_STAGES:
        return ProcessingStageTracker(video_id)
    else:
        # Return existing tracker
        tracker = ProcessingStageTracker.__new__(ProcessingStageTracker)
        tracker.video_id = video_id
        tracker.stages = PROCESSING_STAGES[video_id]['stages']
        tracker.current_stage = PROCESSING_STAGES[video_id]['current_stage']
        tracker.start_time = datetime.fromisoformat(PROCESSING_STAGES[video_id]['start_time'])
        return tracker

def get_all_processing_stages() -> Dict[str, Dict[str, Any]]:
    """
    Get all processing stages
    
    Returns:
        Dictionary of all processing stages
    """
    return PROCESSING_STAGES.copy()

def cleanup_processing_stages(video_id: str) -> None:
    """
    Clean up processing stages for a specific video
    
    Args:
        video_id: Unique identifier for the video
    """
    if video_id in PROCESSING_STAGES:
        del PROCESSING_STAGES[video_id]
        logger.info(f"🧹 Cleaned up processing stages for {video_id}")
