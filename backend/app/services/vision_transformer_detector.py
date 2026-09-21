"""
Vision Transformer Detector
===========================

Deepfake detection using Vision Transformer (ViT) models.
Implements pre-trained ViT models for face analysis and deepfake detection.

Author: Deepfake Detection System
Version: 1.0.0
"""

import logging
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from typing import List, Dict, Any, Optional
from PIL import Image
from .face_data_validator import FaceDataValidator

logger = logging.getLogger(__name__)

class VisionTransformerDetector:
    """
    Vision Transformer-based deepfake detector
    """
    
    def __init__(self, model_name: str = "vit_base_patch16_224"):
        self.model_name = model_name
        self.face_validator = FaceDataValidator()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.is_initialized = False
        self.model = None
        self.transform = None
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Vision Transformer model"""
        try:
            # Try to import timm for Vision Transformer models
            import timm
            
            # Load pre-trained ViT model
            self.model = timm.create_model(
                self.model_name,
                pretrained=True,
                num_classes=1000  # ImageNet classes
            )
            
            # Replace classifier for binary deepfake detection
            num_features = self.model.head.in_features
            self.model.head = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(512, 1),
                nn.Sigmoid()
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            # Initialize transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            self.is_initialized = True
            logger.info(f"✅ Vision Transformer ({self.model_name}) initialized successfully")
            
        except ImportError:
            logger.warning("⚠️ timm not available, using torchvision ViT fallback")
            self._initialize_torchvision_fallback()
        except Exception as e:
            logger.warning(f"⚠️ ViT initialization failed: {e}, using torchvision fallback")
            self._initialize_torchvision_fallback()
    
    def _initialize_torchvision_fallback(self):
        """Initialize torchvision ViT as fallback"""
        try:
            from torchvision.models import vit_b_16
            
            # Load pre-trained ViT from torchvision
            self.model = vit_b_16(weights='IMAGENET1K_V1')
            
            # Replace classifier for binary classification
            num_features = self.model.heads.head.in_features
            self.model.heads.head = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(512, 1),
                nn.Sigmoid()
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            # Initialize transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            self.is_initialized = True
            logger.info("✅ Vision Transformer (torchvision ViT-B/16) initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ ViT fallback initialization failed: {e}")
            self.is_initialized = False
    
    def detect_deepfake(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """
        Detect deepfakes using Vision Transformer
        
        Args:
            faces: List of face images as numpy arrays
            
        Returns:
            Dictionary with detection results
        """
        if not self.is_initialized:
            logger.warning("⚠️ Vision Transformer not initialized")
            return self._get_default_result(len(faces))
        
        # Validate all faces first
        validated_faces = self.face_validator.validate_face_list(faces, "vit_detector")
        
        if not validated_faces:
            logger.warning("⚠️ No valid faces provided to ViT detector")
            return self._get_default_result(len(faces))
        
        try:
            predictions = []
            confidences = []
            
            with torch.no_grad():
                for face in validated_faces:
                    # Convert numpy array to PIL Image
                    if len(face.shape) == 3:
                        # BGR to RGB conversion
                        face_rgb = face[:, :, ::-1]
                        pil_image = Image.fromarray(face_rgb)
                    else:
                        pil_image = Image.fromarray(face)
                    
                    # Apply transforms
                    input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
                    
                    # Run inference
                    output = self.model(input_tensor)
                    confidence = output.item()
                    
                    # Convert to prediction
                    prediction = 'deepfake' if confidence > 0.5 else 'real'
                    
                    predictions.append(prediction)
                    confidences.append(confidence)
            
            # Aggregate results
            avg_confidence = np.mean(confidences)
            deepfake_count = sum(1 for p in predictions if p == 'deepfake')
            real_count = len(predictions) - deepfake_count
            
            # Final prediction based on majority vote
            if deepfake_count > real_count:
                final_prediction = 'deepfake'
                final_confidence = deepfake_count / len(predictions)
            elif real_count > deepfake_count:
                final_prediction = 'real'
                final_confidence = real_count / len(predictions)
            else:
                final_prediction = 'uncertain'
                final_confidence = 0.5
            
            return {
                'model': f'ViT_{self.model_name}',
                'prediction': final_prediction,
                'confidence': final_confidence,
                'avg_confidence': avg_confidence,
                'face_count': len(validated_faces),
                'deepfake_faces': deepfake_count,
                'real_faces': real_count,
                'individual_predictions': predictions,
                'individual_confidences': confidences,
                'model_confidence': avg_confidence
            }
            
        except Exception as e:
            logger.error(f"❌ ViT detection failed: {e}")
            return self._get_default_result(len(validated_faces))
    
    def _get_default_result(self, face_count: int) -> Dict[str, Any]:
        """Return default result when detection fails"""
        return {
            'model': f'ViT_{self.model_name}',
            'prediction': 'uncertain',
            'confidence': 0.5,
            'avg_confidence': 0.5,
            'face_count': face_count,
            'deepfake_faces': 0,
            'real_faces': 0,
            'individual_predictions': ['uncertain'] * face_count,
            'individual_confidences': [0.5] * face_count,
            'model_confidence': 0.5
        }
    
    def get_attention_maps(self, face: np.ndarray) -> Optional[np.ndarray]:
        """
        Get attention maps from ViT for interpretability
        
        Args:
            face: Single face image as numpy array
            
        Returns:
            Attention map as numpy array or None if failed
        """
        if not self.is_initialized:
            return None
        
        try:
            # This is a simplified attention extraction
            # In practice, you'd need to hook into the attention layers
            logger.info("📊 Attention map extraction not fully implemented")
            return None
            
        except Exception as e:
            logger.error(f"❌ Attention map extraction failed: {e}")
            return None
    
    def analyze_face_features(self, face: np.ndarray) -> Dict[str, Any]:
        """
        Analyze specific face features using ViT embeddings
        
        Args:
            face: Single face image as numpy array
            
        Returns:
            Feature analysis results
        """
        if not self.is_initialized:
            return {'error': 'Model not initialized'}
        
        try:
            # Convert to PIL and apply transforms
            if len(face.shape) == 3:
                face_rgb = face[:, :, ::-1]
                pil_image = Image.fromarray(face_rgb)
            else:
                pil_image = Image.fromarray(face)
            
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # Extract features from the last layer before classification
            with torch.no_grad():
                # Get features from the model (before final classification layer)
                features = self.model.forward_features(input_tensor)
                
                # Convert to numpy and analyze
                features_np = features.cpu().numpy().flatten()
                
                # Calculate feature statistics
                feature_stats = {
                    'mean': float(np.mean(features_np)),
                    'std': float(np.std(features_np)),
                    'max': float(np.max(features_np)),
                    'min': float(np.min(features_np)),
                    'feature_dim': len(features_np)
                }
                
                return {
                    'model': f'ViT_{self.model_name}',
                    'feature_stats': feature_stats,
                    'feature_vector': features_np.tolist()[:100]  # First 100 features
                }
                
        except Exception as e:
            logger.error(f"❌ Feature analysis failed: {e}")
            return {'error': str(e)}
    
    def analyze_faces(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """
        Analyze faces for deepfake detection - wrapper method for compatibility
        
        Args:
            faces: List of face images as numpy arrays
            
        Returns:
            Dictionary with detection results in expected format
        """
        try:
            # Call the main detection method
            result = self.detect_deepfake(faces)
            
            # Return the result dictionary directly
            return result
            
        except Exception as e:
            logger.error(f"❌ ViT analyze_faces failed: {e}")
            # Return default result in expected format
            class DefaultResult:
                def __init__(self):
                    self.prediction = 'uncertain'
                    self.confidence = 0.5
            
            return DefaultResult()
    
    def load_fine_tuned_weights(self, weights_path: str) -> bool:
        """
        Load fine-tuned weights for deepfake detection
        
        Args:
            weights_path: Path to the weights file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_initialized:
                logger.error("❌ Model not initialized, cannot load weights")
                return False
            
            # Load state dict
            state_dict = torch.load(weights_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            
            logger.info(f"✅ Loaded fine-tuned ViT weights from {weights_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load ViT weights: {e}")
            return False