# advanced_models/mesonet_detector.py - FIXED VERSION
import torch
import torch.nn as nn
import numpy as np
import os
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

class MesoNet(nn.Module):
    """MesoNet architecture for deepfake detection"""
    
    def __init__(self):
        super(MesoNet, self).__init__()
        
        # Mesoscopic CNN layers
        self.conv1 = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 8, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm2d(8)
        self.conv3 = nn.Conv2d(8, 16, kernel_size=5, padding=2)
        self.bn3 = nn.BatchNorm2d(16)
        self.conv4 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn4 = nn.BatchNorm2d(16)
        
        # Fully connected layers
        self.fc1 = nn.Linear(16 * 14 * 14, 16)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(16, 1)
        
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(2, 2)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # Mesoscopic feature extraction
        x = self.maxpool(self.relu(self.bn1(self.conv1(x))))
        x = self.maxpool(self.relu(self.bn2(self.conv2(x))))
        x = self.maxpool(self.relu(self.bn3(self.conv3(x))))
        x = self.maxpool(self.relu(self.bn4(self.conv4(x))))
        
        # Classification
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        
        return x

class AdvancedMesoNetDetector:
    """MesoNet detector integration for your ensemble"""
    
    def __init__(self):
        self.model = MesoNet()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model_loaded = False
    
    async def load_model(self, model_path: str = None):
        """Load pre-trained MesoNet model"""
        try:
            if model_path and os.path.exists(model_path):
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info("✅ MesoNet model loaded from checkpoint")
            else:
                logger.info("✅ MesoNet initialized with random weights (needs training)")
            
            self.model.eval()
            self.model_loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load MesoNet: {e}")
            raise
    
    async def predict(self, faces: List) -> Dict:
        """MesoNet prediction on face tensors"""
        if not self.model_loaded:
            await self.load_model()
        
        try:
            predictions = []
            
            # Convert numpy arrays to tensors if needed
            processed_faces = []
            for face in faces[:5]:  # Process first 5 faces
                if isinstance(face, np.ndarray):
                    # Convert numpy to tensor and normalize
                    face_tensor = torch.from_numpy(face).float()
                    if face_tensor.dim() == 3:
                        face_tensor = face_tensor.unsqueeze(0)
                    processed_faces.append(face_tensor)
                elif isinstance(face, torch.Tensor):
                    processed_faces.append(face)
            
            if not processed_faces:
                return {
                    "prediction": "No Valid Faces",
                    "confidence": 0.0,
                    "faces_processed": 0
                }
            
            for face_tensor in processed_faces:
                # Ensure correct input size (224x224 -> 112x112 for MesoNet)
                face_resized = torch.nn.functional.interpolate(
                    face_tensor.unsqueeze(0), 
                    size=(112, 112), 
                    mode='bilinear', 
                    align_corners=False
                )
                
                with torch.no_grad():
                    output = self.model(face_resized.to(self.device))
                    predictions.append(output.cpu().item())
            
            avg_prediction = np.mean(predictions)
            
            if avg_prediction >= 0.5:
                prediction = "Deepfake Detected"
                confidence = avg_prediction * 100
            else:
                prediction = "Real Video"
                confidence = (1.0 - avg_prediction) * 100
            
            return {
                "prediction": prediction,
                "confidence": confidence,
                "faces_processed": len(processed_faces),
                "model_used": "MesoNet",
                "raw_scores": predictions
            }
            
        except Exception as e:
            logger.error(f"MesoNet prediction failed: {e}")
            return {
                "prediction": "Error in Analysis",
                "confidence": 0.0,
                "faces_processed": 0,
                "model_used": "MesoNet",
                "error": str(e)
            }

# Initialize detector instance
# Don't create global instance - let the importing module handle instantiation
