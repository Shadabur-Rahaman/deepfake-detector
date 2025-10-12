import torch
import torch.nn as nn
import logging
import time
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)

# Clean transformers import - no fallback messages unless actually needed
TRANSFORMERS_AVAILABLE = False
ViTModel = None
ViTConfig = None

try:
    from transformers import ViTModel, ViTConfig
    TRANSFORMERS_AVAILABLE = True
    logger.info("✅ Transformers imported successfully for ViT")
except Exception:
    # Silent fallback - no info messages about missing transformers
    pass

class ViTDetector:
    """
    Vision Transformer for global context analysis and patch-based deepfake detection
    """
    
    def __init__(self):
        if not TRANSFORMERS_AVAILABLE:
            self.available = False
            return
            
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.patch_size = 16
        self.image_size = 224
        self.available = True
        
    async def load_model(self):
        """Load pre-trained Vision Transformer model"""
        if not self.available:
            return
            
        try:
            # Load ViT configuration
            config = ViTConfig(
                image_size=self.image_size,
                patch_size=self.patch_size,
                num_channels=3,
                hidden_size=768,
                num_hidden_layers=12,
                num_attention_heads=12,
                intermediate_size=3072
            )
            
            # Load pre-trained ViT model
            self.model = ViTModel.from_pretrained('google/vit-base-patch16-224', config=config)
            
            # Add classification head for deepfake detection
            self.classifier = nn.Sequential(
                nn.Linear(768, 256),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(256, 2)  # Real vs Fake
            )
            
            self.model.to(self.device)
            self.classifier.to(self.device)
            self.model.eval()
            
            logger.info("✅ Vision Transformer detector loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading ViT model: {str(e)}")
            raise
    
    async def analyze_global_context(self, face_crops: List[np.ndarray]) -> Dict:
        """
        Analyze global patterns and contextual inconsistencies using self-attention
        """
        if not self.available or self.model is None:
            return {
                'confidence': 0.5,
                'attention_maps': [],
                'global_features': np.array([]),
                'processing_time': 0.0,
                'error': 'ViT detector not available'
            }
            
        start_time = time.time()
        
        try:
            if not face_crops:
                return {
                    'confidence': 0.5,
                    'attention_maps': [],
                    'global_features': np.array([]),
                    'processing_time': time.time() - start_time
                }
            
            global_features = []
            attention_maps = []
            confidence_scores = []
            
            for face_crop in face_crops:
                if len(face_crop.shape) == 3:
                    # Preprocess image
                    face_tensor = self.preprocess_image(face_crop)
                    
                    with torch.no_grad():
                        # Get ViT outputs with attention
                        outputs = self.model(face_tensor, output_attentions=True)
                        
                        # Extract global features from [CLS] token
                        cls_features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                        global_features.append(cls_features)
                        
                        # Extract attention maps for interpretability
                        attention = outputs.attentions[-1].mean(dim=1).cpu().numpy()  # Average over heads
                        attention_maps.append(attention)
                        
                        # Get classification confidence
                        classification_output = self.classifier(outputs.last_hidden_state[:, 0, :])
                        probabilities = torch.softmax(classification_output, dim=1)
                        fake_prob = probabilities[0, 1].item()
                        confidence_scores.append(fake_prob)
            
            # Calculate overall metrics
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
            all_features = np.vstack(global_features) if global_features else np.array([])
            
            result = {
                'confidence': float(avg_confidence),
                'global_features': all_features,
                'attention_maps': attention_maps,
                'patch_analysis': self.analyze_patch_inconsistencies(attention_maps),
                'context_awareness_score': self.calculate_context_score(all_features),
                'faces_analyzed': len(face_crops),
                'processing_time': time.time() - start_time
            }
            
            return result
            
        except Exception as e:
            logger.error(f"ViT global context analysis error: {str(e)}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for ViT input"""
        # Resize to 224x224
        image_resized = cv2.resize(image, (self.image_size, self.image_size))
        
        # Convert to tensor and normalize
        image_tensor = torch.from_numpy(image_resized).float().permute(2, 0, 1) / 255.0
        
        # Normalize with ImageNet statistics
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        image_tensor = normalize(image_tensor).unsqueeze(0).to(self.device)
        
        return image_tensor
    
    def analyze_patch_inconsistencies(self, attention_maps: List[np.ndarray]) -> Dict:
        """Analyze patch-level inconsistencies using attention patterns"""
        if not attention_maps:
            return {'inconsistency_score': 0.0, 'suspicious_patches': []}
        
        # Analyze attention distribution for anomalies
        patch_scores = []
        for attention_map in attention_maps:
            # Calculate patch-level attention variance
            patch_variance = np.var(attention_map, axis=1)
            patch_scores.append(patch_variance)
        
        avg_inconsistency = np.mean(patch_scores) if patch_scores else 0.0
        
        return {
            'inconsistency_score': float(avg_inconsistency),
            'suspicious_patches': self.identify_suspicious_patches(attention_maps),
            'attention_entropy': self.calculate_attention_entropy(attention_maps)
        }
    
    def calculate_context_score(self, features: np.ndarray) -> float:
        """Calculate contextual consistency score"""
        if len(features) < 2:
            return 1.0
        
        # Calculate feature similarity for context awareness
        feature_similarities = []
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                similarity = np.corrcoef(features[i], features[j])[0, 1]
                if not np.isnan(similarity):
                    feature_similarities.append(abs(similarity))
        
        return float(np.mean(feature_similarities)) if feature_similarities else 1.0
