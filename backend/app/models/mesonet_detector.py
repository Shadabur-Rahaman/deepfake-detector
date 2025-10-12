# app/models/mesonet_detector.py - FINAL STABLE VERSION
# app/models/mesonet_detector.py - FINAL STABLE VERSION
import torch
import torch.nn as nn
import logging
import pathlib
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__) # ADDED LOGGER
WEIGHTS_PATH = pathlib.Path(__file__).parent / "mesonet_weights.pth"

# Try to import timm with fallback for Python 3.13 compatibility
TIMM_AVAILABLE = False
try:
    import timm
    TIMM_AVAILABLE = True
    logger.info("[OK] timm imported successfully")
except ImportError as e:
    logger.info(f"ℹ️ timm not available: {e}, using fallback implementation")
    TIMM_AVAILABLE = False
except Exception as e:
    logger.info(f"ℹ️ timm import warning: {e}, using fallback implementation")
    TIMM_AVAILABLE = False

class _MesoNet(nn.Module):
    def __init__(self):
        super().__init__()
        if TIMM_AVAILABLE:
            try:
                self.backbone = timm.create_model('mobilenetv3_small_050', pretrained=False, num_classes=1)
                logger.info("[OK] timm-based MesoNet model created successfully")
            except Exception as e:
                logger.info(f"ℹ️ timm model creation failed: {e}, using fallback")
                TIMM_AVAILABLE = False
                self.backbone = self._create_fallback_model()
        else:
            self.backbone = self._create_fallback_model()
        self.act = nn.Sigmoid()
    
    def _create_fallback_model(self):
        """Fallback model when timm is not available"""
        logger.info("ℹ️ Using fallback MesoNet model (timm not available)")
        return nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(128, 1)
        )
        
    def forward(self, x): 
        return self.act(self.backbone(x)).squeeze(1)

class MesoNetDetector:
    def __init__(self, device: str = "auto"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.model = _MesoNet().to(self.device)
            if WEIGHTS_PATH.exists():
                logger.info(f"Loading MesoNet weights from: {WEIGHTS_PATH}")
                self.model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=self.device))
            else:
                logger.info(f"ℹ️ MesoNet weight file not found at {WEIGHTS_PATH}. Using fallback model.")
            self.model.eval()
            # Reduced logging to avoid duplicates
        except Exception as e:
            logger.error(f"[ERROR] MesoNet initialization failed: {e}")
            self.model = None

    @torch.no_grad()
    async def predict(self, faces: List[torch.Tensor]) -> Dict:
        if not faces or self.model is None: 
            return {'prediction': 'No Faces', 'confidence': 0.0}
        
        try:
            probabilities = []
            for face_tensor in faces:
                if not isinstance(face_tensor, torch.Tensor) or face_tensor.dim() != 3: 
                    continue
                if face_tensor.shape[0] == 1: 
                    face_tensor = face_tensor.repeat(3, 1, 1)
                batch = face_tensor.unsqueeze(0).to(self.device)
                probabilities.append(self.model(batch).item())
            
            if not probabilities: 
                return {'prediction': 'Analysis Failed', 'confidence': 0.0}
            
            avg_prob = float(np.mean(probabilities))
            # This model outputs ~1.0 for DEEPFAKE
            is_fake = avg_prob >= 0.5
            prediction = "Deepfake Detected" if is_fake else "Real Video"
            confidence = avg_prob if is_fake else 1.0 - avg_prob
            return {'prediction': prediction, 'confidence': confidence * 100}
        except Exception as e:
            logger.error(f"[ERROR] MesoNet prediction failed: {e}")
            return {'prediction': 'Error', 'confidence': 0.0}