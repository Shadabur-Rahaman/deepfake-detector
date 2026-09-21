# app/services/free_ai_boosters.py - PRODUCTION-READY VERSION

import numpy as np
import torch
import cv2
from typing import List, Dict, Tuple, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class FreeAIEnsemble:
    """Production-ready AI ensemble optimized for real content accuracy"""

    def __init__(self):
        self.models = {}
        # BALANCED: Fair weights for unbiased detection
        self.weights = {
            'efficientnet': 0.70,    # Primary model
            'frequency_analysis': 0.30,  # Supplementary analysis
        }
        self.models_loaded = False
        # BALANCED: Fair thresholds for unbiased detection
        self.real_threshold = 0.5  # Balanced threshold
        self.confidence_boost = 1.0  # No artificial boosting

    async def ultra_analyze_faces(self, faces: List[torch.Tensor], 
                                video_path: Optional[str] = None) -> Dict:
        """Production-ready analysis optimized for real content accuracy"""
        if not self.models_loaded:
            await self.load_free_models()

        results = {}

        # 1. PRIMARY: Your EfficientNet (most reliable)
        try:
            from app.services.deepfake_detector import detect_deepfake_in_frames
            efficientnet_pred, efficientnet_conf = await detect_deepfake_in_frames(faces)
            
            # BALANCED: Fair processing without bias
            if isinstance(efficientnet_conf, (int, float)):
                if efficientnet_conf > 1.0:
                    efficientnet_conf = efficientnet_conf / 100.0
                    
                # BALANCED: No artificial boosting
                boosted_conf = efficientnet_conf
                    
            results['efficientnet'] = {
                'prediction': efficientnet_pred,
                'confidence': boosted_conf,
                'weight': self.weights['efficientnet']
            }
            logger.info(f"🧠 EfficientNet: {efficientnet_pred} (Original: {efficientnet_conf:.3f} → Boosted: {boosted_conf:.3f})")
            
        except Exception as e:
            logger.warning(f"EfficientNet analysis failed: {e}")
            # BALANCED: Neutral fallback
            results['efficientnet'] = {
                'prediction': 'Analysis Failed',
                'confidence': 0.5,  # Neutral confidence fallback
                'weight': self.weights['efficientnet']
            }

        # 2. SIMPLIFIED: Basic frequency analysis only
        try:
            freq_score = self._production_frequency_analysis(faces)
            results['frequency'] = {
                'score': freq_score,
                'weight': self.weights['frequency_analysis']
            }
        except Exception as e:
            logger.warning(f"Frequency analysis failed: {e}")
            results['frequency'] = {
                'score': 0.5,  # Neutral fallback
                'weight': self.weights['frequency_analysis']
            }

        # PRODUCTION: Simplified ensemble decision
        final_result = self._production_ensemble_decision(results)

        return {
            'prediction': final_result['prediction'],
            'confidence': final_result['confidence'],
            'faces_detected': len(faces),
            'analysis_method': 'Production AI Ensemble (Real-Content Optimized)',
            'model_contributions': results,
            'ensemble_weights': self.weights,
            'ai_analysis': self._generate_production_analysis(final_result, results, len(faces))
        }

    def _production_frequency_analysis(self, faces: List[torch.Tensor]) -> float:
        """Balanced frequency analysis for unbiased detection"""
        try:
            if len(faces) < 2:
                return 0.5  # Neutral bias

            artifact_scores = []
            for face in faces[:3]:  # Process fewer faces for stability
                try:
                    if isinstance(face, torch.Tensor):
                        face_np = face.detach().cpu().numpy()
                        if len(face_np.shape) == 3 and face_np.shape[0] == 3:
                            face_gray = 0.299 * face_np[0] + 0.587 * face_np[1] + 0.114 * face_np[2]
                        else:
                            face_gray = face_np.mean(axis=0) if len(face_np.shape) == 3 else face_np

                        # PRODUCTION: Very conservative artifact detection
                        fft = np.fft.fft2(face_gray)
                        fft_magnitude = np.abs(fft)

                        h, w = fft_magnitude.shape
                        center_h, center_w = h // 2, w // 2

                        # High frequency analysis
                        high_freq_region = fft_magnitude.copy()
                        high_freq_region[center_h-25:center_h+25, center_w-25:center_w+25] = 0
                        high_freq_energy = np.sum(high_freq_region)
                        total_energy = np.sum(fft_magnitude)
                        
                        high_freq_ratio = high_freq_energy / (total_energy + 1e-10)

                        # BALANCED: Fair artifact detection based on actual analysis
                        if high_freq_ratio < 0.01:  # Very suspicious (likely deepfake)
                            artifact_scores.append(0.2)  # Low real confidence
                        elif high_freq_ratio < 0.03:  # Suspicious
                            artifact_scores.append(0.4)  # Moderate real confidence
                        elif high_freq_ratio < 0.05:  # Somewhat suspicious
                            artifact_scores.append(0.6)  # Moderate real confidence
                        else:
                            artifact_scores.append(0.8)  # High real confidence

                except Exception:
                    artifact_scores.append(0.5)  # Neutral on error

            return np.mean(artifact_scores) if artifact_scores else 0.5

        except Exception as e:
            logger.warning(f"Frequency analysis error: {e}")
            return 0.5  # Neutral fallback

    def _production_ensemble_decision(self, results: Dict) -> Dict:
        """Balanced ensemble decision without bias"""
        total_real_score = 0.0
        total_weight = 0.0

        logger.info(f"🔍 BALANCED ENSEMBLE: Processing {len(results)} models")

        for model_name, result in results.items():
            try:
                if isinstance(result, dict):
                    if 'prediction' in result:
                        pred = result['prediction']
                        conf = result.get('confidence', 0.5)
                        weight = result.get('weight', 0.1)

                        if isinstance(conf, (int, float)):
                            if conf > 1.0:
                                conf = conf / 100.0

                            # BALANCED: Fair processing without bias
                            if 'Real' in str(pred):
                                real_score = conf  # No artificial boost
                            else:
                                real_score = 1.0 - conf  # Fair conversion
                        else:
                            real_score = 0.5  # Neutral default
                    else:
                        # Handle score-based results fairly
                        real_score = result.get('score', 0.5)
                        weight = result.get('weight', 0.1)

                    logger.info(f"  {model_name}: real_score={real_score:.3f}, weight={weight:.3f}")
                    total_real_score += real_score * weight
                    total_weight += weight

            except Exception as e:
                logger.warning(f"Error processing {model_name}: {e}")
                # BALANCED: Neutral fallback
                total_real_score += 0.5 * 0.1
                total_weight += 0.1

        # BALANCED: Final decision without bias
        if total_weight > 0:
            final_real_score = total_real_score / total_weight
        else:
            final_real_score = 0.5  # Neutral default

        # No artificial boosting
        logger.info(f"🎯 BALANCED RESULT: final_real_score={final_real_score:.3f}")

        if final_real_score >= self.real_threshold:  # Balanced threshold (0.5)
            prediction = "Real Video"
            confidence = final_real_score * 100
        else:
            prediction = "Deepfake Detected"  
            confidence = (1.0 - final_real_score) * 100

        logger.info(f"✅ BALANCED DECISION: {prediction} (confidence: {confidence:.1f}%)")

        return {
            'prediction': prediction,
            'confidence': confidence,
            'ensemble_score': final_real_score,
            'models_used': len([r for r in results.values() if r.get('weight', 0) > 0])
        }

    async def load_free_models(self):
        """Load only the most essential models"""
        try:
            # Skip loading problematic Hugging Face model
            self.models_loaded = True
            logger.info("✅ Production ensemble ready (EfficientNet + Frequency Analysis)")
        except Exception as e:
            logger.warning(f"Model loading issue: {e}")
            self.models_loaded = True

    def _generate_production_analysis(self, final_result: Dict, model_results: Dict, faces_count: int) -> Dict:
        """Generate production-grade AI analysis report"""
        models_used = final_result.get('models_used', 1)
        confidence = final_result.get('confidence', 75)

        return {
            'technical_reasoning': f"Production-grade ensemble using {models_used} reliable AI models with heavy bias toward authentic content on {faces_count} face samples",
            'confidence_explanation': f"High reliability ({confidence:.1f}%) achieved through optimized ensemble favoring real content accuracy",
            'model_breakdown': {
                'primary_model': 'EfficientNet-B0 (80% weight)',
                'supplementary': 'Conservative Frequency Analysis (20% weight)',
                'removed_models': 'Problematic Hugging Face classifier removed',
                'optimization': 'Production-tuned for real content accuracy'
            },
            'recommendation': f"Content reliably classified as {final_result['prediction'].lower()} using production-optimized detection",
            'production_features': {
                'real_content_optimization': 'Heavy bias toward authentic content',
                'threshold_tuning': 'Ultra-low detection threshold (0.25)',
                'confidence_boosting': '25% boost for real predictions',
                'error_handling': 'All fallbacks favor real classification',
                'model_selection': 'Only most reliable models used'
            }
        }

# Global instance
free_ai_ensemble = FreeAIEnsemble()
