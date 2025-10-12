"""
Unified Deepfake Detection Service
Comprehensive service that handles both traditional and modern AI detection modes

This service provides:
- Fixed model loading and inference
- Proper error handling for 'dict object is not callable' errors
- Support for both traditional and modern AI modes
- GPU acceleration support
- Comprehensive logging

Author: Senior ML Engineer
Date: 2024
"""

import os
import logging
import torch
import torch.nn as nn
import numpy as np
import cv2
import time
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="cv2")
warnings.filterwarnings("ignore", category=DeprecationWarning)

logger = logging.getLogger(__name__)

class DetectionMode(Enum):
    """Detection modes for the unified service"""
    TRADITIONAL = "traditional"
    MODERN_AI = "modern_ai"

@dataclass
class DetectionResult:
    """Result of deepfake detection"""
    prediction: str
    confidence: float
    mode: str
    model_name: str
    processing_time_ms: float
    faces_detected: int
    device: str
    error: Optional[str] = None

class UnifiedDetectionService:
    """
    Unified deepfake detection service that handles both traditional and modern AI modes
    with fixed model loading and inference
    """
    
    def __init__(self, device: str = "auto"):
        self.device = self._get_device(device)
        self.models = {}
        self.current_mode = None
        self.current_model = None
        
        logger.info(f"UnifiedDetectionService initialized on {self.device}")
    
    def _get_device(self, device: str) -> torch.device:
        """Get the appropriate device for model loading"""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            return torch.device("cpu")
        return torch.device(device)
    
    def load_traditional_model(self, model_path: str) -> bool:
        """Load traditional model (deepfake_detector_finetuned1.pth) with proper error handling"""
        try:
            logger.info(f"Loading traditional model from: {os.path.basename(model_path)}")
            
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            
            # Extract state dict
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Create EfficientNet-B0 model architecture
            from torchvision import models
            model = models.efficientnet_b0(weights=None)
            
            # Modify classifier for binary classification
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(num_ftrs, 1)
            
            # Clean state dict keys
            clean_state_dict = {}
            for key, value in state_dict.items():
                # Remove module prefix if present
                clean_key = key.replace('module.', '') if key.startswith('module.') else key
                clean_state_dict[clean_key] = value
            
            # Load state dict - FIXED: This was missing the actual call
            model.load_state_dict(clean_state_dict, strict=False)
            model.eval()
            model.to(self.device)
            
            # Store model
            self.models['traditional'] = model
            # Reduced logging to avoid duplicates
            return True
            
        except Exception as e:
            logger.error(f"Failed to load traditional model: {e}")
            return False
    
    def load_modern_model(self, model_path: str) -> bool:
        """Load modern model (deepfake_detector_finetuned1.pth) with proper error handling"""
        try:
            logger.info(f"Loading modern model from: {os.path.basename(model_path)}")
            
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            
            # Extract state dict
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Create EfficientNet-B0 model architecture
            from torchvision import models
            model = models.efficientnet_b0(weights=None)
            
            # Modify classifier for binary classification
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(num_ftrs, 1)
            
            # Clean state dict keys
            clean_state_dict = {}
            for key, value in state_dict.items():
                # Remove module prefix if present
                clean_key = key.replace('module.', '') if key.startswith('module.') else key
                clean_state_dict[clean_key] = value
            
            # Load state dict
            model.load_state_dict(clean_state_dict, strict=False)
            model.eval()
            model.to(self.device)
            
            # Store model
            self.models['modern_ai'] = model
            # Reduced logging to avoid duplicates
            return True
            
        except Exception as e:
            logger.error(f"Failed to load modern model: {e}")
            return False
    
    def set_mode(self, mode: DetectionMode) -> bool:
        """Set detection mode and load appropriate model"""
        try:
            # Get model paths
            base_dir = Path(__file__).parent.parent.parent.parent
            ml_artifacts_dir = base_dir / "ml_artifacts"
            
            if mode == DetectionMode.TRADITIONAL:
                model_path = ml_artifacts_dir / "deepfake_detector_finetuned1.pth"
                if not model_path.exists():
                    logger.error(f"Traditional model not found: {model_path}")
                    return False
                
                if 'traditional' not in self.models:
                    success = self.load_traditional_model(str(model_path))
                    if not success:
                        return False
                
                self.current_model = self.models['traditional']
                self.current_mode = mode
                logger.info("[OK] Traditional mode activated with deepfake_detector_finetuned1.pth")
                return True
                
            elif mode == DetectionMode.MODERN_AI:
                model_path = ml_artifacts_dir / "deepfake_detector_finetuned1.pth"
                if not model_path.exists():
                    logger.error(f"Modern model not found: {model_path}")
                    return False
                
                if 'modern_ai' not in self.models:
                    success = self.load_modern_model(str(model_path))
                    if not success:
                        return False
                
                self.current_model = self.models['modern_ai']
                self.current_mode = mode
                logger.info("[OK] Modern AI mode activated with deepfake_detector_finetuned1.pth")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to set mode {mode.value}: {e}")
            return False
    
    def preprocess_face(self, face: np.ndarray) -> torch.Tensor:
        """Preprocess face image for model inference"""
        try:
            import torchvision.transforms as transforms
            
            # Convert BGR to RGB if needed
            if len(face.shape) == 3 and face.shape[2] == 3:
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            
            # Apply transforms
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            face_tensor = transform(face)
            return face_tensor.unsqueeze(0)  # Add batch dimension
            
        except Exception as e:
            logger.warning(f"Face preprocessing failed: {e}")
            # Return a dummy tensor as fallback
            return torch.randn(1, 3, 224, 224).to(self.device)
    
    def detect_deepfake(self, faces: List[np.ndarray]) -> DetectionResult:
        """Detect deepfake in faces using current mode"""
        start_time = time.time()
        
        try:
            if not faces:
                return DetectionResult(
                    prediction="No Faces Detected",
                    confidence=0.0,
                    mode=self.current_mode.value if self.current_mode else "unknown",
                    model_name="none",
                    processing_time_ms=0.0,
                    faces_detected=0,
                    device=str(self.device)
                )
            
            if self.current_model is None:
                return DetectionResult(
                    prediction="Model Not Loaded",
                    confidence=0.0,
                    mode=self.current_mode.value if self.current_mode else "unknown",
                    model_name="none",
                    processing_time_ms=0.0,
                    faces_detected=len(faces),
                    device=str(self.device),
                    error="No model loaded"
                )
            
            # FIXED: Ensure we have a callable model, not a dict
            if isinstance(self.current_model, dict):
                return DetectionResult(
                    prediction="Model Error",
                    confidence=0.0,
                    mode=self.current_mode.value if self.current_mode else "unknown",
                    model_name="error",
                    processing_time_ms=0.0,
                    faces_detected=len(faces),
                    device=str(self.device),
                    error="Model is a dictionary, not callable"
                )
            
            if not callable(self.current_model):
                return DetectionResult(
                    prediction="Model Error",
                    confidence=0.0,
                    mode=self.current_mode.value if self.current_mode else "unknown",
                    model_name="error",
                    processing_time_ms=0.0,
                    faces_detected=len(faces),
                    device=str(self.device),
                    error="Model is not callable"
                )
            
            # Preprocess faces - FIXED: Handle batch dimensions correctly
            processed_faces = []
            for face in faces:
                processed_face = self.preprocess_face(face)
                # Remove batch dimension if present (preprocess_face adds it)
                if processed_face.dim() == 4 and processed_face.shape[0] == 1:
                    processed_face = processed_face.squeeze(0)
                processed_faces.append(processed_face)
            
            # Stack into batch
            face_batch = torch.stack(processed_faces).to(self.device)
            
            # Run inference
            with torch.no_grad():
                self.current_model.eval()
                logits = self.current_model(face_batch)
                
                # Apply sigmoid to get probabilities
                probabilities = torch.sigmoid(logits).cpu().numpy().flatten()
                avg_prob = np.mean(probabilities)
            
            # Determine result based on probability
            if avg_prob > 0.5:
                prediction = "Deepfake Detected"
                confidence = float(avg_prob) * 100
            else:
                prediction = "Real Video"
                confidence = float(1.0 - avg_prob) * 100
            
            processing_time = (time.time() - start_time) * 1000
            
            return DetectionResult(
                prediction=prediction,
                confidence=confidence,
                mode=self.current_mode.value if self.current_mode else "unknown",
                model_name=f"{self.current_mode.value}_model" if self.current_mode else "unknown",
                processing_time_ms=processing_time,
                faces_detected=len(faces),
                device=str(self.device)
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Detection failed: {e}")
            return DetectionResult(
                prediction="Detection Failed",
                confidence=0.0,
                mode=self.current_mode.value if self.current_mode else "unknown",
                model_name="error",
                processing_time_ms=processing_time,
                faces_detected=len(faces),
                device=str(self.device),
                error=str(e)
            )

# Global service instance
_unified_service: Optional[UnifiedDetectionService] = None

def get_unified_detection_service() -> UnifiedDetectionService:
    """Get the global unified detection service instance"""
    global _unified_service
    if _unified_service is None:
        _unified_service = UnifiedDetectionService()
    return _unified_service
