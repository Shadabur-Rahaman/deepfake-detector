#!/usr/bin/env python3
"""
Detection Debug Logger - Comprehensive logging for deepfake detection debugging
Logs all model predictions, thresholds, consensus scores, and decision reasoning
"""

import os
import json
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ModelPredictionLog:
    """Log entry for individual model prediction"""
    model_name: str
    prediction: str
    confidence: float
    raw_output: Optional[float] = None
    processing_time_ms: Optional[float] = None
    error: Optional[str] = None

@dataclass
class ConsensusLog:
    """Log entry for consensus analysis"""
    agreement_score: float
    consensus_level: str
    models_agreeing: int
    total_models: int
    disagreement_details: Dict[str, Any]
    recommended_threshold: float

@dataclass
class ThresholdDecisionLog:
    """Log entry for threshold decision"""
    final_threshold: float
    reasoning: str
    consensus_level: str
    confidence_boost: float
    uncertainty_flag: bool
    fallback_recommendation: str

@dataclass
class DetectionDebugReport:
    """Complete debug report for a video detection"""
    video_id: str
    timestamp: float
    detection_method: str
    model_predictions: List[ModelPredictionLog]
    consensus_analysis: Optional[ConsensusLog]
    threshold_decision: Optional[ThresholdDecisionLog]
    final_prediction: str
    final_confidence: float
    processing_time: float
    face_count: int
    adjustments_applied: Dict[str, Any]
    error_logs: List[str]
    debug_summary: str

class DetectionDebugLogger:
    """
    Comprehensive debug logging for deepfake detection
    """
    
    def __init__(self, log_dir: str = "logs/detection_debug"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # In-memory cache for current detection session
        self.current_session = {}
        
        logger.info(f"🔍 DetectionDebugLogger initialized, log_dir: {log_dir}")
    
    def start_detection_session(self, video_id: str, detection_method: str = "unknown"):
        """Start a new detection session"""
        self.current_session[video_id] = {
            'video_id': video_id,
            'start_time': time.time(),
            'detection_method': detection_method,
            'model_predictions': [],
            'consensus_analysis': None,
            'threshold_decision': None,
            'adjustments_applied': {},
            'error_logs': [],
            'face_count': 0
        }
        
        logger.info(f"🔍 Started detection session for {video_id} using {detection_method}")
    
    def log_model_prediction(self, video_id: str, model_name: str, prediction: str, 
                           confidence: float, raw_output: Optional[float] = None,
                           processing_time_ms: Optional[float] = None, error: Optional[str] = None):
        """Log individual model prediction"""
        if video_id not in self.current_session:
            self.start_detection_session(video_id)
        
        prediction_log = ModelPredictionLog(
            model_name=model_name,
            prediction=prediction,
            confidence=confidence,
            raw_output=raw_output,
            processing_time_ms=processing_time_ms,
            error=error
        )
        
        self.current_session[video_id]['model_predictions'].append(prediction_log)
        
        logger.info(f"🔍 Model {model_name}: {prediction} ({confidence:.3f})")
        if error:
            logger.warning(f"   Error: {error}")
    
    def log_consensus_analysis(self, video_id: str, consensus_result):
        """Log consensus analysis result"""
        if video_id not in self.current_session:
            self.start_detection_session(video_id)
        
        consensus_log = ConsensusLog(
            agreement_score=consensus_result.agreement_score,
            consensus_level=consensus_result.consensus_level,
            models_agreeing=consensus_result.models_agreeing,
            total_models=consensus_result.total_models,
            disagreement_details=consensus_result.disagreement_details,
            recommended_threshold=consensus_result.recommended_threshold
        )
        
        self.current_session[video_id]['consensus_analysis'] = consensus_log
        
        logger.info(f"🔍 Consensus: {consensus_result.consensus_level} ({consensus_result.agreement_score:.2f})")
    
    def log_threshold_decision(self, video_id: str, threshold_decision):
        """Log threshold decision"""
        if video_id not in self.current_session:
            self.start_detection_session(video_id)
        
        threshold_log = ThresholdDecisionLog(
            final_threshold=threshold_decision.threshold,
            reasoning=threshold_decision.reasoning,
            consensus_level=threshold_decision.consensus_level,
            confidence_boost=threshold_decision.confidence_boost,
            uncertainty_flag=threshold_decision.uncertainty_flag,
            fallback_recommendation=threshold_decision.fallback_recommendation
        )
        
        self.current_session[video_id]['threshold_decision'] = threshold_log
        
        logger.info(f"🔍 Threshold: {threshold_decision.threshold:.3f} ({threshold_decision.reasoning})")
    
    def log_adjustment(self, video_id: str, adjustment_type: str, adjustment_value: Any, reason: str = ""):
        """Log adjustments applied to final prediction"""
        if video_id not in self.current_session:
            self.start_detection_session(video_id)
        
        self.current_session[video_id]['adjustments_applied'][adjustment_type] = {
            'value': adjustment_value,
            'reason': reason,
            'timestamp': time.time()
        }
        
        logger.info(f"🔍 Adjustment {adjustment_type}: {adjustment_value} ({reason})")
    
    def log_error(self, video_id: str, error_message: str, context: str = ""):
        """Log error during detection"""
        if video_id not in self.current_session:
            self.start_detection_session(video_id)
        
        error_entry = {
            'message': error_message,
            'context': context,
            'timestamp': time.time()
        }
        
        self.current_session[video_id]['error_logs'].append(error_entry)
        
        logger.error(f"🔍 Error in {video_id}: {error_message} ({context})")
    
    def set_face_count(self, video_id: str, face_count: int):
        """Set the number of faces detected"""
        if video_id not in self.current_session:
            self.start_detection_session(video_id)
        
        self.current_session[video_id]['face_count'] = face_count
    
    def finalize_detection_session(self, video_id: str, final_prediction: str, 
                                 final_confidence: float) -> DetectionDebugReport:
        """Finalize detection session and create debug report"""
        if video_id not in self.current_session:
            logger.warning(f"No session found for {video_id}")
            return None
        
        session = self.current_session[video_id]
        processing_time = time.time() - session['start_time']
        
        # Generate debug summary
        debug_summary = self._generate_debug_summary(session, final_prediction, final_confidence)
        
        # Create debug report
        report = DetectionDebugReport(
            video_id=video_id,
            timestamp=session['start_time'],
            detection_method=session['detection_method'],
            model_predictions=session['model_predictions'],
            consensus_analysis=session['consensus_analysis'],
            threshold_decision=session['threshold_decision'],
            final_prediction=final_prediction,
            final_confidence=final_confidence,
            processing_time=processing_time,
            face_count=session['face_count'],
            adjustments_applied=session['adjustments_applied'],
            error_logs=session['error_logs'],
            debug_summary=debug_summary
        )
        
        # Save to file
        self._save_debug_report(report)
        
        # Clean up session
        del self.current_session[video_id]
        
        logger.info(f"🔍 Finalized detection session for {video_id}: {final_prediction} ({final_confidence:.3f})")
        
        return report
    
    def _generate_debug_summary(self, session: Dict, final_prediction: str, final_confidence: float) -> str:
        """Generate human-readable debug summary"""
        summary_parts = []
        
        # Model predictions summary
        if session['model_predictions']:
            real_models = sum(1 for p in session['model_predictions'] if "Real" in p.prediction)
            fake_models = sum(1 for p in session['model_predictions'] if "Deepfake" in p.prediction or "Fake" in p.prediction)
            total_models = len(session['model_predictions'])
            
            summary_parts.append(f"Models: {real_models} real, {fake_models} fake ({total_models} total)")
        
        # Consensus summary
        if session['consensus_analysis']:
            consensus = session['consensus_analysis']
            summary_parts.append(f"Consensus: {consensus.consensus_level} ({consensus.agreement_score:.2f})")
        
        # Threshold summary
        if session['threshold_decision']:
            threshold = session['threshold_decision']
            summary_parts.append(f"Threshold: {threshold.final_threshold:.3f}")
            if threshold.uncertainty_flag:
                summary_parts.append("UNCERTAINTY FLAG")
        
        # Adjustments summary
        if session['adjustments_applied']:
            adj_count = len(session['adjustments_applied'])
            summary_parts.append(f"Adjustments: {adj_count} applied")
        
        # Errors summary
        if session['error_logs']:
            error_count = len(session['error_logs'])
            summary_parts.append(f"Errors: {error_count} logged")
        
        # Final result
        summary_parts.append(f"Result: {final_prediction} ({final_confidence:.3f})")
        
        return " | ".join(summary_parts)
    
    def _save_debug_report(self, report: DetectionDebugReport):
        """Save debug report to JSON file"""
        try:
            # Create filename
            timestamp = datetime.fromtimestamp(report.timestamp).strftime("%Y%m%d_%H%M%S")
            filename = f"{report.video_id}_{timestamp}.json"
            filepath = os.path.join(self.log_dir, filename)
            
            # Convert to serializable format
            report_dict = asdict(report)
            
            # Add metadata
            report_dict['metadata'] = {
                'generated_by': 'DetectionDebugLogger',
                'version': '1.0',
                'generation_time': time.time()
            }
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            logger.info(f"💾 Debug report saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save debug report: {e}")
    
    def load_debug_report(self, video_id: str, timestamp: Optional[float] = None) -> Optional[DetectionDebugReport]:
        """Load debug report from file"""
        try:
            if timestamp:
                # Load specific timestamp
                timestamp_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
                filename = f"{video_id}_{timestamp_str}.json"
            else:
                # Load most recent
                files = [f for f in os.listdir(self.log_dir) if f.startswith(f"{video_id}_") and f.endswith('.json')]
                if not files:
                    return None
                filename = sorted(files)[-1]  # Most recent
            
            filepath = os.path.join(self.log_dir, filename)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct report object
            report = DetectionDebugReport(
                video_id=data['video_id'],
                timestamp=data['timestamp'],
                detection_method=data['detection_method'],
                model_predictions=[ModelPredictionLog(**p) for p in data['model_predictions']],
                consensus_analysis=ConsensusLog(**data['consensus_analysis']) if data['consensus_analysis'] else None,
                threshold_decision=ThresholdDecisionLog(**data['threshold_decision']) if data['threshold_decision'] else None,
                final_prediction=data['final_prediction'],
                final_confidence=data['final_confidence'],
                processing_time=data['processing_time'],
                face_count=data['face_count'],
                adjustments_applied=data['adjustments_applied'],
                error_logs=data['error_logs'],
                debug_summary=data['debug_summary']
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to load debug report: {e}")
            return None
    
    def get_detection_statistics(self, limit: int = 100) -> Dict[str, Any]:
        """Get statistics from recent detections"""
        try:
            files = [f for f in os.listdir(self.log_dir) if f.endswith('.json')]
            files = sorted(files, reverse=True)[:limit]  # Most recent first
            
            stats = {
                'total_detections': len(files),
                'prediction_distribution': {'Real Video': 0, 'Deepfake Detected': 0, 'Other': 0},
                'consensus_distribution': {'high': 0, 'medium': 0, 'low': 0},
                'average_confidence': 0.0,
                'error_rate': 0.0,
                'processing_times': []
            }
            
            total_confidence = 0.0
            total_errors = 0
            
            for filename in files:
                try:
                    filepath = os.path.join(self.log_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Prediction distribution
                    prediction = data['final_prediction']
                    if prediction in stats['prediction_distribution']:
                        stats['prediction_distribution'][prediction] += 1
                    else:
                        stats['prediction_distribution']['Other'] += 1
                    
                    # Consensus distribution
                    if data['consensus_analysis']:
                        consensus_level = data['consensus_analysis']['consensus_level']
                        if consensus_level in stats['consensus_distribution']:
                            stats['consensus_distribution'][consensus_level] += 1
                    
                    # Average confidence
                    total_confidence += data['final_confidence']
                    
                    # Error rate
                    total_errors += len(data['error_logs'])
                    
                    # Processing times
                    stats['processing_times'].append(data['processing_time'])
                    
                except Exception as e:
                    logger.warning(f"Error processing {filename}: {e}")
            
            if len(files) > 0:
                stats['average_confidence'] = total_confidence / len(files)
                stats['error_rate'] = total_errors / len(files)
                stats['average_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get detection statistics: {e}")
            return {}

# Global instance
detection_debug_logger = DetectionDebugLogger()

def get_debug_logger() -> DetectionDebugLogger:
    """Get global debug logger instance"""
    return detection_debug_logger
