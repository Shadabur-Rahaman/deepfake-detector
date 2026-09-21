"""
Processing Steps Tracker - Markdown-Formatted Progress Tracking
============================================================

This module provides comprehensive step-by-step processing tracking with markdown formatting
for both API responses and WebSocket messages. It tracks each processing step with timestamps
and provides detailed progress information.

Features:
- Markdown-formatted step tracking
- Real-time progress updates
- Model-specific progress tracking
- Timing information for each step
- Support for both sync and async operations
- Integration with WebSocket and API responses
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
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

class StepStatus(Enum):
    """Status of processing steps"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class StepType(Enum):
    """Type of processing steps"""
    VIDEO_UPLOAD = "video_upload"
    FACE_EXTRACTION = "face_extraction"
    MODEL_LOADING = "model_loading"
    MODEL_ANALYSIS = "model_analysis"
    ENSEMBLE_FUSION = "ensemble_fusion"
    VALIDATION = "validation"
    FINAL_RESULT = "final_result"

@dataclass
class ProcessingStep:
    """Individual processing step"""
    id: str
    name: str
    description: str
    step_type: StepType
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    progress_percentage: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    model_name: Optional[str] = None
    sub_steps: List['ProcessingStep'] = field(default_factory=list)

    def start(self):
        """Mark step as started"""
        self.status = StepStatus.IN_PROGRESS
        self.start_time = time.time()
        self.progress_percentage = 0.0

    def update_progress(self, percentage: float, details: Optional[Dict[str, Any]] = None):
        """Update step progress"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        if details:
            # Sanitize all values before storing
            sanitized_details = sanitize_value(details)
            self.details.update(sanitized_details)

    def complete(self, details: Optional[Dict[str, Any]] = None):
        """Mark step as completed"""
        self.status = StepStatus.COMPLETED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.progress_percentage = 100.0
        if details:
            # Sanitize all values before storing
            sanitized_details = sanitize_value(details)
            self.details.update(sanitized_details)

    def fail(self, error_message: str):
        """Mark step as failed"""
        self.status = StepStatus.FAILED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.error_message = error_message

    def skip(self, reason: Optional[str] = None):
        """Mark step as skipped"""
        self.status = StepStatus.SKIPPED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        if reason:
            self.details['skip_reason'] = reason

@dataclass
class ProcessingSession:
    """Complete processing session with all steps"""
    session_id: str
    video_id: str
    video_path: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    steps: List[ProcessingStep] = field(default_factory=list)
    current_step: Optional[ProcessingStep] = None
    overall_progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: ProcessingStep) -> ProcessingStep:
        """Add a processing step"""
        self.steps.append(step)
        return step

    def start_step(self, step_id: str):
        """Start a specific step"""
        for step in self.steps:
            if step.id == step_id:
                step.start()
                self.current_step = step
                self._update_overall_progress()
                break

    def complete_step(self, step_id: str, details: Optional[Dict[str, Any]] = None):
        """Complete a specific step"""
        for step in self.steps:
            if step.id == step_id:
                step.complete(details)
                if self.current_step == step:
                    self.current_step = None
                self._update_overall_progress()
                break

    def fail_step(self, step_id: str, error_message: str):
        """Fail a specific step"""
        for step in self.steps:
            if step.id == step_id:
                step.fail(error_message)
                if self.current_step == step:
                    self.current_step = None
                self._update_overall_progress()
                break

    def skip_step(self, step_id: str, reason: Optional[str] = None):
        """Skip a specific step"""
        for step in self.steps:
            if step.id == step_id:
                step.skip(reason)
                if self.current_step == step:
                    self.current_step = None
                self._update_overall_progress()
                break

    def update_step_progress(self, step_id: str, percentage: float, details: Optional[Dict[str, Any]] = None):
        """Update progress for a specific step"""
        for step in self.steps:
            if step.id == step_id:
                step.update_progress(percentage, details)
                self._update_overall_progress()
                break

    def _update_overall_progress(self):
        """Update overall session progress"""
        if not self.steps:
            self.overall_progress = 0.0
            return

        total_weight = len(self.steps)
        completed_weight = 0.0

        for step in self.steps:
            if step.status == StepStatus.COMPLETED:
                completed_weight += 1.0
            elif step.status == StepStatus.IN_PROGRESS:
                completed_weight += step.progress_percentage / 100.0
            elif step.status == StepStatus.FAILED:
                completed_weight += 0.0  # Failed steps don't contribute to progress
            elif step.status == StepStatus.SKIPPED:
                completed_weight += 1.0  # Skipped steps count as completed

        self.overall_progress = (completed_weight / total_weight) * 100.0

    def complete_session(self):
        """Complete the entire session"""
        self.end_time = time.time()
        self.total_duration = self.end_time - self.start_time
        self.overall_progress = 100.0

    def get_step(self, step_id: str) -> Optional[ProcessingStep]:
        """Get a specific step by ID"""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def to_markdown(self) -> str:
        """Convert session to markdown format"""
        md_lines = []
        
        # Header
        md_lines.append("# Deepfake Detection Processing Steps")
        md_lines.append(f"**Session ID:** {self.session_id}")
        md_lines.append(f"**Video ID:** {self.video_id}")
        md_lines.append(f"**Start Time:** {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.end_time:
            md_lines.append(f"**End Time:** {datetime.fromtimestamp(self.end_time).strftime('%Y-%m-%d %H:%M:%S')}")
            md_lines.append(f"**Total Duration:** {self.total_duration:.2f}s")
        
        md_lines.append(f"**Overall Progress:** {self.overall_progress:.1f}%")
        md_lines.append("")

        # Progress bar
        progress_bar = self._generate_progress_bar(self.overall_progress)
        md_lines.append(f"**Progress:** {progress_bar} {self.overall_progress:.1f}%")
        md_lines.append("")

        # Steps
        md_lines.append("## Processing Steps")
        md_lines.append("")

        for i, step in enumerate(self.steps, 1):
            md_lines.append(f"### {i}. {step.name}")
            
            # Status badge
            status_badge = self._get_status_badge(step.status)
            md_lines.append(f"**Status:** {status_badge}")
            
            # Description
            md_lines.append(f"**Description:** {step.description}")
            
            # Timing
            if step.start_time:
                start_str = datetime.fromtimestamp(step.start_time).strftime('%H:%M:%S')
                md_lines.append(f"**Start Time:** {start_str}")
            
            if step.end_time and step.duration:
                end_str = datetime.fromtimestamp(step.end_time).strftime('%H:%M:%S')
                md_lines.append(f"**End Time:** {end_str}")
                md_lines.append(f"**Duration:** {step.duration:.2f}s")
            
            # Progress
            if step.status == StepStatus.IN_PROGRESS:
                progress_bar = self._generate_progress_bar(step.progress_percentage)
                md_lines.append(f"**Progress:** {progress_bar} {step.progress_percentage:.1f}%")
            
            # Details
            if step.details:
                md_lines.append("**Details:**")
                for key, value in step.details.items():
                    md_lines.append(f"- **{key}:** {value}")
            
            # Error
            if step.error_message:
                md_lines.append(f"**Error:** {step.error_message}")
            
            # Model name
            if step.model_name:
                md_lines.append(f"**Model:** {step.model_name}")
            
            md_lines.append("")

        return "\n".join(md_lines)

    def _generate_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Generate a text-based progress bar"""
        filled = int(width * percentage / 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"

    def _get_status_badge(self, status: StepStatus) -> str:
        """Get markdown status badge"""
        badges = {
            StepStatus.PENDING: "⏳ Pending",
            StepStatus.IN_PROGRESS: "🔄 In Progress",
            StepStatus.COMPLETED: "✅ Completed",
            StepStatus.FAILED: "❌ Failed",
            StepStatus.SKIPPED: "⏭️ Skipped"
        }
        return badges.get(status, "❓ Unknown")

    def to_json(self) -> Dict[str, Any]:
        """Convert session to JSON format"""
        return {
            "session_id": self.session_id,
            "video_id": self.video_id,
            "video_path": self.video_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration": self.total_duration,
            "overall_progress": self.overall_progress,
            "current_step": self.current_step.id if self.current_step else None,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "description": step.description,
                    "step_type": step.step_type.value,
                    "status": step.status.value,
                    "start_time": step.start_time,
                    "end_time": step.end_time,
                    "duration": step.duration,
                    "progress_percentage": step.progress_percentage,
                    "details": step.details,
                    "error_message": step.error_message,
                    "model_name": step.model_name
                }
                for step in self.steps
            ],
            "metadata": self.metadata,
            "markdown": self.to_markdown()
        }

class ProcessingStepsTracker:
    """Main tracker for processing steps"""
    
    def __init__(self):
        self.sessions: Dict[str, ProcessingSession] = {}
        self.active_sessions: Dict[str, str] = {}  # video_id -> session_id mapping

    def create_session(self, video_id: str, video_path: Optional[str] = None) -> ProcessingSession:
        """Create a new processing session"""
        session_id = f"session_{video_id}_{int(time.time())}"
        session = ProcessingSession(
            session_id=session_id,
            video_id=video_id,
            video_path=video_path
        )
        
        # Add default steps
        self._add_default_steps(session)
        
        self.sessions[session_id] = session
        self.active_sessions[video_id] = session_id
        
        logger.info(f"📊 Created processing session {session_id} for video {video_id}")
        return session

    def _add_default_steps(self, session: ProcessingSession):
        """Add default processing steps"""
        steps = [
            ProcessingStep(
                id="video_upload",
                name="Video Upload",
                description="Upload and validate video file",
                step_type=StepType.VIDEO_UPLOAD
            ),
            ProcessingStep(
                id="face_extraction",
                name="Face Extraction",
                description="Extract faces from video frames using YOLOv8",
                step_type=StepType.FACE_EXTRACTION
            ),
            ProcessingStep(
                id="model_loading",
                name="Model Loading",
                description="Load all detection models (EfficientNet, MesoNet, Vision Transformers, etc.)",
                step_type=StepType.MODEL_LOADING
            ),
            ProcessingStep(
                id="efficientnet_analysis",
                name="EfficientNet Analysis",
                description="Analyze faces using EfficientNet model",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="EfficientNet"
            ),
            ProcessingStep(
                id="mesonet_analysis",
                name="MesoNet Analysis",
                description="Analyze faces using MesoNet model",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="MesoNet"
            ),
            ProcessingStep(
                id="yolov8_analysis",
                name="YOLOv8 Analysis",
                description="Analyze faces using YOLOv8-based detection",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="YOLOv8"
            ),
            ProcessingStep(
                id="vision_transformer_analysis",
                name="Vision Transformer Analysis",
                description="Analyze faces using Vision Transformer model",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="Vision Transformer"
            ),
            ProcessingStep(
                id="lstm_temporal_analysis",
                name="LSTM Temporal Analysis",
                description="Analyze temporal patterns using LSTM model",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="LSTM"
            ),
            ProcessingStep(
                id="clip_analysis",
                name="CLIP Analysis",
                description="Analyze faces using CLIP model",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="CLIP"
            ),
            ProcessingStep(
                id="openai_analysis",
                name="OpenAI GPT-4 Analysis",
                description="Analyze content using OpenAI GPT-4",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="OpenAI GPT-4"
            ),
            ProcessingStep(
                id="gemini_analysis",
                name="Google Gemini Analysis",
                description="Analyze content using Google Gemini",
                step_type=StepType.MODEL_ANALYSIS,
                model_name="Google Gemini"
            ),
            ProcessingStep(
                id="ensemble_fusion",
                name="Ensemble Fusion",
                description="Combine results from all models using weighted ensemble",
                step_type=StepType.ENSEMBLE_FUSION
            ),
            ProcessingStep(
                id="ground_truth_validation",
                name="Ground Truth Validation",
                description="Validate results using ground truth analysis",
                step_type=StepType.VALIDATION
            ),
            ProcessingStep(
                id="final_result",
                name="Final Result",
                description="Generate final detection result",
                step_type=StepType.FINAL_RESULT
            )
        ]
        
        for step in steps:
            session.add_step(step)

    def get_session(self, video_id: str) -> Optional[ProcessingSession]:
        """Get session by video ID"""
        session_id = self.active_sessions.get(video_id)
        if session_id:
            return self.sessions.get(session_id)
        return None

    def start_step(self, video_id: str, step_id: str):
        """Start a processing step"""
        session = self.get_session(video_id)
        if session:
            session.start_step(step_id)
            logger.info(f"🔄 Started step {step_id} for video {video_id}")

    def update_step_progress(self, video_id: str, step_id: str, percentage: float, details: Optional[Dict[str, Any]] = None):
        """Update step progress"""
        session = self.get_session(video_id)
        if session:
            session.update_step_progress(step_id, percentage, details)
            logger.debug(f"📊 Updated step {step_id} progress: {percentage:.1f}%")

    def complete_step(self, video_id: str, step_id: str, details: Optional[Dict[str, Any]] = None):
        """Complete a processing step"""
        session = self.get_session(video_id)
        if session:
            session.complete_step(step_id, details)
            logger.info(f"✅ Completed step {step_id} for video {video_id}")

    def fail_step(self, video_id: str, step_id: str, error_message: str):
        """Fail a processing step"""
        session = self.get_session(video_id)
        if session:
            session.fail_step(step_id, error_message)
            logger.error(f"❌ Failed step {step_id} for video {video_id}: {error_message}")

    def skip_step(self, video_id: str, step_id: str, reason: Optional[str] = None):
        """Skip a processing step"""
        session = self.get_session(video_id)
        if session:
            session.skip_step(step_id, reason)
            logger.info(f"⏭️ Skipped step {step_id} for video {video_id}: {reason or 'No reason provided'}")

    def complete_session(self, video_id: str):
        """Complete a processing session"""
        session = self.get_session(video_id)
        if session:
            session.complete_session()
            logger.info(f"🎉 Completed processing session for video {video_id}")

    def get_progress_markdown(self, video_id: str) -> Optional[str]:
        """Get markdown progress for a video"""
        session = self.get_session(video_id)
        if session:
            return session.to_markdown()
        return None

    def get_progress_json(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get JSON progress for a video"""
        session = self.get_session(video_id)
        if session:
            return session.to_json()
        return None

    def cleanup_session(self, video_id: str):
        """Clean up a processing session"""
        session_id = self.active_sessions.get(video_id)
        if session_id:
            del self.active_sessions[video_id]
            # Keep session in memory for a while for debugging
            # del self.sessions[session_id]
            logger.info(f"🧹 Cleaned up session for video {video_id}")

# Global tracker instance
processing_tracker = ProcessingStepsTracker()

# Convenience functions
def create_processing_session(video_id: str, video_path: Optional[str] = None) -> ProcessingSession:
    """Create a new processing session"""
    return processing_tracker.create_session(video_id, video_path)

def start_processing_step(video_id: str, step_id: str):
    """Start a processing step"""
    processing_tracker.start_step(video_id, step_id)

def update_processing_progress(video_id: str, step_id: str, percentage: float, details: Optional[Dict[str, Any]] = None):
    """Update processing progress"""
    processing_tracker.update_step_progress(video_id, step_id, percentage, details)

def complete_processing_step(video_id: str, step_id: str, details: Optional[Dict[str, Any]] = None):
    """Complete a processing step"""
    processing_tracker.complete_step(video_id, step_id, details)

def fail_processing_step(video_id: str, step_id: str, error_message: str):
    """Fail a processing step"""
    processing_tracker.fail_step(video_id, step_id, error_message)

def skip_processing_step(video_id: str, step_id: str, reason: Optional[str] = None):
    """Skip a processing step"""
    processing_tracker.skip_step(video_id, step_id, reason)

def complete_processing_session(video_id: str):
    """Complete a processing session"""
    processing_tracker.complete_session(video_id)

def get_processing_markdown(video_id: str) -> Optional[str]:
    """Get markdown progress for a video"""
    return processing_tracker.get_progress_markdown(video_id)

def get_processing_json(video_id: str) -> Optional[Dict[str, Any]]:
    """Get JSON progress for a video"""
    return processing_tracker.get_progress_json(video_id)

def cleanup_processing_session(video_id: str):
    """Clean up a processing session"""
    processing_tracker.cleanup_session(video_id)
