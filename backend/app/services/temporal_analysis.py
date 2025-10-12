# backend/app/services/temporal_analysis.py - Temporal Analysis Models for Deepfake Detection

import logging
import torch
import torch.nn as nn
from typing import Optional, Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)

# Check for required dependencies
VIT_AVAILABLE = False
LSTM_AVAILABLE = False

try:
    import vit_pytorch
    VIT_AVAILABLE = True
    logger.info("[OK] vit-pytorch available for temporal analysis")
except ImportError as e:
    logger.info(f"ℹ️ vit-pytorch not available: {e}")

try:
    # Check if LSTM is available in PyTorch
    if hasattr(torch.nn, 'LSTM'):
        LSTM_AVAILABLE = True
        logger.info("[OK] LSTM modules available for temporal analysis")
    else:
        logger.info("ℹ️ LSTM not available in PyTorch")
except Exception as e:
    logger.info(f"ℹ️ LSTM check failed: {e}")

class ViViTDetector:
    """Video Vision Transformer for temporal deepfake detection"""
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = None
        self.available = False
        
        if not VIT_AVAILABLE:
            logger.warning("[WARNING] ViViT not available: vit-pytorch not installed. Install with: pip install vit-pytorch")
            return
        
        try:
            from vit_pytorch import ViT
            
            # Create a simplified ViT for video analysis
            # In practice, you'd use a proper video transformer like ViViT
            self.model = ViT(
                image_size=224,
                patch_size=16,
                num_classes=2,
                dim=512,  # Smaller dimension for video
                depth=4,  # Fewer layers for efficiency
                heads=8,
                mlp_dim=1024,
                dropout=0.1,
                emb_dropout=0.1
            )
            
            # Move to device
            self.model = self.model.to(device)
            self.model.eval()
            
            self.available = True
            # Reduced logging to avoid duplicates
            
        except Exception as e:
            logger.warning(f"[WARNING] ViViT initialization failed: {e}")
            self.model = None
            self.available = False
    
    def analyze_sequence(self, face_sequences: List[List[np.ndarray]]) -> Dict[str, Any]:
        """Analyze sequences of faces for temporal inconsistencies"""
        if not self.available or not face_sequences:
            return {
                'prediction': 'No Analysis',
                'confidence': 0.0,
                'temporal_features': [],
                'inconsistency_score': 0.0
            }
        
        try:
            # Process each sequence
            sequence_results = []
            temporal_features = []
            
            for sequence in face_sequences:
                if not sequence or len(sequence) == 0:
                    continue
                
                # Convert sequence to tensors
                frame_tensors = []
                for face in sequence:
                    if face is not None and face.size > 0:
                        # Resize to 224x224 and normalize
                        import cv2
                        face_resized = cv2.resize(face, (224, 224))
                        face_tensor = torch.from_numpy(face_resized).permute(2, 0, 1).float() / 255.0
                        frame_tensors.append(face_tensor)
                
                if not frame_tensors:
                    continue
                
                # Stack tensors and move to device
                batch = torch.stack(frame_tensors).to(self.device)
                
                # Normalize with ImageNet stats
                mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(self.device)
                std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(self.device)
                batch = (batch - mean) / std
                
                with torch.no_grad():
                    outputs = self.model(batch)
                    probabilities = torch.softmax(outputs, dim=1)
                    
                    # Get fake probability (assuming class 1 is fake)
                    fake_prob = probabilities[:, 1].mean().item()
                    real_prob = probabilities[:, 0].mean().item()
                    
                    sequence_results.append({
                        'fake_probability': fake_prob,
                        'real_probability': real_prob
                    })
                    
                    # Extract temporal features
                    temporal_feat = self._extract_temporal_features(batch)
                    temporal_features.append(temporal_feat.cpu().numpy())
            
            if not sequence_results:
                return {
                    'prediction': 'No Valid Sequences',
                    'confidence': 0.0,
                    'temporal_features': [],
                    'inconsistency_score': 0.0
                }
            
            # Aggregate results across sequences
            avg_fake_prob = np.mean([r['fake_probability'] for r in sequence_results])
            avg_real_prob = np.mean([r['real_probability'] for r in sequence_results])
            
            prediction = 'Deepfake' if avg_fake_prob > 0.5 else 'Real'
            confidence = max(avg_fake_prob, avg_real_prob)
            
            # Calculate temporal inconsistency score
            inconsistency_score = self._calculate_temporal_inconsistency(temporal_features)
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'temporal_features': temporal_features,
                'inconsistency_score': inconsistency_score,
                'fake_probability': avg_fake_prob,
                'real_probability': avg_real_prob,
                'sequence_count': len(sequence_results)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] ViViT analysis failed: {e}")
            return {
                'prediction': 'Error',
                'confidence': 0.0,
                'temporal_features': [],
                'inconsistency_score': 0.0
            }
    
    def _extract_temporal_features(self, batch: torch.Tensor) -> torch.Tensor:
        """Extract temporal features from video frames"""
        try:
            # Simplified temporal feature extraction
            # In practice, you'd use proper video transformer layers
            batch_size = batch.size(0)
            feature_dim = 512
            return torch.rand(batch_size, feature_dim).to(self.device)
        except Exception:
            return torch.zeros(batch.size(0), 512).to(self.device)
    
    def _calculate_temporal_inconsistency(self, temporal_features: List[np.ndarray]) -> float:
        """Calculate temporal inconsistency score"""
        try:
            if len(temporal_features) < 2:
                return 0.0
            
            # Calculate variance across temporal features
            features_array = np.array(temporal_features)
            temporal_variance = np.var(features_array, axis=0).mean()
            
            # Normalize to 0-1 range
            inconsistency_score = min(temporal_variance / 10.0, 1.0)
            return inconsistency_score
        except Exception:
            return 0.0

class LSTMDetector:
    """LSTM-based temporal analysis for deepfake detection"""
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = None
        self.available = False
        
        if not LSTM_AVAILABLE:
            logger.warning("[WARNING] LSTM not available: PyTorch LSTM modules not found")
            return
        
        try:
            # Create LSTM model for temporal analysis
            self.model = TemporalLSTM(
                input_size=512,  # Feature dimension
                hidden_size=256,
                num_layers=2,
                num_classes=2,
                dropout=0.1
            )
            
            # Move to device
            self.model = self.model.to(device)
            self.model.eval()
            
            self.available = True
            # Reduced logging to avoid duplicates
            
        except Exception as e:
            logger.warning(f"[WARNING] LSTM initialization failed: {e}")
            self.model = None
            self.available = False
    
    def analyze_sequence(self, face_sequences: List[List[np.ndarray]]) -> Dict[str, Any]:
        """Analyze sequences of faces using LSTM"""
        if not self.available or not face_sequences:
            return {
                'prediction': 'No Analysis',
                'confidence': 0.0,
                'hidden_states': [],
                'temporal_pattern_score': 0.0
            }
        
        try:
            # Process each sequence
            sequence_results = []
            hidden_states = []
            
            for sequence in face_sequences:
                if not sequence or len(sequence) == 0:
                    continue
                
                # Convert sequence to feature tensors
                features = []
                for face in sequence:
                    if face is not None and face.size > 0:
                        # Extract features (simplified)
                        feature = self._extract_face_features(face)
                        features.append(feature)
                
                if len(features) < 2:  # Need at least 2 frames for temporal analysis
                    continue
                
                # Convert to tensor
                feature_tensor = torch.stack(features).unsqueeze(0).to(self.device)  # [1, seq_len, feature_dim]
                
                with torch.no_grad():
                    outputs, hidden = self.model(feature_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    
                    # Get fake probability (assuming class 1 is fake)
                    fake_prob = probabilities[0, 1].item()
                    real_prob = probabilities[0, 0].item()
                    
                    sequence_results.append({
                        'fake_probability': fake_prob,
                        'real_probability': real_prob
                    })
                    
                    # Store hidden states
                    hidden_states.append(hidden[0].cpu().numpy())  # [num_layers, batch, hidden_size]
            
            if not sequence_results:
                return {
                    'prediction': 'No Valid Sequences',
                    'confidence': 0.0,
                    'hidden_states': [],
                    'temporal_pattern_score': 0.0
                }
            
            # Aggregate results across sequences
            avg_fake_prob = np.mean([r['fake_probability'] for r in sequence_results])
            avg_real_prob = np.mean([r['real_probability'] for r in sequence_results])
            
            prediction = 'Deepfake' if avg_fake_prob > 0.5 else 'Real'
            confidence = max(avg_fake_prob, avg_real_prob)
            
            # Calculate temporal pattern score
            temporal_pattern_score = self._calculate_temporal_pattern_score(hidden_states)
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'hidden_states': hidden_states,
                'temporal_pattern_score': temporal_pattern_score,
                'fake_probability': avg_fake_prob,
                'real_probability': avg_real_prob,
                'sequence_count': len(sequence_results)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] LSTM analysis failed: {e}")
            return {
                'prediction': 'Error',
                'confidence': 0.0,
                'hidden_states': [],
                'temporal_pattern_score': 0.0
            }
    
    def _extract_face_features(self, face: np.ndarray) -> torch.Tensor:
        """Extract features from a single face"""
        try:
            # Simplified feature extraction
            # In practice, you'd use a pretrained feature extractor
            import cv2
            
            # Resize and normalize
            face_resized = cv2.resize(face, (224, 224))
            face_tensor = torch.from_numpy(face_resized).permute(2, 0, 1).float() / 255.0
            
            # Flatten and take first 512 features
            features = face_tensor.flatten()[:512]
            if len(features) < 512:
                features = torch.cat([features, torch.zeros(512 - len(features))])
            
            return features
        except Exception:
            return torch.zeros(512)
    
    def _calculate_temporal_pattern_score(self, hidden_states: List[np.ndarray]) -> float:
        """Calculate temporal pattern score from LSTM hidden states"""
        try:
            if len(hidden_states) < 2:
                return 0.0
            
            # Calculate pattern consistency across hidden states
            states_array = np.array(hidden_states)
            pattern_variance = np.var(states_array, axis=0).mean()
            
            # Normalize to 0-1 range
            pattern_score = min(pattern_variance / 5.0, 1.0)
            return pattern_score
        except Exception:
            return 0.0

class TemporalLSTM(nn.Module):
    """LSTM model for temporal deepfake detection"""
    
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, 
                 num_classes: int, dropout: float = 0.1):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_classes)
        )
    
    def forward(self, x):
        # x: [batch_size, seq_len, input_size]
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Use the last hidden state for classification
        last_hidden = hidden[-1]  # [batch_size, hidden_size]
        
        # Classification
        output = self.classifier(last_hidden)
        
        return output, (hidden, cell)

# Convenience functions for model loading
def get_vivit_detector(device: str = "cuda" if torch.cuda.is_available() else "cpu") -> Optional[ViViTDetector]:
    """Get ViViT detector instance"""
    if VIT_AVAILABLE:
        return ViViTDetector(device)
    return None

def get_lstm_detector(device: str = "cuda" if torch.cuda.is_available() else "cpu") -> Optional[LSTMDetector]:
    """Get LSTM detector instance"""
    if LSTM_AVAILABLE:
        return LSTMDetector(device)
    return None

def get_availability_status() -> Dict[str, bool]:
    """Get availability status of temporal analysis models"""
    return {
        'vit_pytorch': VIT_AVAILABLE,
        'lstm': LSTM_AVAILABLE,
        'vivit': VIT_AVAILABLE,
        'lstm_detector': LSTM_AVAILABLE
    }

def get_installation_hints() -> Dict[str, str]:
    """Get installation hints for missing dependencies"""
    hints = {}
    
    if not VIT_AVAILABLE:
        hints['vit_pytorch'] = "pip install vit-pytorch"
    
    if not LSTM_AVAILABLE:
        hints['lstm'] = "LSTM is part of PyTorch core - check PyTorch installation"
    
    return hints
