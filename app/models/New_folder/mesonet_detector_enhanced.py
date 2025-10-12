import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Dict
import logging
import os

logger = logging.getLogger(__name__)

class MesoNet(nn.Module):
    """MesoNet architecture for deepfake detection"""
    def __init__(self, image_size=256):
        super(MesoNet, self).__init__()
        
        # Encoder layers
        self.conv1 = nn.Conv2d(3, 8, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 8, 5, padding=2)
        self.bn2 = nn.BatchNorm2d(8)
        
        self.conv3 = nn.Conv2d(8, 16, 5, padding=2)
        self.bn3 = nn.BatchNorm2d(16)
        self.conv4 = nn.Conv2d(16, 16, 5, padding=2)
        self.bn4 = nn.BatchNorm2d(16)
        
        self.conv5 = nn.Conv2d(16, 32, 5, padding=2)
        self.bn5 = nn.BatchNorm2d(32)
        self.conv6 = nn.Conv2d(32, 32, 5, padding=2)
        self.bn6 = nn.BatchNorm2d(32)
        
        self.conv7 = nn.Conv2d(32, 64, 5, padding=2)
        self.bn7 = nn.BatchNorm2d(64)
        self.conv8 = nn.Conv2d(64, 64, 5, padding=2)
        self.bn8 = nn.BatchNorm2d(64)
        
        self.maxpool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)
        
        # Calculate feature map size
        feature_size = (image_size // (2**4)) ** 2 * 64  # 4 maxpool operations
        
        # Classifier
        self.fc1 = nn.Linear(feature_size, 16)
        self.fc2 = nn.Linear(16, 1)
        
    def forward(self, x):
        # First block
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.maxpool(x)
        
        # Second block
        x = F.relu(self.bn3(self.conv3(x)))
        x = F.relu(self.bn4(self.conv4(x)))
        x = self.maxpool(x)
        
        # Third block
        x = F.relu(self.bn5(self.conv5(x)))
        x = F.relu(self.bn6(self.conv6(x)))
        x = self.maxpool(x)
        
        # Fourth block
        x = F.relu(self.bn7(self.conv7(x)))
        x = F.relu(self.bn8(self.conv8(x)))
        x = self.maxpool(x)
        
        # Classifier
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x

class MesoNetDetector:
    def __init__(self, model_path: str = None, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.model_path = model_path or "ml_artifacts/mesonet_weights.pth"
        self.initialized = False

    async def load_model(self):
        """Load MesoNet model"""
        try:
            self.model = MesoNet(image_size=224)
            
            # Try to load weights if available
            if os.path.exists(self.model_path):
                state_dict = torch.load(self.model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                logger.info(f"✅ MesoNet weights loaded from {self.model_path}")
            else:
                logger.warning("⚠️ MesoNet weights not found, using randomly initialized model")
            
            self.model.to(self.device)
            self.model.eval()
            self.initialized = True
            logger.info("✅ MesoNet model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load MesoNet: {e}")
            self.model = None
            self.initialized = False

    async def predict(self, faces: List[torch.Tensor]) -> Dict:
        """Predict using MesoNet"""
        if not self.initialized:
            await self.load_model()
            
        if self.model is None or not faces:
            return {
                "prediction": "Unknown", 
                "confidence": 0.0,
                "model": "MesoNet"
            }

        try:
            # Prepare batch
            face_batch = torch.stack(faces[:10]).to(self.device)  # Limit batch size
            
            with torch.no_grad():
                outputs = self.model(face_batch)
                probabilities = torch.sigmoid(outputs).cpu().numpy().flatten()
                
            # Calculate metrics
            mean_prob = np.mean(probabilities)
            
            # MesoNet typically outputs high values for deepfakes
            if mean_prob >= 0.5:
                prediction = "Deepfake Detected"
                confidence = float(mean_prob)
            else:
                prediction = "Real Video"
                confidence = float(1.0 - mean_prob)
                
            return {
                "prediction": prediction,
                "confidence": confidence * 100,
                "model": "MesoNet",
                "faces_processed": len(faces),
                "mesoscopic_features": "analyzed"
            }
            
        except Exception as e:
            logger.error(f"❌ MesoNet prediction failed: {e}")
            return {
                "prediction": "Analysis Failed",
                "confidence": 0.0,
                "model": "MesoNet",
                "error": str(e)
            }

# Global instance
mesonet_detector = MesoNetDetector()
