import torch
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List, Optional
import time
import logging

logger = logging.getLogger(__name__)

class MultiStageDeepfakeDetector:
    """Multi-stage detector adapted for your project structure"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Paths for YOUR project structure
        self.base_dir = Path(__file__).parent.parent.parent  # deepfake-detector
        self.model_artifacts_path = self.base_dir / "ml_artifacts"
        self.models_loaded = False
        
        # Your existing model integration
        from app.services.deepfake_detector import load_deepfake_model
        self.main_model_loader = load_deepfake_model
        
    async def load_models(self):
        """Load all detection models"""
        try:
            logger.info("Loading multi-stage detection models...")
            
            # Load your main trained model
            self.main_model = self.main_model_loader()
            
            # Here you can add the other specialized models as you implement them
            # self.face_detector = YOLOv8Face()
            # self.resnet50 = ResNet50Detector()
            # etc.
            
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
            from app.services.deepfake_detector import detect_deepfake_in_frames
            
            # Extract faces
            faces = extract_faces_from_video(video_path)
            
            if not faces:
                return {
                    "prediction": "No Faces Detected",
                    "confidence": 0.0,
                    "faces_found": 0
                }
            
            # Run detection
            result, confidence = await detect_deepfake_in_frames(faces)
            
            return {
                "prediction": result,
                "confidence": confidence * 100,  # Convert to percentage
                "faces_found": len(faces),
                "model_used": "EfficientNet-B0 Fine-tuned",
                "processing_complete": True
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            raise

# Initialize detector
detector = MultiStageDeepfakeDetector()
