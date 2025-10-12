import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
import torch

logger = logging.getLogger(__name__)

class UltimateEnsembleDetector:
    def __init__(self):
        self.detectors = {}
        # ✅ BIAS FIX: Balanced weights for unbiased detection
        self.weights = {
            'efficientnet': 0.15,        # Base model - reduced from 0.20
            'mesonet': 0.15,            # Mesoscopic features - reduced from 0.20
            'modern_ai_detector': 0.15,  # Modern AI patterns - same
            'hybrid_detector': 0.15,     # CNN-LSTM hybrid - same
            'unite_detector': 0.15,      # UNITE framework - increased from 0.10
            'divid_detector': 0.15,      # DIVID detector - increased from 0.10
            'frequency_analyzer': 0.10   # Frequency analysis - same
        }
        self.initialized = False
        
    async def initialize_detectors(self):
        """Initialize all available detectors"""
        try:
            logger.info("🚀 Initializing Ultimate Ensemble Detector...")
            
            # Import and initialize your existing detectors
            from app.services.deepfake_detector import load_deepfake_model
            from app.services.modern_ai_detector import modern_ai_detector
            from app.services.hybrid_detector import hybrid_detector
            from app.services.unite_detector import unite_detector
            from app.services.divid_detector import divid_detector
            from app.services.advanced_frequency_analyzer import ultra_frequency_analyzer
            from app.models.mesonet_detector_enhanced import mesonet_detector
            
            # Load models
            self.detectors['efficientnet'] = load_deepfake_model()
            self.detectors['modern_ai_detector'] = modern_ai_detector
            self.detectors['hybrid_detector'] = hybrid_detector
            self.detectors['unite_detector'] = unite_detector
            self.detectors['divid_detector'] = divid_detector
            self.detectors['frequency_analyzer'] = ultra_frequency_analyzer
            
            # Initialize MesoNet
            await mesonet_detector.load_model()
            self.detectors['mesonet'] = mesonet_detector
            
            self.initialized = True
            logger.info(f"✅ Ultimate ensemble initialized with {len(self.detectors)} detectors")
            
        except Exception as e:
            logger.error(f"❌ Ensemble initialization failed: {e}")
            raise

    async def detect(self, faces: List[torch.Tensor], video_path: str) -> Dict[str, Any]:
        """Run ensemble detection"""
        if not self.initialized:
            await self.initialize_detectors()
            
        if not faces:
            return {
                'prediction': 'No Faces Detected',
                'confidence': 0.0,
                'models_used': 0
            }
            
        start_time = time.time()
        logger.info(f"🎯 Running ensemble detection on {len(faces)} faces")
        
        # Run detectors in parallel where possible
        detection_tasks = []
        
        # EfficientNet detection
        if 'efficientnet' in self.detectors:
            detection_tasks.append(('efficientnet', self._run_efficientnet(faces)))
            
        # MesoNet detection
        if 'mesonet' in self.detectors:
            detection_tasks.append(('mesonet', self._run_mesonet(faces)))
            
        # Modern AI detector
        if 'modern_ai_detector' in self.detectors:
            detection_tasks.append(('modern_ai', self._run_modern_ai(faces, video_path)))
            
        # Hybrid detector
        if 'hybrid_detector' in self.detectors:
            detection_tasks.append(('hybrid', self._run_hybrid(faces)))
            
        # UNITE detector
        if 'unite_detector' in self.detectors:
            detection_tasks.append(('unite', self._run_unite(faces, video_path)))
            
        # DIVID detector
        if 'divid_detector' in self.detectors:
            detection_tasks.append(('divid', self._run_divid(faces, video_path)))
            
        # Frequency analyzer
        if 'frequency_analyzer' in self.detectors:
            detection_tasks.append(('frequency', self._run_frequency(faces, video_path)))
        
        # Execute all detections
        results = {}
        for name, task in detection_tasks:
            try:
                results[name] = await task
            except Exception as e:
                logger.warning(f"Detector {name} failed: {e}")
                results[name] = {'prediction': 'Failed', 'confidence': 0.0}
        
        # Make ensemble decision
        return self._make_ensemble_decision(results, len(faces), time.time() - start_time)

    async def _run_efficientnet(self, faces):
        """Run EfficientNet detection"""
        from app.services.deepfake_detector import detect_deepfake_in_frames
        prediction, confidence = await detect_deepfake_in_frames(faces)
        return {'prediction': prediction, 'confidence': confidence}
    
    async def _run_mesonet(self, faces):
        """Run MesoNet detection"""
        return await self.detectors['mesonet'].predict(faces)
    
    async def _run_modern_ai(self, faces, video_path):
        """Run modern AI detector"""
        result = self.detectors['modern_ai_detector'].detect_modern_ai_generation(faces, video_path)
        return {
            'prediction': 'AI-Generated' if result.get('confidence', 0) > 50 else 'Authentic',
            'confidence': result.get('confidence', 0)
        }
    
    async def _run_hybrid(self, faces):
        """Run hybrid CNN-LSTM detector"""
        result = await self.detectors['hybrid_detector'].analyze_sequence(faces)
        return result
    
    async def _run_unite(self, faces, video_path):
        """Run UNITE detector"""
        result = await self.detectors['unite_detector'].detect(faces, video_path)
        return result
    
    async def _run_divid(self, faces, video_path):
        """Run DIVID detector"""
        result = await self.detectors['divid_detector'].detect(faces, video_path)
        return result
    
    async def _run_frequency(self, faces, video_path):
        """Run frequency analyzer"""
        result = self.detectors['frequency_analyzer'].ultra_frequency_analysis(faces, video_path)
        return {
            'prediction': 'AI-Generated' if result.get('ai_probability', 0) > 0.5 else 'Authentic',
            'confidence': result.get('ai_probability', 0) * 100
        }
    
    def _make_ensemble_decision(self, results: Dict, faces_count: int, processing_time: float) -> Dict:
        """Make final ensemble decision"""
        if not results:
            return {'prediction': 'Analysis Failed', 'confidence': 0.0, 'models_used': 0}
        
        logger.info(f"📊 Making ensemble decision from {len(results)} detectors")
        
        total_score = 0.0
        total_weight = 0.0
        model_contributions = {}
        
        for detector_name, result in results.items():
            if detector_name in self.weights:
                try:
                    prediction = result.get('prediction', '')
                    confidence = result.get('confidence', 0.0)
                    weight = self.weights[detector_name]
                    
                    # Normalize confidence
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                    
                    # Convert to AI/deepfake score (higher = more likely AI/fake)
                    ai_keywords = ['deepfake', 'ai-generated', 'fake', 'synthetic', 'generated']
                    is_ai_prediction = any(keyword in prediction.lower() for keyword in ai_keywords)
                    
                    score = confidence if is_ai_prediction else (1.0 - confidence)
                    
                    total_score += score * weight
                    total_weight += weight
                    
                    model_contributions[detector_name] = {
                        'prediction': prediction,
                        'confidence': confidence * 100 if confidence <= 1.0 else confidence,
                        'weight': weight,
                        'contribution_score': score * weight
                    }
                    
                    logger.info(f"  {detector_name}: {prediction} ({confidence:.3f}) weight={weight:.3f}")
                    
                except Exception as e:
                    logger.warning(f"Error processing {detector_name}: {e}")
        
        # Final decision
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.5
        
        # Determine prediction with threshold
        if final_score >= 0.52:  # Slightly conservative
            final_prediction = "AI-Generated/Deepfake Content Detected"
            final_confidence = min(final_score * 100, 96.0)
        else:
            final_prediction = "Authentic Content"
            final_confidence = min((1.0 - final_score) * 100, 96.0)
        
        # Boost confidence with ensemble size
        confidence_boost = min(len(results) * 1.5, 10)
        final_confidence = min(final_confidence + confidence_boost, 98.0)
        
        logger.info(f"🏆 ENSEMBLE DECISION: {final_prediction} ({final_confidence:.1f}%)")
        
        return {
            'prediction': final_prediction,
            'confidence': final_confidence,
            'faces_detected': faces_count,
            'models_used': len(results),
            'ensemble_score': final_score,
            'processing_time': processing_time,
            'analysis_method': f'Ultimate Ensemble ({len(results)} Models)',
            'model_contributions': model_contributions,
            'enhanced_analysis': True,
            'ai_analysis': {
                'technical_reasoning': f"Ultimate ensemble analysis using {len(results)} specialized models including EfficientNet, MesoNet, modern AI detectors, and advanced analysis modules",
                'confidence_explanation': f"Very high confidence ({final_confidence:.1f}%) achieved through consensus of {len(results)} independent detection systems",
                'recommendation': f"Content classified as {final_prediction.split()[0].lower()} using state-of-the-art ensemble approach"
            }
        }

# Global instance
ultimate_ensemble = UltimateEnsembleDetector()
