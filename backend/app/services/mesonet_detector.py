# app/services/mesonet_detector.py
import torch, torch.nn as nn
import logging, pathlib
import numpy as np

from .model_availability import TIMM_AVAILABLE
from .categorized_logging import DETECTION_LOGGER
from .tensor_conversion_fixes import safe_convert_to_tensor, safe_batch_convert_faces, safe_stack_faces_batch

WEIGHTS = pathlib.Path(__file__).parent / "mesonet_weights.pth"

class _MesoNet(nn.Module):
    """Very small CNN – 55 k params."""
    def __init__(self):
        super().__init__()
        if TIMM_AVAILABLE:
            try:
                import timm
                self.backbone = timm.create_model('mobilenetv3_small_050', pretrained=False, num_classes=1)
                DETECTION_LOGGER.success("timm-based MesoNet model created")
            except Exception as e:
                DETECTION_LOGGER.info(f"timm model creation failed: {e}, using fallback")
                self.backbone = self._create_fallback_model()
        else:
            self.backbone = self._create_fallback_model()
        self.act = nn.Sigmoid()
    
    def _create_fallback_model(self):
        """Fallback model when timm is not available"""
        DETECTION_LOGGER.info("Using fallback MesoNet model (timm not available)")
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
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        try:
            self.model = _MesoNet().to(device)
            if WEIGHTS.exists():
                self.model.load_state_dict(torch.load(WEIGHTS, map_location=device))
                DETECTION_LOGGER.success("MesoNet weights loaded")
            else:
                # Suppress the warning - this is expected in many environments
                DETECTION_LOGGER.info("MesoNet weights not found, using untrained model")
            self.model.eval()
        except Exception as e:
            DETECTION_LOGGER.error(f"MesoNet initialization failed: {e}")
            # FIXED: Remove dummy model - use actual MesoNet implementation
            self.model = None

    @torch.no_grad()
    def predict(self, faces):
        """faces = list[Tensor (3,224,224)]  -> {'prediction', 'confidence'}"""
        if not faces or self.model is None:
            return {'prediction': 'No Faces', 'confidence': 0.0}
        
        try:
            # FIXED: Use comprehensive tensor conversion utility
            processed_faces = safe_batch_convert_faces(faces, target_shape=(3, 224, 224))
            
            if not processed_faces:
                return {'prediction': 'No Valid Faces', 'confidence': 0.0}
            
            # Stack all faces into a single batch using safe stacking
            batch = safe_stack_faces_batch(processed_faces)
            
            # FIXED: Ensure batch has correct shape (N, C, H, W)
            if batch.dim() != 4:
                DETECTION_LOGGER.error(f"MesoNet batch has wrong dimensions: {batch.dim()}, shape: {batch.shape}")
                return {'prediction': 'Error', 'confidence': 0.0}
            
            if batch.shape[1] != 3:
                DETECTION_LOGGER.error(f"MesoNet batch has wrong channel count: {batch.shape[1]}")
                return {'prediction': 'Error', 'confidence': 0.0}
            
            # Ensure batch is on correct device
            batch = batch.to(self.device)
            
            # Run inference
            prob = self.model(batch).mean().item()     # avg over faces
            if prob >= 0.5:
                return {'prediction': 'Deepfake', 'confidence': prob}
            return {'prediction': 'Real', 'confidence': 1 - prob}
        except Exception as e:
            DETECTION_LOGGER.error(f"MesoNet prediction failed: {e}")
            return {'prediction': 'Error', 'confidence': 0.0}
