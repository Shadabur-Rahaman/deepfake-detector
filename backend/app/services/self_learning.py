# app/services/self_learning.py
import time
import json
import os
from typing import Dict, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class SelfImprovingDetectionSystem:
    """Continuous learning system for detection improvement"""
    
    def __init__(self):
        self.feedback_file = "detection_feedback.json"
        self.performance_file = "performance_metrics.json"
        self.feedback_database = self._load_feedback_database()
        self.performance_metrics = self._load_performance_metrics()
        
    def _load_feedback_database(self) -> Dict:
        """Load existing feedback database"""
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def _load_performance_metrics(self) -> Dict:
        """Load existing performance metrics"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    return json.load(f)
            return {
                'total_detections': 0,
                'correct_predictions': 0,
                'accuracy_trend': [],
                'false_positive_rate': 0.0,
                'false_negative_rate': 0.0,
                'confidence_calibration': {}
            }
        except Exception:
            return {'total_detections': 0, 'accuracy_trend': []}
    
    async def process_user_feedback(self, video_id: str, user_feedback: str, 
                                  confidence_rating: int = None, 
                                  expert_validation: str = None) -> Dict:
        """Process user feedback to improve future detections"""
        try:
            # Get original detection result from your DETECTION_RESULTS
            from main import DETECTION_RESULTS
            original_result = DETECTION_RESULTS.get(video_id)
            
            if not original_result:
                return {"error": "Video ID not found"}
            
            feedback_entry = {
                'video_id': video_id,
                'timestamp': time.time(),
                'original_prediction': original_result.get('prediction'),
                'original_confidence': original_result.get('confidence'),
                'user_feedback': user_feedback,  # "correct", "incorrect", "uncertain"
                'confidence_rating': confidence_rating,  # 1-5 scale
                'expert_validation': expert_validation,
                'detection_method': original_result.get('model_type', 'unknown'),
                'video_type': original_result.get('video_type', 'unknown')
            }
            
            # Store feedback
            self.feedback_database[video_id] = feedback_entry
            self._save_feedback_database()
            
            # Update performance metrics
            await self._update_performance_metrics(feedback_entry)
            
            # Check if model retraining is needed
            if len(self.feedback_database) % 20 == 0:  # Every 20 feedbacks
                await self._trigger_model_improvement()
            
            return {
                "status": "feedback_processed",
                "feedback_count": len(self.feedback_database),
                "current_accuracy": self.performance_metrics.get('accuracy_trend', [])[-1] if self.performance_metrics.get('accuracy_trend') else 0
            }
            
        except Exception as e:
            logger.error(f"Feedback processing failed: {e}")
            return {"error": str(e)}
    
    async def _update_performance_metrics(self, feedback_entry: Dict):
        """Update running performance statistics"""
        self.performance_metrics['total_detections'] += 1
        
        # Calculate if prediction was correct
        is_correct = feedback_entry['user_feedback'] == 'correct'
        
        if is_correct:
            self.performance_metrics['correct_predictions'] = self.performance_metrics.get('correct_predictions', 0) + 1
        
        # Calculate current accuracy
        current_accuracy = (
            self.performance_metrics['correct_predictions'] / 
            self.performance_metrics['total_detections']
        )
        
        # Update accuracy trend
        accuracy_trend = self.performance_metrics.get('accuracy_trend', [])
        accuracy_trend.append(current_accuracy)
        
        # Keep only last 100 accuracy measurements
        if len(accuracy_trend) > 100:
            accuracy_trend = accuracy_trend[-100:]
        
        self.performance_metrics['accuracy_trend'] = accuracy_trend
        
        # Update confidence calibration
        original_conf = feedback_entry.get('original_confidence', 0)
        conf_bucket = int(original_conf // 10) * 10  # Group by 10s (0-10, 10-20, etc.)
        
        if 'confidence_calibration' not in self.performance_metrics:
            self.performance_metrics['confidence_calibration'] = {}
        
        if str(conf_bucket) not in self.performance_metrics['confidence_calibration']:
            self.performance_metrics['confidence_calibration'][str(conf_bucket)] = {
                'total': 0, 'correct': 0
            }
        
        self.performance_metrics['confidence_calibration'][str(conf_bucket)]['total'] += 1
        if is_correct:
            self.performance_metrics['confidence_calibration'][str(conf_bucket)]['correct'] += 1
        
        self._save_performance_metrics()
    
    async def get_adaptive_threshold(self, content_type: str = "general") -> float:
        """Get dynamically adjusted confidence threshold based on recent performance"""
        recent_accuracy = self._get_recent_accuracy()
        
        # Adjust threshold based on recent performance
        if recent_accuracy > 0.85:
            return 0.4  # Lower threshold when performing well
        elif recent_accuracy > 0.70:
            return 0.5  # Standard threshold
        else:
            return 0.6  # Higher threshold when uncertain
    
    def _get_recent_accuracy(self) -> float:
        """Get accuracy from last 10 detections"""
        accuracy_trend = self.performance_metrics.get('accuracy_trend', [])
        if len(accuracy_trend) >= 10:
            return np.mean(accuracy_trend[-10:])
        elif accuracy_trend:
            return accuracy_trend[-1]
        return 0.5
    
    async def _trigger_model_improvement(self):
        """Trigger model improvement based on accumulated feedback"""
        try:
            logger.info("[LOADING] Triggering model improvement based on feedback...")
            
            # Analyze feedback patterns
            improvement_insights = self._analyze_feedback_patterns()
            
            # Update detection weights if needed
            if improvement_insights['needs_weight_adjustment']:
                await self._adjust_detection_weights(improvement_insights)
            
            logger.info("[OK] Model improvement completed")
            
        except Exception as e:
            logger.error(f"Model improvement failed: {e}")
    
    def _analyze_feedback_patterns(self) -> Dict:
        """Analyze patterns in user feedback"""
        insights = {
            'needs_weight_adjustment': False,
            'problematic_confidence_ranges': [],
            'model_performance_by_type': {}
        }
        
        # Analyze feedback by detection method
        method_performance = {}
        for feedback in self.feedback_database.values():
            method = feedback.get('detection_method', 'unknown')
            is_correct = feedback['user_feedback'] == 'correct'
            
            if method not in method_performance:
                method_performance[method] = {'total': 0, 'correct': 0}
            
            method_performance[method]['total'] += 1
            if is_correct:
                method_performance[method]['correct'] += 1
        
        # Calculate accuracy by method
        for method, stats in method_performance.items():
            accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            insights['model_performance_by_type'][method] = accuracy
            
            # Flag for weight adjustment if accuracy is poor
            if accuracy < 0.6 and stats['total'] >= 5:
                insights['needs_weight_adjustment'] = True
        
        return insights