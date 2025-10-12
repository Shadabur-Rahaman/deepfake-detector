import torch
import numpy as np
import time
import logging
from typing import Dict, List, Optional
from pathlib import Path

# Import your existing detector
from app.services.deepfake_detector import detect_deepfake_in_frames

logger = logging.getLogger(__name__)

class MultiStageDeepfakeDetector:
    """Enhanced detector using your trained model as the base"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models_loaded = False
        
        # Paths for your project structure
        self.base_dir = Path(__file__).parent.parent.parent  # deepfake-detector
        self.model_artifacts_path = self.base_dir / "ml_artifacts"
        
        # Your existing model
        self.efficientnet_model = None
        
        # Multi-stage components (loaded only when available)
        self.advanced_models_available = False
        
    async def load_models(self):
        """Load available models"""
        try:
            logger.info("Loading detection models...")
            
            # Your main model is loaded automatically when first used
            self.models_loaded = True
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    async def analyze_video(self, video_path: str) -> Dict:
        """Analyze video using your existing pipeline + future enhancements"""
        try:
            if not self.models_loaded:
                await self.load_models()
            
            # Use your existing video processor
            from app.services.video_processor import extract_faces_from_video
            
            # Extract faces
            faces = extract_faces_from_video(video_path)
            
            if not faces:
                return {
                    "prediction": "No Faces Detected",
                    "confidence": 0.0,
                    "faces_found": 0,
                    "model_used": "Face Detection Failed"
                }
            
            # Run detection using your trained model
            result, confidence = await detect_deepfake_in_frames(faces)
            
            return {
                "prediction": result,
                "confidence": confidence * 100,  # Convert to percentage
                "faces_found": len(faces),
                "model_used": "EfficientNet-B0 Fine-tuned",
                "enhanced_analysis": False,  # Will be True when multi-stage is implemented
                "processing_complete": True
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            raise

# Initialize detector instance
detector = MultiStageDeepfakeDetector()
