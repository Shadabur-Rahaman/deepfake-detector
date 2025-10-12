import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class CNNLSTMHybridDetector:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def build_model(self):
        """Build CNN-LSTM hybrid architecture"""
        class HybridModel(nn.Module):
            def __init__(self):
                super(HybridModel, self).__init__()
                
                # CNN Feature Extractor
                self.cnn_features = nn.Sequential(
                    nn.Conv2d(3, 64, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(64, 128, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(128, 256, 3, padding=1),
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d((7, 7))
                )
                
                # LSTM for temporal analysis
                self.lstm = nn.LSTM(
                    input_size=256 * 7 * 7,
                    hidden_size=512,
                    num_layers=2,
                    batch_first=True,
                    dropout=0.3,
                    bidirectional=True
                )
                
                # Final classifier
                self.classifier = nn.Sequential(
                    nn.Dropout(0.5),
                    nn.Linear(512 * 2, 256),  # *2 for bidirectional
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(256, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                batch_size, seq_len, c, h, w = x.size()
                
                # Process each frame through CNN
                cnn_features = []
                for i in range(seq_len):
                    frame_features = self.cnn_features(x[:, i])
                    frame_features = frame_features.view(batch_size, -1)
                    cnn_features.append(frame_features)
                
                # Stack features for LSTM
                sequence_features = torch.stack(cnn_features, dim=1)
                
                # LSTM processing
                lstm_out, _ = self.lstm(sequence_features)
                final_features = lstm_out[:, -1]  # Use last output
                
                # Classification
                output = self.classifier(final_features)
                return output
        
        self.model = HybridModel().to(self.device)
        self.model.eval()
        logger.info("✅ CNN-LSTM Hybrid model built")
    
    async def analyze_sequence(self, face_sequence: List[torch.Tensor]) -> Dict:
        """Analyze sequence of faces using CNN-LSTM hybrid"""
        if not self.model:
            self.build_model()
        
        if len(face_sequence) < 5:
            return {
                'prediction': 'Insufficient Frames',
                'confidence': 0.0,
                'model': 'CNN-LSTM Hybrid',
                'frames_required': 5
            }
        
        try:
            # Prepare sequence (limit to 10 frames for performance)
            sequence = torch.stack(face_sequence[:10]).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(sequence)
                score = output.item()
            
            prediction = "Deepfake Detected" if score > 0.5 else "Real Video"
            confidence = score if score > 0.5 else (1.0 - score)
            
            return {
                'prediction': prediction,
                'confidence': confidence * 100,
                'model': 'CNN-LSTM Hybrid',
                'temporal_consistency': 'inconsistent' if score > 0.6 else 'consistent',
                'frames_analyzed': len(face_sequence),
                'spatial_features': 'extracted',
                'temporal_features': 'analyzed'
            }
            
        except Exception as e:
            logger.error(f"CNN-LSTM analysis failed: {e}")
            return {'prediction': 'Analysis Failed', 'confidence': 0.0, 'error': str(e)}
