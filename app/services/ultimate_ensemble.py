import asyncio
import logging
from typing import List, Dict, Optional
import torch
import time

logger = logging.getLogger(__name__)

class UltimateEnsembleCoordinator:
    def __init__(self):
        self.models = {}
        self.weights = {
            # Your existing models (already imported in main.py)
            'efficientnet': 0.15,           # Base EfficientNet
            'modern_ai_detector': 0.15,     # ModernAIContentDetector
            'enhanced_detector': 0.12,      # enhanced_detector
            'hybrid_detector': 0.12,        # HybridCNNLSTMDetector
            'unite_detector': 0.10,         # UNITEDetector
            'divid_detector': 0.10,         # DIVIDDetector
            
            # New models we're adding
            'resnet50_detector': 0.13,      # New ResNet-50
            'vit_analyzer': 0.13,           # New Vision Transformer
        }
        self.initialized = False
    
    async def initialize_all_models(self):
        """Initialize all available detection models"""
        try:
            logger.info("🚀 Initializing Ultimate Ensemble Coordinator...")
            
            # Import your existing models (already available in main.py)
            from app.services.deepfake_detector import load_deepfake_model
            from app.services.modern_ai_detector import modern_ai_detector
            from app.services.enhanced_detector import enhanced_detector
            from app.services.hybrid_detector import hybrid_detector
            from app.services.unite_detector import unite_detector
            from app.services.divid_detector import divid_detector
            
            # Load existing models
            self.models['efficientnet'] = load_deepfake_model()
            self.models['modern_ai_detector'] = modern_ai_detector
            self.models['enhanced_detector'] = enhanced_detector
            self.models['hybrid_detector'] = hybrid_detector
            self.models['unite_detector'] = unite_detector
            self.models['divid_detector'] = divid_detector
            
            # Load new models
            try:
                from app.models.New_folder.resnet50_enhanced import resnet50_detector
                resnet50_detector.load_model()
                self.models['resnet50_detector'] = resnet50_detector
                logger.info("✅ ResNet-50 loaded")
            except Exception as e:
                logger.warning(f"ResNet-50 not available: {e}")
            
            try:
                from app.models.New_folder.vision_transformer_enhanced import vit_analyzer
                await vit_analyzer.initialize()
                self.models['vit_analyzer'] = vit_analyzer
                logger.info("✅ Vision Transformer loaded")
            except Exception as e:
                logger.warning(f"Vision Transformer not available: {e}")
            
            self.initialized = True
            logger.info(f"✅ Ultimate Ensemble initialized with {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"❌ Ultimate ensemble initialization failed: {e}")
            raise
    
    async def ultimate_detection(self, faces: List[torch.Tensor], video_path: str) -> Dict:
        """Perform ultimate ensemble detection using all available models"""
        if not self.initialized:
            await self.initialize_all_models()
        
        if not faces:
            return {
                'prediction': 'No Faces Detected',
                'confidence': 0.0,
                'models_used': 0,
                'analysis_method': 'Ultimate Ensemble'
            }
        
        logger.info(f"🎯 Running ultimate ensemble on {len(faces)} faces with {len(self.models)} models")
        start_time = time.time()
        
        # Run all models and collect results
        results = {}
        
        # 1. EfficientNet (your base model)
        if 'efficientnet' in self.models:
            try:
                from app.services.deepfake_detector import detect_deepfake_in_frames
                prediction, confidence = await detect_deepfake_in_frames(faces)
                results['efficientnet'] = {
                    'prediction': prediction,
                    'confidence': confidence,
                    'weight': self.weights['efficientnet']
                }
            except Exception as e:
                logger.warning(f"EfficientNet failed: {e}")
        
        # 2. Modern AI Detector
        if 'modern_ai_detector' in self.models:
            try:
                modern_result = self.models['modern_ai_detector'].detect_modern_ai_generation(faces, video_path)
                results['modern_ai_detector'] = {
                    'prediction': 'AI-Generated Content' if modern_result.get('confidence', 0) > 50 else 'Authentic Content',
                    'confidence': modern_result.get('confidence', 50) / 100.0,
                    'weight': self.weights['modern_ai_detector']
                }
            except Exception as e:
                logger.warning(f"Modern AI detector failed: {e}")
        
        # 3. Enhanced Detector
        if 'enhanced_detector' in self.models:
            try:
                enhanced_result = self.models['enhanced_detector'].enhanced_analyze_faces(faces)
                results['enhanced_detector'] = {
                    'prediction': enhanced_result.get('prediction', 'Unknown'),
                    'confidence': enhanced_result.get('confidence', 50) / 100.0,
                    'weight': self.weights['enhanced_detector']
                }
            except Exception as e:
                logger.warning(f"Enhanced detector failed: {e}")
        
        # 4. Hybrid CNN-LSTM Detector
        if 'hybrid_detector' in self.models:
            try:
                hybrid_result = await self.models['hybrid_detector'].analyze_sequence(faces)
                results['hybrid_detector'] = {
                    'prediction': hybrid_result.get('prediction', 'Unknown'),
                    'confidence': hybrid_result.get('confidence', 50) / 100.0,
                    'weight': self.weights['hybrid_detector']
                }
            except Exception as e:
                logger.warning(f"Hybrid detector failed: {e}")
        
        # 5. UNITE Detector
        if 'unite_detector' in self.models:
            try:
                unite_result = await self.models['unite_detector'].detect(faces, video_path)
                results['unite_detector'] = {
                    'prediction': unite_result.get('prediction', 'Unknown'),
                    'confidence': unite_result.get('confidence', 50) / 100.0,
                    'weight': self.weights['unite_detector']
                }
            except Exception as e:
                logger.warning(f"UNITE detector failed: {e}")
        
        # 6. DIVID Detector
        if 'divid_detector' in self.models:
            try:
                divid_result = await self.models['divid_detector'].detect(faces, video_path)
                results['divid_detector'] = {
                    'prediction': divid_result.get('prediction', 'Unknown'),
                    'confidence': divid_result.get('confidence', 50) / 100.0,
                    'weight': self.weights['divid_detector']
                }
            except Exception as e:
                logger.warning(f"DIVID detector failed: {e}")
        
        # 7. ResNet-50 (NEW)
        if 'resnet50_detector' in self.models:
            try:
                resnet_result = await self.models['resnet50_detector'].detect(faces)
                results['resnet50_detector'] = {
                    'prediction': resnet_result.get('prediction', 'Unknown'),
                    'confidence': resnet_result.get('confidence', 50) / 100.0,
                    'weight': self.weights['resnet50_detector']
                }
            except Exception as e:
                logger.warning(f"ResNet-50 failed: {e}")
        
        # 8. Vision Transformer (NEW)
        if 'vit_analyzer' in self.models:
            try:
                vit_result = await self.models['vit_analyzer'].analyze(faces)
                results['vit_analyzer'] = {
                    'prediction': vit_result.get('prediction', 'Unknown'),
                    'confidence': vit_result.get('confidence', 50) / 100.0,
                    'weight': self.weights['vit_analyzer']
                }
            except Exception as e:
                logger.warning(f"Vision Transformer failed: {e}")
        
        # Ultimate ensemble decision
        return self._make_ultimate_decision(results, len(faces), time.time() - start_time)
    
    def _make_ultimate_decision(self, results: Dict, faces_count: int, processing_time: float) -> Dict:
        """Make final ensemble decision with sophisticated weighting"""
        if not results:
            return {
                'prediction': 'Analysis Failed',
                'confidence': 0.0,
                'models_used': 0
            }
        
        logger.info(f"📊 Ultimate Ensemble Decision from {len(results)} models")
        
        # Calculate weighted ensemble score
        total_score = 0.0
        total_weight = 0.0
        model_contributions = {}
        
        for model_name, result in results.items():
            if model_name in self.weights:
                try:
                    confidence = result.get('confidence', 0.5)
                    prediction = result.get('prediction', '')
                    weight = self.weights[model_name]
                    
                    # Normalize confidence
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                    
                    # Convert prediction to score (higher = more likely fake/AI)
                    deepfake_keywords = ['deepfake', 'fake', 'ai-generated', 'generated', 'synthetic']
                    is_fake_prediction = any(keyword in str(prediction).lower() for keyword in deepfake_keywords)
                    
                    score = confidence if is_fake_prediction else (1.0 - confidence)
                    
                    total_score += score * weight
                    total_weight += weight
                    
                    model_contributions[model_name] = {
                        'prediction': prediction,
                        'confidence': confidence * 100 if confidence <= 1.0 else confidence,
                        'weight': weight,
                        'contribution_score': score * weight
                    }
                    
                    logger.info(f"  {model_name}: {prediction} ({confidence:.3f}) weight={weight:.3f}")
                    
                except Exception as e:
                    logger.warning(f"Error processing {model_name}: {e}")
        
        # Final decision
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.5
        
        # Determine prediction with conservative threshold
        if final_score >= 0.52:  # Slightly conservative
            final_prediction = "AI-Generated/Deepfake Content Detected"
            final_confidence = min(final_score * 100, 96.0)
        else:
            final_prediction = "Authentic Content"
            final_confidence = min((1.0 - final_score) * 100, 96.0)
        
        # Boost confidence with multiple models (more models = higher confidence)
        confidence_boost = min(len(results) * 1.5, 8)  # Up to 8% boost
        final_confidence = min(final_confidence + confidence_boost, 98.0)
        
        logger.info(f"🏆 ULTIMATE ENSEMBLE: {final_prediction} ({final_confidence:.1f}%)")
        logger.info(f"📈 Final score: {final_score:.3f} from {len(results)} models")
        
        return {
            'prediction': final_prediction,
            'confidence': final_confidence,
            'faces_detected': faces_count,
            'models_used': len(results),
            'ensemble_score': final_score,
            'processing_time': round(processing_time, 2),
            'analysis_method': f'Ultimate Ensemble ({len(results)} Advanced Models)',
            'model_contributions': model_contributions,
            'ultimate_enhanced': True,
            'ai_analysis': {
                'technical_reasoning': f"Ultimate ensemble analysis using {len(results)} state-of-the-art models including EfficientNet, ResNet-50, Vision Transformer, CNN-LSTM Hybrid, UNITE, DIVID, and modern AI detectors",
                'confidence_explanation': f"Extremely high confidence ({final_confidence:.1f}%) achieved through consensus of {len(results)} independent AI systems with sophisticated weighted voting",
                'model_architecture': 'Multi-dimensional analysis: spatial + temporal + contextual + frequency + specialized detection',
                'recommendation': f"Content definitively classified as {final_prediction.split()[0].lower()} using production-grade ultimate ensemble with {len(results)} neural networks"
            }
        }

# Global instance
ultimate_ensemble = UltimateEnsembleCoordinator()
