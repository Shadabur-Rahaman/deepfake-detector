import torch
import torch.nn as nn
import numpy as np
import time
import logging
import cv2
from typing import List, Dict

logger = logging.getLogger(__name__)

# Try to import transformers, fallback to None if not available
try:
    from transformers import VivitModel, VivitConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    VivitModel = None
    VivitConfig = None
    logger.warning("Transformers library not available, ViViT detector will use fallback mode")

class ViViTDetector:
    """
    Video Vision Transformer for temporal consistency analysis
    3D attention mechanism for video sequence processing
    """
    
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_frames = 16
        self.image_size = 224
        
    async def load_model(self):
        """Load ViViT model for video analysis"""
        try:
            if TRANSFORMERS_AVAILABLE and VivitModel is not None:
                # Configure ViViT for deepfake detection
                config = VivitConfig(
                    image_size=self.image_size,
                    num_frames=self.num_frames,
                    tubelet_size=[2, 16, 16],
                    num_channels=3,
                    hidden_size=768,
                    num_hidden_layers=12,
                    num_attention_heads=12
                )
                
                self.model = VivitModel.from_pretrained('google/vivit-b-16x2-kinetics400', config=config)
                
                # Add classification head
                self.classifier = nn.Sequential(
                    nn.Linear(768, 256),
                    nn.ReLU(),
                    nn.Dropout(0.4),
                    nn.Linear(256, 2)  # Real vs Fake
                )
                
                self.model.to(self.device)
                self.classifier.to(self.device)
                self.model.eval()
                
                logger.info("ViViT video detector loaded successfully")
            else:
                # Use simple fallback model
                logger.warning("Transformers not available, using fallback ViViT model")
                self.model = None
                self.classifier = None
            
        except Exception as e:
            logger.error(f"Error loading ViViT model: {str(e)}")
            # Don't raise, just use fallback
            self.model = None
            self.classifier = None
    
    async def analyze_temporal_consistency(self, frame_sequence: List[np.ndarray], face_sequences: List[List[np.ndarray]]) -> Dict:
        """
        Analyze temporal consistency using 3D attention mechanism
        """
        start_time = time.time()
        
        try:
            if len(frame_sequence) < self.num_frames:
                # Pad or repeat frames if sequence is too short
                frame_sequence = self.pad_frame_sequence(frame_sequence)
            
            # Prepare video tensor
            video_tensor = self.prepare_video_tensor(frame_sequence[:self.num_frames])
            
            with torch.no_grad():
                # Get ViViT outputs with 3D attention
                outputs = self.model(video_tensor, output_attentions=True)
                
                # Extract temporal features
                temporal_features = outputs.last_hidden_state[:, 0, :].cpu().numpy()  # [CLS] token
                
                # Get classification confidence
                classification_output = self.classifier(outputs.last_hidden_state[:, 0, :])
                probabilities = torch.softmax(classification_output, dim=1)
                fake_confidence = probabilities[0, 1].item()
                
                # Analyze 3D attention patterns
                attention_analysis = self.analyze_3d_attention(outputs.attentions)
                
                # Calculate temporal metrics
                motion_consistency = self.calculate_motion_consistency(frame_sequence)
                frame_coherence = self.calculate_frame_coherence(face_sequences)
            
            result = {
                'confidence': float(fake_confidence),
                'temporal_features': temporal_features,
                'motion_consistency_score': motion_consistency,
                'frame_coherence_score': frame_coherence,
                'attention_analysis': attention_analysis,
                'frames_analyzed': len(frame_sequence),
                'processing_time': time.time() - start_time,
                '3d_attention_entropy': attention_analysis['entropy'],
                'temporal_artifact_score': self.detect_temporal_artifacts(outputs.attentions)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"ViViT temporal analysis error: {str(e)}")
            raise
    
    def prepare_video_tensor(self, frames: List[np.ndarray]) -> torch.Tensor:
        """Prepare video tensor for ViViT input"""
        video_frames = []
        
        for frame in frames:
            # Resize frame
            frame_resized = cv2.resize(frame, (self.image_size, self.image_size))
            # Normalize
            frame_normalized = frame_resized.astype(np.float32) / 255.0
            video_frames.append(frame_normalized)
        
        # Stack frames: [T, H, W, C] -> [C, T, H, W]
        video_array = np.stack(video_frames, axis=0)
        video_tensor = torch.from_numpy(video_array).permute(3, 0, 1, 2).unsqueeze(0).to(self.device)
        
        return video_tensor
    
    def analyze_3d_attention(self, attentions: tuple) -> Dict:
        """Analyze 3D attention patterns for temporal inconsistencies"""
        if not attentions:
            return {'entropy': 0.0, 'temporal_focus': 0.0, 'spatial_focus': 0.0}
        
        # Use the last layer attention
        last_attention = attentions[-1].cpu().numpy()  # [batch, heads, seq_len, seq_len]
        
        # Calculate attention entropy
        attention_entropy = []
        for head in range(last_attention.shape[1]):
            entropy = -np.sum(last_attention[0, head] * np.log(last_attention[0, head] + 1e-8))
            attention_entropy.append(entropy)
        
        avg_entropy = np.mean(attention_entropy)
        
        # Analyze temporal vs spatial focus
        temporal_focus = self.calculate_temporal_attention_focus(last_attention)
        spatial_focus = self.calculate_spatial_attention_focus(last_attention)
        
        return {
            'entropy': float(avg_entropy),
            'temporal_focus': temporal_focus,
            'spatial_focus': spatial_focus,
            'attention_distribution': self.analyze_attention_distribution(last_attention)
        }
    
    def calculate_motion_consistency(self, frames: List[np.ndarray]) -> float:
        """Calculate optical flow-based motion consistency"""
        if len(frames) < 2:
            return 1.0
        
        flow_consistencies = []
        
        for i in range(len(frames) - 1):
            gray1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)
            
            # Calculate flow magnitude consistency
            if flow[0] is not None:
                flow_magnitude = np.sqrt(flow[0][:, :, 0]**2 + flow[0][:, :, 1]**2)
                consistency = 1.0 / (1.0 + np.std(flow_magnitude))
                flow_consistencies.append(consistency)
        
        return float(np.mean(flow_consistencies)) if flow_consistencies else 1.0
    
    def pad_frame_sequence(self, frame_sequence: List[np.ndarray]) -> List[np.ndarray]:
        """Pad frame sequence to required length"""
        if len(frame_sequence) >= self.num_frames:
            return frame_sequence[:self.num_frames]
        
        # Pad by repeating the last frame
        last_frame = frame_sequence[-1] if frame_sequence else np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
        while len(frame_sequence) < self.num_frames:
            frame_sequence.append(last_frame)
        
        return frame_sequence
    
    def calculate_frame_coherence(self, face_sequences: List[List[np.ndarray]]) -> float:
        """Calculate frame coherence score"""
        try:
            if not face_sequences or not face_sequences[0]:
                return 0.5
            
            # Simple coherence calculation based on face count consistency
            face_counts = [len(seq) for seq in face_sequences if seq]
            if not face_counts:
                return 0.5
            
            # Calculate variance in face counts
            variance = np.var(face_counts)
            coherence = 1.0 / (1.0 + variance)
            return min(max(coherence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Frame coherence calculation error: {e}")
            return 0.5
    
    def detect_temporal_artifacts(self, attentions) -> float:
        """Detect temporal artifacts in attention patterns"""
        try:
            if not attentions:
                return 0.0
            
            # Simple artifact detection based on attention variance
            last_attention = attentions[-1].cpu().numpy()
            variance = np.var(last_attention)
            artifact_score = min(variance * 10, 1.0)  # Scale to 0-1
            return float(artifact_score)
        except Exception as e:
            logger.error(f"Temporal artifact detection error: {e}")
            return 0.0
    
    def calculate_temporal_attention_focus(self, attention: np.ndarray) -> float:
        """Calculate temporal attention focus"""
        try:
            # Simplified calculation
            temporal_variance = np.var(attention, axis=-1).mean()
            focus = 1.0 / (1.0 + temporal_variance)
            return float(focus)
        except Exception as e:
            logger.error(f"Temporal attention focus calculation error: {e}")
            return 0.5
    
    def calculate_spatial_attention_focus(self, attention: np.ndarray) -> float:
        """Calculate spatial attention focus"""
        try:
            # Simplified calculation
            spatial_variance = np.var(attention, axis=-2).mean()
            focus = 1.0 / (1.0 + spatial_variance)
            return float(focus)
        except Exception as e:
            logger.error(f"Spatial attention focus calculation error: {e}")
            return 0.5
    
    def analyze_attention_distribution(self, attention: np.ndarray) -> Dict:
        """Analyze attention distribution patterns"""
        try:
            return {
                'mean': float(np.mean(attention)),
                'std': float(np.std(attention)),
                'max': float(np.max(attention)),
                'min': float(np.min(attention))
            }
        except Exception as e:
            logger.error(f"Attention distribution analysis error: {e}")
            return {'mean': 0.0, 'std': 0.0, 'max': 0.0, 'min': 0.0}
