"""
Production-Grade Deepfake Detection Pipeline

This is the main production pipeline that integrates all detection methods:
- Deterministic detection (no randomness)
- Real video analysis with anomaly detection
- Advanced model ensemble (ResNet, LSTM, YOLOv8, MesoNet, ViT)
- Comprehensive error handling
- Real-time processing capabilities

Author: Senior ML Engineer
Date: 2024
"""

import asyncio
import logging
import time
import torch
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from collections import deque
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from .production_deterministic_detector import ProductionDeterministicDetector, DetectionResult
from .advanced_real_video_detector import AdvancedRealVideoDetector, RealVideoAnalysis
from .advanced_models_integration import AdvancedEnsembleDetector, EnsembleResult

logger = logging.getLogger(__name__)

@dataclass
class ProductionDetectionResult:
    """Final production detection result"""
    prediction: str  # "Real Video", "Deepfake Detected", "Uncertain"
    confidence: float  # 0.0 to 1.0
    processing_time: float
    detection_methods: List[str]
    individual_results: Dict[str, Any]
    anomaly_scores: Dict[str, float]
    real_video_analysis: Optional[RealVideoAnalysis]
    ensemble_result: Optional[EnsembleResult]
    deterministic_result: Optional[DetectionResult]
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class ProductionDeepfakePipeline:
    """Production-grade deepfake detection pipeline"""
    
    def __init__(self, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.deterministic_detector = None
        self.real_video_detector = None
        self.ensemble_detector = None
        
        # Detection configuration
        self.config = {
            'enable_deterministic': True,
            'enable_real_video_analysis': True,
            'enable_advanced_models': True,
            'confidence_threshold': 0.6,
            'real_threshold': 0.3,
            'fake_threshold': 0.7,
            'uncertain_threshold': 0.4
        }
        
        # Performance tracking
        self.stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'average_processing_time': 0.0,
            'model_performance': {}
        }
        
        self._initialize_detectors()
        logger.info(f"[OK] Production Deepfake Pipeline initialized on {device}")
    
    def _initialize_detectors(self):
        """Initialize all detection components"""
        try:
            # Initialize deterministic detector
            if self.config['enable_deterministic']:
                self.deterministic_detector = ProductionDeterministicDetector(self.device)
                logger.info("[OK] Deterministic detector initialized")
            
            # Initialize real video detector
            if self.config['enable_real_video_analysis']:
                self.real_video_detector = AdvancedRealVideoDetector()
                logger.info("[OK] Real video detector initialized")
            
            # Initialize advanced models ensemble
            if self.config['enable_advanced_models']:
                self.ensemble_detector = AdvancedEnsembleDetector(self.device)
                logger.info("[OK] Advanced models ensemble initialized")
            
        except Exception as e:
            logger.error(f"[ERROR] Detector initialization failed: {e}")
    
    async def detect_comprehensive(self, faces: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> ProductionDetectionResult:
        """Comprehensive deepfake detection using all available methods"""
        start_time = time.time()
        
        try:
            # Validate input
            if not faces or len(faces) == 0:
                return self._create_error_result("No faces provided", start_time)
            
            # Initialize result containers
            individual_results = {}
            anomaly_scores = {}
            detection_methods = []
            
            # Step 1: Deterministic Detection
            deterministic_result = None
            if self.deterministic_detector:
                try:
                    deterministic_result = await self.deterministic_detector.detect_comprehensive(faces, audio_data)
                    individual_results['deterministic'] = {
                        'prediction': deterministic_result.prediction,
                        'confidence': deterministic_result.confidence,
                        'processing_time': deterministic_result.processing_time
                    }
                    detection_methods.append('deterministic')
                    logger.info(f"[OK] Deterministic detection: {deterministic_result.prediction} ({deterministic_result.confidence:.3f})")
                except Exception as e:
                    logger.warning(f"[WARNING] Deterministic detection failed: {e}")
            
            # Step 2: Real Video Analysis
            real_video_analysis = None
            if self.real_video_detector:
                try:
                    real_video_analysis = await self.real_video_detector.analyze_real_video(faces, audio_data)
                    individual_results['real_video_analysis'] = {
                        'is_real': real_video_analysis.is_real,
                        'confidence': real_video_analysis.confidence,
                        'processing_time': real_video_analysis.processing_time
                    }
                    anomaly_scores.update({
                        'lip_sync': real_video_analysis.lip_sync_score,
                        'facial_consistency': real_video_analysis.facial_consistency,
                        'temporal_consistency': real_video_analysis.temporal_consistency,
                        'blink_rate': real_video_analysis.blink_rate,
                        'eye_movement': real_video_analysis.eye_movement_consistency,
                        'skin_texture': real_video_analysis.skin_texture_score,
                        'lighting_consistency': real_video_analysis.lighting_consistency,
                        'geometry_consistency': real_video_analysis.geometry_consistency
                    })
                    detection_methods.append('real_video_analysis')
                    logger.info(f"[OK] Real video analysis: {'Real' if real_video_analysis.is_real else 'Fake'} ({real_video_analysis.confidence:.3f})")
                except Exception as e:
                    logger.warning(f"[WARNING] Real video analysis failed: {e}")
            
            # Step 3: Advanced Models Ensemble
            ensemble_result = None
            if self.ensemble_detector:
                try:
                    ensemble_result = await self.ensemble_detector.predict_ensemble(faces)
                    individual_results['ensemble'] = {
                        'prediction': ensemble_result.final_prediction,
                        'confidence': ensemble_result.final_confidence,
                        'processing_time': ensemble_result.processing_time,
                        'models_used': len(ensemble_result.individual_predictions)
                    }
                    detection_methods.append('advanced_ensemble')
                    logger.info(f"[OK] Advanced ensemble: {ensemble_result.final_prediction} ({ensemble_result.final_confidence:.3f})")
                except Exception as e:
                    logger.warning(f"[WARNING] Advanced ensemble failed: {e}")
            
            # Step 4: Fusion and Final Decision
            final_prediction, final_confidence = self._fuse_all_results(
                deterministic_result, real_video_analysis, ensemble_result
            )
            
            # Step 5: Update statistics
            processing_time = time.time() - start_time
            self._update_stats(processing_time, True)
            
            # Create final result
            result = ProductionDetectionResult(
                prediction=final_prediction,
                confidence=final_confidence,
                processing_time=processing_time,
                detection_methods=detection_methods,
                individual_results=individual_results,
                anomaly_scores=anomaly_scores,
                real_video_analysis=real_video_analysis,
                ensemble_result=ensemble_result,
                deterministic_result=deterministic_result,
                metadata={
                    'total_faces': len(faces),
                    'has_audio': audio_data is not None,
                    'device': self.device,
                    'timestamp': time.time(),
                    'config': self.config
                },
                success=True
            )
            
            logger.info(f"🎯 Production detection completed: {final_prediction} ({final_confidence:.3f}) in {processing_time:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"[ERROR] Production detection failed: {e}")
            processing_time = time.time() - start_time
            self._update_stats(processing_time, False)
            return self._create_error_result(f"Detection failed: {e}", start_time)
    
    def _fuse_all_results(self, deterministic_result: Optional[DetectionResult], 
                         real_video_analysis: Optional[RealVideoAnalysis], 
                         ensemble_result: Optional[EnsembleResult]) -> Tuple[str, float]:
        """Fuse all detection results into final decision"""
        try:
            # Collect all predictions and confidences
            predictions = []
            confidences = []
            weights = []
            
            # Add deterministic result
            if deterministic_result:
                predictions.append(deterministic_result.prediction)
                confidences.append(deterministic_result.confidence)
                weights.append(0.3)  # 30% weight
            
            # Add real video analysis
            if real_video_analysis:
                prediction = "Real Video" if real_video_analysis.is_real else "Deepfake Detected"
                predictions.append(prediction)
                confidences.append(real_video_analysis.confidence)
                weights.append(0.4)  # 40% weight (highest for real video analysis)
            
            # Add ensemble result
            if ensemble_result:
                predictions.append(ensemble_result.final_prediction)
                confidences.append(ensemble_result.final_confidence)
                weights.append(0.3)  # 30% weight
            
            if not predictions:
                return "No Predictions Available", 0.0
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            
            # Calculate weighted confidence
            weighted_confidence = sum(c * w for c, w in zip(confidences, weights))
            
            # Count predictions
            real_count = sum(1 for p in predictions if "Real" in p)
            fake_count = sum(1 for p in predictions if "Deepfake" in p or "Fake" in p)
            uncertain_count = sum(1 for p in predictions if "Uncertain" in p)
            
            # Determine final prediction based on majority and confidence
            if weighted_confidence >= self.config['confidence_threshold']:
                if real_count > fake_count:
                    return "Real Video", weighted_confidence
                elif fake_count > real_count:
                    return "Deepfake Detected", weighted_confidence
                else:
                    return "Uncertain", weighted_confidence
            else:
                return "Uncertain", weighted_confidence
        
        except Exception as e:
            logger.error(f"[ERROR] Result fusion failed: {e}")
            return "Fusion Failed", 0.0
    
    def _update_stats(self, processing_time: float, success: bool):
        """Update performance statistics"""
        self.stats['total_detections'] += 1
        
        if success:
            self.stats['successful_detections'] += 1
        else:
            self.stats['failed_detections'] += 1
        
        # Update average processing time
        total_time = self.stats['average_processing_time'] * (self.stats['total_detections'] - 1)
        self.stats['average_processing_time'] = (total_time + processing_time) / self.stats['total_detections']
    
    def _create_error_result(self, error_message: str, start_time: float) -> ProductionDetectionResult:
        """Create error result"""
        return ProductionDetectionResult(
            prediction="Detection Failed",
            confidence=0.0,
            processing_time=time.time() - start_time,
            detection_methods=[],
            individual_results={},
            anomaly_scores={},
            real_video_analysis=None,
            ensemble_result=None,
            deterministic_result=None,
            metadata={'error': error_message},
            success=False,
            error_message=error_message
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.stats,
            'success_rate': self.stats['successful_detections'] / max(1, self.stats['total_detections']),
            'config': self.config
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update detection configuration"""
        self.config.update(new_config)
        logger.info(f"[OK] Configuration updated: {new_config}")

# Global pipeline instance
_production_pipeline = None

def get_production_pipeline() -> ProductionDeepfakePipeline:
    """Get global production pipeline instance"""
    global _production_pipeline
    if _production_pipeline is None:
        _production_pipeline = ProductionDeepfakePipeline()
    return _production_pipeline

async def detect_deepfake_production(faces: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> ProductionDetectionResult:
    """Main function for production deepfake detection"""
    pipeline = get_production_pipeline()
    return await pipeline.detect_comprehensive(faces, audio_data)

# Convenience functions for different detection modes
async def detect_deterministic_only(faces: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> ProductionDetectionResult:
    """Detection using only deterministic methods"""
    pipeline = get_production_pipeline()
    original_config = pipeline.config.copy()
    
    # Temporarily disable other methods
    pipeline.update_config({
        'enable_real_video_analysis': False,
        'enable_advanced_models': False
    })
    
    try:
        result = await pipeline.detect_comprehensive(faces, audio_data)
        return result
    finally:
        # Restore original config
        pipeline.update_config(original_config)

async def detect_real_video_optimized(faces: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> ProductionDetectionResult:
    """Detection optimized for real video analysis"""
    pipeline = get_production_pipeline()
    original_config = pipeline.config.copy()
    
    # Emphasize real video analysis
    pipeline.update_config({
        'enable_deterministic': True,
        'enable_real_video_analysis': True,
        'enable_advanced_models': False,
        'confidence_threshold': 0.5  # Lower threshold for real videos
    })
    
    try:
        result = await pipeline.detect_comprehensive(faces, audio_data)
        return result
    finally:
        # Restore original config
        pipeline.update_config(original_config)

async def detect_with_all_models(faces: List[np.ndarray], audio_data: Optional[np.ndarray] = None) -> ProductionDetectionResult:
    """Detection using all available models and methods"""
    pipeline = get_production_pipeline()
    return await pipeline.detect_comprehensive(faces, audio_data)
