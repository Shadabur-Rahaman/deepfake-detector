"""
Processing Stage Tracker - Step-by-Step Processing Display
=========================================================

This module tracks the processing stages of deepfake detection and provides
detailed step-by-step information for display in the frontend, formatted
as markdown as specified in the project report.

Author: AI Assistant
Date: 2025
"""

import time
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class StageStatus(Enum):
    """Processing stage status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class StageType(Enum):
    """Type of processing stage"""
    PREPROCESSING = "preprocessing"
    FACE_EXTRACTION = "face_extraction"
    TRADITIONAL_DETECTION = "traditional_detection"
    MODERN_AI_DETECTION = "modern_ai_detection"
    CLOUD_AI_DETECTION = "cloud_ai_detection"
    ENSEMBLE_CALCULATION = "ensemble_calculation"
    POSTPROCESSING = "postprocessing"

@dataclass
class ModelResult:
    """Individual model result"""
    name: str
    prediction: str
    confidence: float
    weight: float
    contribution: float
    model_type: str
    processing_time: float
    status: StageStatus
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessingStage:
    """Individual processing stage"""
    name: str
    stage_type: StageType
    status: StageStatus
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    models: List[ModelResult] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: int = 0
    message: str = ""
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class ProcessingTracker:
    """Main processing tracker"""
    video_id: str
    start_time: float
    current_stage: Optional[str] = None
    stages: List[ProcessingStage] = field(default_factory=list)
    overall_progress: int = 0
    total_models_used: int = 0
    final_result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProcessingStageTracker:
    """
    Tracks processing stages and generates step-by-step display information
    
    Features:
    - Real-time stage tracking
    - Model result tracking
    - Markdown formatting
    - Progress visualization
    - Error handling
    """
    
    def __init__(self, video_id: str):
        self.tracker = ProcessingTracker(
            video_id=video_id,
            start_time=time.time()
        )
        self._initialize_stages()
    
    def _initialize_stages(self):
        """Initialize all processing stages"""
        stages = [
            ("Video Preprocessing", StageType.PREPROCESSING),
            ("Face Extraction", StageType.FACE_EXTRACTION),
            ("Traditional AI Detection", StageType.TRADITIONAL_DETECTION),
            ("Modern AI Detection", StageType.MODERN_AI_DETECTION),
            ("Cloud AI Detection", StageType.CLOUD_AI_DETECTION),
            ("Ensemble Calculation", StageType.ENSEMBLE_CALCULATION),
            ("Result Compilation", StageType.POSTPROCESSING)
        ]
        
        for name, stage_type in stages:
            stage = ProcessingStage(
                name=name,
                stage_type=stage_type,
                status=StageStatus.PENDING,
                start_time=time.time(),
                progress_percentage=0
            )
            self.tracker.stages.append(stage)
    
    def start_stage(self, stage_name: str, message: str = "") -> None:
        """Start a processing stage"""
        try:
            stage = self._get_stage_by_name(stage_name)
            if stage:
                stage.status = StageStatus.IN_PROGRESS
                stage.start_time = time.time()
                stage.message = message
                stage.progress_percentage = 0
                self.tracker.current_stage = stage_name
                
                logger.info(f"🔄 Starting stage: {stage_name} - {message}")
            else:
                logger.warning(f"Stage not found: {stage_name}")
                
        except Exception as e:
            logger.error(f"Failed to start stage {stage_name}: {e}")
    
    def complete_stage(self, stage_name: str, models: List[Dict[str, Any]] = None, 
                      details: Dict[str, Any] = None) -> None:
        """Complete a processing stage"""
        try:
            stage = self._get_stage_by_name(stage_name)
            if stage:
                stage.status = StageStatus.COMPLETED
                stage.end_time = time.time()
                stage.duration = stage.end_time - stage.start_time
                stage.progress_percentage = 100
                
                if models:
                    for model_data in models:
                        model_result = ModelResult(
                            name=model_data.get('name', 'Unknown'),
                            prediction=model_data.get('prediction', 'Unknown'),
                            confidence=model_data.get('confidence', 0.0),
                            weight=model_data.get('weight', 0.0),
                            contribution=model_data.get('contribution', 0.0),
                            model_type=model_data.get('model_type', 'Unknown'),
                            processing_time=model_data.get('processing_time', 0.0),
                            status=StageStatus.COMPLETED,
                            details=model_data.get('details', {})
                        )
                        stage.models.append(model_result)
                
                if details:
                    stage.details.update(details)
                
                logger.info(f"✅ Completed stage: {stage_name} ({stage.duration:.2f}s)")
                self._update_overall_progress()
            else:
                logger.warning(f"Stage not found: {stage_name}")
                
        except Exception as e:
            logger.error(f"Failed to complete stage {stage_name}: {e}")
    
    def fail_stage(self, stage_name: str, error: str) -> None:
        """Mark a stage as failed"""
        try:
            stage = self._get_stage_by_name(stage_name)
            if stage:
                stage.status = StageStatus.FAILED
                stage.end_time = time.time()
                stage.duration = stage.end_time - stage.start_time
                stage.errors.append(error)
                
                logger.error(f"❌ Failed stage: {stage_name} - {error}")
            else:
                logger.warning(f"Stage not found: {stage_name}")
                
        except Exception as e:
            logger.error(f"Failed to fail stage {stage_name}: {e}")
    
    def update_stage_progress(self, stage_name: str, progress: int, message: str = "") -> None:
        """Update stage progress"""
        try:
            stage = self._get_stage_by_name(stage_name)
            if stage:
                stage.progress_percentage = min(progress, 100)
                if message:
                    stage.message = message
                
                logger.debug(f"📊 Updated {stage_name} progress: {progress}% - {message}")
            else:
                logger.warning(f"Stage not found: {stage_name}")
                
        except Exception as e:
            logger.error(f"Failed to update progress for {stage_name}: {e}")
    
    def add_model_result(self, stage_name: str, model_data: Dict[str, Any]) -> None:
        """Add a model result to a stage"""
        try:
            stage = self._get_stage_by_name(stage_name)
            if stage:
                model_result = ModelResult(
                    name=model_data.get('name', 'Unknown'),
                    prediction=model_data.get('prediction', 'Unknown'),
                    confidence=model_data.get('confidence', 0.0),
                    weight=model_data.get('weight', 0.0),
                    contribution=model_data.get('contribution', 0.0),
                    model_type=model_data.get('model_type', 'Unknown'),
                    processing_time=model_data.get('processing_time', 0.0),
                    status=StageStatus.COMPLETED,
                    details=model_data.get('details', {})
                )
                stage.models.append(model_result)
                self.tracker.total_models_used += 1
                
                logger.debug(f"📝 Added model result: {model_result.name} to {stage_name}")
            else:
                logger.warning(f"Stage not found: {stage_name}")
                
        except Exception as e:
            logger.error(f"Failed to add model result to {stage_name}: {e}")
    
    def finalize_result(self, final_result: Dict[str, Any]) -> None:
        """Finalize the processing with final result"""
        try:
            self.tracker.final_result = final_result
            self.tracker.overall_progress = 100
            
            # Mark all remaining stages as completed
            for stage in self.tracker.stages:
                if stage.status == StageStatus.PENDING:
                    stage.status = StageStatus.SKIPPED
                elif stage.status == StageStatus.IN_PROGRESS:
                    stage.status = StageStatus.COMPLETED
                    stage.end_time = time.time()
                    stage.duration = stage.end_time - stage.start_time
                    stage.progress_percentage = 100
            
            logger.info(f"🎯 Finalized processing for {self.tracker.video_id}")
            
        except Exception as e:
            logger.error(f"Failed to finalize result: {e}")
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary for API response"""
        try:
            total_time = time.time() - self.tracker.start_time
            completed_stages = [s for s in self.tracker.stages if s.status == StageStatus.COMPLETED]
            failed_stages = [s for s in self.tracker.stages if s.status == StageStatus.FAILED]
            
            return {
                'video_id': self.tracker.video_id,
                'status': 'completed' if not failed_stages else 'failed',
                'current_stage': self.tracker.current_stage,
                'overall_progress': self.tracker.overall_progress,
                'total_processing_time': round(total_time, 2),
                'stages_completed': len(completed_stages),
                'stages_failed': len(failed_stages),
                'total_stages': len(self.tracker.stages),
                'total_models_used': self.tracker.total_models_used,
                'stages': [
                    {
                        'name': stage.name,
                        'status': stage.status.value,
                        'duration': round(stage.duration, 2) if stage.duration else None,
                        'progress_percentage': stage.progress_percentage,
                        'message': stage.message,
                        'models_count': len(stage.models),
                        'models': [
                            {
                                'name': model.name,
                                'prediction': model.prediction,
                                'confidence': model.confidence,
                                'weight': model.weight,
                                'contribution': model.contribution,
                                'model_type': model.model_type,
                                'processing_time': model.processing_time
                            }
                            for model in stage.models
                        ],
                        'details': stage.details,
                        'warnings': stage.warnings,
                        'errors': stage.errors
                    }
                    for stage in self.tracker.stages
                ],
                'final_result': self.tracker.final_result
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing summary: {e}")
            return {'error': str(e)}
    
    def get_markdown_report(self) -> str:
        """Generate markdown report as specified in project requirements"""
        try:
            total_time = time.time() - self.tracker.start_time
            completed_stages = [s for s in self.tracker.stages if s.status == StageStatus.COMPLETED]
            
            markdown = []
            markdown.append("# Deepfake Detection Processing Report")
            markdown.append("")
            markdown.append(f"**Video ID:** `{self.tracker.video_id}`")
            markdown.append(f"**Processing Time:** {total_time:.2f} seconds")
            markdown.append(f"**Stages Completed:** {len(completed_stages)}/{len(self.tracker.stages)}")
            markdown.append(f"**Models Used:** {self.tracker.total_models_used}")
            markdown.append("")
            
            # Processing stages
            markdown.append("## Processing Stages")
            markdown.append("")
            
            for stage in self.tracker.stages:
                status_emoji = {
                    StageStatus.PENDING: "⏳",
                    StageStatus.IN_PROGRESS: "🔄",
                    StageStatus.COMPLETED: "✅",
                    StageStatus.FAILED: "❌",
                    StageStatus.SKIPPED: "⏭️"
                }.get(stage.status, "❓")
                
                markdown.append(f"### {status_emoji} {stage.name}")
                markdown.append("")
                markdown.append(f"- **Status:** {stage.status.value}")
                markdown.append(f"- **Duration:** {stage.duration:.2f}s" if stage.duration else "- **Duration:** N/A")
                markdown.append(f"- **Progress:** {stage.progress_percentage}%")
                
                if stage.message:
                    markdown.append(f"- **Message:** {stage.message}")
                
                if stage.models:
                    markdown.append(f"- **Models Used:** {len(stage.models)}")
                    markdown.append("")
                    markdown.append("#### Model Results")
                    markdown.append("")
                    markdown.append("| Model | Prediction | Confidence | Weight | Contribution | Type |")
                    markdown.append("|-------|------------|------------|--------|--------------|------|")
                    
                    for model in stage.models:
                        markdown.append(f"| {model.name} | {model.prediction} | {model.confidence:.3f} | {model.weight:.3f} | {model.contribution:.3f} | {model.model_type} |")
                    
                    markdown.append("")
                
                if stage.warnings:
                    markdown.append("#### ⚠️ Warnings")
                    for warning in stage.warnings:
                        markdown.append(f"- {warning}")
                    markdown.append("")
                
                if stage.errors:
                    markdown.append("#### ❌ Errors")
                    for error in stage.errors:
                        markdown.append(f"- {error}")
                    markdown.append("")
                
                markdown.append("")
            
            # Final result
            if self.tracker.final_result:
                markdown.append("## Final Detection Result")
                markdown.append("")
                markdown.append(f"- **Prediction:** {self.tracker.final_result.get('prediction', 'Unknown')}")
                markdown.append(f"- **Confidence:** {self.tracker.final_result.get('confidence', 0):.1f}%")
                markdown.append(f"- **Detection Method:** {self.tracker.final_result.get('detection_method', 'Unknown')}")
                markdown.append(f"- **Faces Detected:** {self.tracker.final_result.get('faces_detected', 0)}")
                
                if 'model_contributions' in self.tracker.final_result:
                    markdown.append("")
                    markdown.append("### Model Contributions")
                    markdown.append("")
                    markdown.append("| Model | Score | Weight | Contribution | Type |")
                    markdown.append("|-------|-------|--------|--------------|------|")
                    
                    for contrib in self.tracker.final_result['model_contributions']:
                        markdown.append(f"| {contrib['name']} | {contrib['score']:.3f} | {contrib['weight']:.3f} | {contrib['contribution']:.3f} | {contrib['model_type']} |")
            
            return "\n".join(markdown)
            
        except Exception as e:
            logger.error(f"Failed to generate markdown report: {e}")
            return f"# Error\n\nFailed to generate report: {str(e)}"
    
    def _get_stage_by_name(self, stage_name: str) -> Optional[ProcessingStage]:
        """Get stage by name"""
        for stage in self.tracker.stages:
            if stage.name == stage_name:
                return stage
        return None
    
    def _update_overall_progress(self) -> None:
        """Update overall progress percentage"""
        try:
            completed_stages = len([s for s in self.tracker.stages if s.status == StageStatus.COMPLETED])
            total_stages = len(self.tracker.stages)
            self.tracker.overall_progress = int((completed_stages / total_stages) * 100)
            
        except Exception as e:
            logger.error(f"Failed to update overall progress: {e}")

# Global tracker storage
_processing_trackers: Dict[str, ProcessingStageTracker] = {}

def get_processing_tracker(video_id: str) -> ProcessingStageTracker:
    """Get or create processing tracker for video"""
    if video_id not in _processing_trackers:
        _processing_trackers[video_id] = ProcessingStageTracker(video_id)
    return _processing_trackers[video_id]

def cleanup_processing_tracker(video_id: str) -> None:
    """Clean up processing tracker"""
    if video_id in _processing_trackers:
        del _processing_trackers[video_id]
