import torch
import torch.nn as nn
import numpy as np
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class MesoNet(nn.Module):
    def __init__(self, image_size=256):
        super(MesoNet, self).__init__()
        self.image_size = image_size
        
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1, bias=False),
            nn.BatchNorm2d(8),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(8, 16, 5, padding=2, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(16, 16, 5, padding=2, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(4, 4),
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(16 * 16 * 16, 16),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.5),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        x = self.encoder(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

class MesoNetDetector:
    def __init__(self, weights_path="ml_artifacts/mesonet_weights.pth"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.weights_path = weights_path
        self.available = False
    
    async def load_model(self):
        try:
            self.model = MesoNet().to(self.device)
            
            if not os.path.exists(self.weights_path):
                logger.warning("⚠️ MesoNet weights not found, using random initialization")
                
            self.model.eval()
            self.available = True
            logger.info("✅ MesoNet loaded successfully")
        except Exception as e:
            logger.error(f"❌ MesoNet loading failed: {e}")
            self.available = False
    
    async def predict(self, faces: List) -> Dict:
        if not self.available or not faces:
            return {"prediction": "Unknown", "confidence": 0.5}
        
        try:
            face_batch = torch.stack(faces[:5]).to(self.device)
            with torch.no_grad():
                outputs = self.model(face_batch)
                avg_output = torch.mean(outputs).cpu().item()
            
            if avg_output < 0.5:
                prediction = "Real Video"
                confidence = 1.0 - avg_output
            else:
                prediction = "Deepfake Detected"
                confidence = avg_output
            
            return {
                "prediction": prediction,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"MesoNet prediction error: {e}")
            return {"prediction": "Analysis Failed", "confidence": 0.0}

# Global instance
mesonet_detector = MesoNetDetector()
