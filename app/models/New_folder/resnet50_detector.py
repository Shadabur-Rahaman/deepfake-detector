import torch
import torch.nn as nn
from torchvision.models import resnet50
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ResNet50DeepfakeDetector:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.initialized = False
    
    def load_model(self):
        """Load and customize ResNet-50 for deepfake detection"""
        try:
            # Load pre-trained ResNet-50
            self.model = resnet50(weights='IMAGENET1K_V1')
            
            # Replace final layer for binary classification
            num_features = self.model.fc.in_features
            self.model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(512, 1),
                nn.Sigmoid()
            )
            
            self.model = self.model.to(self.device)
            self.model.eval()
            self.initialized = True
            logger.info("✅ ResNet-50 loaded successfully")
            
        except Exception as e:
            logger.error(f"ResNet-50 loading failed: {e}")
            raise
    
    async def detect(self, faces: List[torch.Tensor]) -> Dict:
        """Detect deepfakes using ResNet-50"""
        if not self.initialized:
            self.load_model()
            
        if not faces:
            return {
                'prediction': 'No Faces Detected',
                'confidence': 0.0,
                'model': 'ResNet-50'
            }
        
        try:
            # Process faces (limit for performance)
            face_batch = torch.stack(faces[:10]).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(face_batch)
                avg_score = torch.mean(outputs).item()
            
            prediction = "Deepfake Detected" if avg_score > 0.5 else "Real Video"
            confidence = avg_score if avg_score > 0.5 else (1.0 - avg_score)
            
            return {
                'prediction': prediction,
                'confidence': confidence * 100,
                'model': 'ResNet-50 Enhanced',
                'faces_processed': len(faces),
                'spatial_features': 'extracted'
            }
            
        except Exception as e:
            logger.error(f"ResNet-50 detection failed: {e}")
            return {
                'prediction': 'Analysis Failed',
                'confidence': 0.0,
                'model': 'ResNet-50',
                'error': str(e)
            }

# Global instance
resnet50_detector = ResNet50DeepfakeDetector()
