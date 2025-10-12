"""
Health Check API Endpoints - System Monitoring & Diagnostics
===========================================================

This module provides health check endpoints for monitoring the deepfake detection
system performance, calibration quality, and overall health status.

Endpoints:
- GET /health/metrics - system health metrics
- GET /health/calibration - detailed calibration report
- GET /health/summary - overall system status
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime
import asyncio
import numpy as np

from ..services.metrics_monitor import metrics_monitor
from ..services.confidence_calibration_2025 import CalibrationValidator

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health/metrics")
async def get_system_health_metrics():
    """
    Get current system health metrics.
    
    Returns comprehensive metrics including:
    - Calibration quality (ECE, MCE)
    - Model diversity (agreement entropy)
    - Temporal consistency
    - Alert status
    """
    try:
        # Get recent predictions from database (mock data for now)
        recent_predictions = await get_recent_predictions(limit=100)
        
        # Compute health metrics
        health_metrics = await metrics_monitor.compute_system_health(recent_predictions)
        
        return {
            'status': 'healthy' if not health_metrics.get('alerts') else 'degraded',
            'metrics': health_metrics,
            'timestamp': datetime.now().isoformat(),
            'evaluated_predictions': len(recent_predictions)
        }
        
    except Exception as e:
        logger.error(f"Health metrics computation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health metrics computation failed: {str(e)}")

@router.get("/health/calibration")
async def get_calibration_report():
    """Get detailed calibration report with reliability diagram data"""
    try:
        # Get validation set predictions (mock data for now)
        validation_predictions = await get_validation_predictions()
        
        if not validation_predictions:
            return {
                'message': 'No validation data available',
                'calibration_status': 'unknown'
            }
        
        # Generate calibration report
        calibration_validator = CalibrationValidator(n_bins=10)
        
        predictions = np.array([1 if p['ground_truth'] == 'Fake' else 0 for p in validation_predictions])
        confidences = np.array([p['confidence'] / 100.0 for p in validation_predictions])
        
        reliability_data = calibration_validator.generate_reliability_diagram(
            predictions=predictions,
            confidences=confidences
        )
        
        return {
            'ece': reliability_data['ece'],
            'reliability_diagram': reliability_data['reliability_diagram_data'],
            'calibration_status': 'good' if reliability_data['ece'] < 0.1 else 'poor',
            'n_samples': len(validation_predictions),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Calibration report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Calibration report generation failed: {str(e)}")

@router.get("/health/summary")
async def get_health_summary():
    """Get overall system health summary"""
    try:
        summary = metrics_monitor.get_health_summary()
        
        # Add additional system info
        summary.update({
            'timestamp': datetime.now().isoformat(),
            'system_version': '2.0 (2025 AI Standards)',
            'uptime_hours': 24,  # Mock uptime
            'total_predictions': len(metrics_monitor.metrics_history),
        })
        
        return summary
        
    except Exception as e:
        logger.error(f"Health summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health summary generation failed: {str(e)}")

@router.get("/health/alerts")
async def get_active_alerts():
    """Get currently active alerts"""
    try:
        recent_metrics = metrics_monitor.get_recent_metrics(hours=1)
        
        active_alerts = []
        for entry in recent_metrics:
            if entry['metrics'].get('alerts'):
                active_alerts.extend(entry['metrics']['alerts'])
        
        return {
            'active_alerts': list(set(active_alerts)),  # Remove duplicates
            'alert_count': len(set(active_alerts)),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Alert retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Alert retrieval failed: {str(e)}")

# Mock data functions (would be replaced with actual database queries)
async def get_recent_predictions(limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent predictions from database (mock implementation)"""
    # Mock data for demonstration
    return [
        {
            'ground_truth': 'Real',
            'prediction': 'Real',
            'confidence': 85.0,
            'ensemble_scores': {'model1': 0.8, 'model2': 0.9, 'model3': 0.85},
            'faces_detected': 3
        },
        {
            'ground_truth': 'Fake',
            'prediction': 'Fake',
            'confidence': 92.0,
            'ensemble_scores': {'model1': 0.95, 'model2': 0.88, 'model3': 0.93},
            'faces_detected': 2
        }
    ] * (limit // 2)

async def get_validation_predictions() -> List[Dict[str, Any]]:
    """Get validation set predictions (mock implementation)"""
    # Mock validation data
    validation_data = []
    for i in range(50):
        is_fake = i % 2 == 0
        confidence = np.random.normal(0.85 if not is_fake else 0.15, 0.1)
        confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        
        validation_data.append({
            'ground_truth': 'Fake' if is_fake else 'Real',
            'prediction': 'Fake' if confidence > 0.5 else 'Real',
            'confidence': confidence * 100,
            'ensemble_scores': {
                f'model{j}': confidence + np.random.normal(0, 0.05) 
                for j in range(3)
            }
        })
    
    return validation_data
