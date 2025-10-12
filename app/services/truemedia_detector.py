# app/services/truemedia_detector.py - ENHANCED with Free AI tools
import numpy as np
import torch
from typing import Dict, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

async def enhanced_deepfake_detection(faces: List[torch.Tensor], 
                                    video_path: Optional[str] = None) -> Dict:
    """
    Ultra-enhanced detection using free AI ensemble + your existing models
    TARGET: 95%+ accuracy using 100% FREE tools
    """
    try:
        # Try to use the free AI ensemble first
        try:
            from app.services.free_ai_boosters import free_ai_ensemble
            
            print("🚀 Using Ultra-Free AI Ensemble (5+ models)")
            result_data = await free_ai_ensemble.ultra_analyze_faces(faces, video_path)
            
            # Add ultra enhancement flag
            result_data['ultra_enhanced'] = True
            result_data['models_used'] = 'Free AI Ensemble (EfficientNet + HuggingFace + Temporal + Frequency + Landmarks)'
            
            return result_data
            
        except ImportError:
            print("⚠️ Free AI ensemble not available, using enhanced detector")
    
        # Fallback to enhanced detector
        try:
            from app.services.enhanced_detector import enhanced_detector
            
            print("🧠 Using Enhanced Detector")
            result_data = enhanced_detector.enhanced_analyze_faces(faces)
            
            if isinstance(result_data, dict):
                result_data['fallback_method'] = 'Enhanced Detector'
                return result_data
            else:
                # Handle tuple return format
                prediction, confidence = result_data
                return {
                    'prediction': prediction,
                    'confidence': confidence * 100 if confidence <= 1.0 else confidence,
                    'faces_detected': len(faces),
                    'fallback_method': 'Enhanced Detector',
                    'ai_analysis': {
                        'technical_reasoning': f"Enhanced analysis using EfficientNet with ensemble methods on {len(faces)} face samples",
                        'confidence_explanation': f"High confidence in {prediction.lower()} classification",
                        'recommendation': f"Content classified as {prediction.lower()} using advanced AI analysis"
                    },
                    'model_results': {
                        'primary_model': 'Enhanced EfficientNet',
                        'faces_analyzed': len(faces)
                    }
                }
                
        except ImportError:
            print("⚠️ Enhanced detector not available, using standard")
    
        # Final fallback to basic detection
        try:
            from app.services.deepfake_detector import detect_deepfake_in_frames
            
            print("🔍 Using Standard EfficientNet")
            prediction, confidence = await detect_deepfake_in_frames(faces)
            
            return {
                'prediction': prediction,
                'confidence': confidence * 100 if confidence <= 1.0 else confidence,
                'faces_detected': len(faces),
                'fallback_method': 'Standard EfficientNet',
                'ai_analysis': {
                    'technical_reasoning': f"Standard analysis using EfficientNet model on {len(faces)} face samples",
                    'confidence_explanation': f"Moderate confidence in {prediction.lower()} classification",
                    'recommendation': f"Content classified as {prediction.lower()} using standard AI model"
                },
                'model_results': {
                    'primary_model': 'Standard EfficientNet',
                    'faces_analyzed': len(faces),
                    'note': 'Consider upgrading to enhanced detection for higher accuracy'
                }
            }
            
        except Exception as standard_error:
            logger.error(f"Standard detection also failed: {standard_error}")
            
            return {
                'prediction': 'Analysis Failed',
                'confidence': 0.0,
                'faces_detected': len(faces),
                'error': str(standard_error),
                'ai_analysis': {
                    'technical_reasoning': 'All detection methods failed due to technical issues',
                    'confidence_explanation': 'Unable to analyze content',
                    'recommendation': 'Please try uploading the video again or contact support'
                },
                'model_results': {
                    'error': 'Complete detection pipeline failure'
                }
            }
            
    except Exception as e:
        logger.error(f"Enhanced deepfake detection failed completely: {e}")
        
        return {
            'prediction': 'System Error',
            'confidence': 0.0,
            'faces_detected': len(faces),
            'system_error': str(e),
            'ai_analysis': {
                'technical_reasoning': 'System encountered a critical error during analysis',
                'confidence_explanation': 'Analysis could not be completed',
                'recommendation': 'Please report this issue to the development team'
            }
        }