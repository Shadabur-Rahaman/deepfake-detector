"""
Continuous Metrics Monitor - System Health & Performance Tracking
================================================================

This module provides continuous monitoring of the deepfake detection system health,
tracking key metrics like ECE, model diversity, temporal consistency, and more.

Features:
- Real-time system health metrics computation
- ECE calibration quality monitoring
- Model agreement entropy tracking
- Temporal coherence analysis
- Alert threshold management
- JSON logging for historical analysis
"""

import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class ContinuousMetricsMonitor:
    """Continuous monitoring of detection system health"""
    
    def __init__(self, log_dir: str = "logs/metrics"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_history = []
        self.alert_thresholds = {
            'ece': 0.3,
            'agreement_entropy': 0.2,
            'temporal_coherence_std': 0.25,
            'dropout_uncertainty': 0.35,
            'face_detection_rate': 0.75,
            'model_agreement_rate': 0.95
        }
    
    async def compute_system_health(
        self, 
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Compute comprehensive system health metrics.
        
        Args:
            predictions: List of prediction results with ground truth
            
        Returns:
            Dictionary of health metrics
        """
        health_metrics = {}
        
        # Extract data
        true_labels = [p['ground_truth'] for p in predictions if 'ground_truth' in p]
        pred_labels = [p['prediction'] for p in predictions]
        confidences = [p['confidence'] for p in predictions]
        ensemble_predictions = [p.get('ensemble_scores', {}) for p in predictions]
        
        # 1. Calibration metrics (ECE)
        if true_labels and confidences:
            try:
                from .confidence_calibration_2025 import CalibrationValidator
                ece_calculator = CalibrationValidator()
                ece_results = ece_calculator.calculate_ece(
                    np.array([1 if l == 'Fake' else 0 for l in true_labels]),
                    np.array(confidences)
                )
                health_metrics['ece'] = ece_results['ece']
                health_metrics['mce'] = ece_results['mce']
                health_metrics['reliability_score'] = ece_results['reliability_score']
            except Exception as e:
                logger.warning(f"ECE calculation failed: {e}")
                health_metrics['ece'] = 0.0
                health_metrics['mce'] = 0.0
                health_metrics['reliability_score'] = 0.5
        
        # 2. Agreement entropy (model diversity)
        if ensemble_predictions:
            entropies = []
            for pred in ensemble_predictions:
                if pred:
                    scores = np.array(list(pred.values()))
                    # Shannon entropy
                    entropy = -np.sum(scores * np.log(scores + 1e-8))
                    entropies.append(entropy)
            health_metrics['agreement_entropy'] = np.mean(entropies) if entropies else 0.0
        
        # 3. Temporal coherence
        if len(confidences) > 1:
            health_metrics['temporal_coherence_std'] = np.std(confidences)
        
        # 4. Model agreement rate
        if ensemble_predictions:
            agreement_rates = []
            for pred in ensemble_predictions:
                if pred and len(pred) > 0:
                    scores = list(pred.values())
                    # Agreement: fraction of models within 0.1 of mean
                    mean_score = np.mean(scores)
                    agreement = np.mean([abs(s - mean_score) < 0.1 for s in scores])
                    agreement_rates.append(agreement)
            health_metrics['model_agreement_rate'] = np.mean(agreement_rates) if agreement_rates else 0.0
        
        # 5. Face detection rate
        total_faces = sum(p.get('faces_detected', 0) for p in predictions)
        total_expected = len(predictions) * 5  # Assume 5 faces per video on average
        if total_expected > 0:
            health_metrics['face_detection_rate'] = total_faces / total_expected
        else:
            health_metrics['face_detection_rate'] = 1.0
        
        # 6. Check for alerts
        alerts = self._check_alerts(health_metrics)
        health_metrics['alerts'] = alerts
        
        # 7. Log metrics
        await self._log_metrics(health_metrics)
        
        return health_metrics
    
    def _check_alerts(self, metrics: Dict[str, float]) -> List[str]:
        """Check if any metrics exceed alert thresholds"""
        alerts = []
        
        for metric_name, threshold in self.alert_thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                
                # Different comparison logic based on metric
                if metric_name in ['ece', 'temporal_coherence_std', 'dropout_uncertainty']:
                    # Lower is better
                    if value > threshold:
                        alerts.append(f"{metric_name.upper()} too high: {value:.3f} > {threshold}")
                elif metric_name in ['agreement_entropy', 'face_detection_rate']:
                    # Higher is better
                    if value < threshold:
                        alerts.append(f"{metric_name.upper()} too low: {value:.3f} < {threshold}")
                elif metric_name == 'model_agreement_rate':
                    # Should be moderate (not too low, not too high)
                    if value > threshold:
                        alerts.append(f"{metric_name.upper()} too high (low diversity): {value:.3f} > {threshold}")
        
        return alerts
    
    async def _log_metrics(self, metrics: Dict[str, float]):
        """Log metrics to file and database"""
        timestamp = datetime.now().isoformat()
        
        # Append to history
        self.metrics_history.append({
            'timestamp': timestamp,
            'metrics': metrics
        })
        
        # Write to JSON log file
        log_file = self.log_dir / f"health_metrics_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_file, 'a') as f:
            json.dump({'timestamp': timestamp, **metrics}, f)
            f.write('\n')
        
        # Log alerts
        if metrics.get('alerts'):
            logger.warning(f"⚠️ METRICS ALERTS:")
            for alert in metrics['alerts']:
                logger.warning(f"   {alert}")
    
    def get_recent_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent metrics from the last N hours"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        recent_metrics = []
        for entry in self.metrics_history:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
                if entry_time >= cutoff_time:
                    recent_metrics.append(entry)
            except Exception as e:
                logger.warning(f"Error parsing timestamp: {e}")
                continue
        
        return recent_metrics
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        if not self.metrics_history:
            return {
                'status': 'unknown',
                'message': 'No metrics available',
                'last_check': None
            }
        
        latest_metrics = self.metrics_history[-1]['metrics']
        
        # Determine overall health status
        if latest_metrics.get('alerts'):
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'last_check': self.metrics_history[-1]['timestamp'],
            'ece': latest_metrics.get('ece', 0.0),
            'agreement_entropy': latest_metrics.get('agreement_entropy', 0.0),
            'model_agreement_rate': latest_metrics.get('model_agreement_rate', 0.0),
            'face_detection_rate': latest_metrics.get('face_detection_rate', 1.0),
            'alerts': latest_metrics.get('alerts', [])
        }

# Global metrics monitor instance
metrics_monitor = ContinuousMetricsMonitor()
