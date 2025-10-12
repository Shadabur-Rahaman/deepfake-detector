import torch
import torch.nn as nn
import numpy as np
import time
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class LSTMDetector:
    """
    LSTM-based temporal sequence analysis for deepfake detection
    Captures long-term dependencies and temporal patterns
    """
    
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.hidden_size = 256
        self.num_layers = 2
        self.sequence_length = 30
        
    async def load_model(self):
        """Load LSTM model for temporal analysis"""
        try:
            self.model = TemporalLSTMModel(
                input_size=512,  # Feature vector size from previous stages
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                num_classes=2
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("LSTM temporal detector loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LSTM model: {str(e)}")
            raise
    
    async def analyze_sequence_patterns(self, feature_sequences: List[np.ndarray]) -> Dict:
        """
        Analyze temporal patterns using LSTM networks
        """
        start_time = time.time()
        
        try:
            if not feature_sequences or len(feature_sequences) < 2:
                return {
                    'confidence': 0.5,
                    'sequence_consistency': 0.5,
                    'temporal_dependencies': [],
                    'processing_time': time.time() - start_time
                }
            
            # Prepare sequence tensor
            sequence_tensor = self.prepare_sequence_tensor(feature_sequences)
            
            with torch.no_grad():
                # Get LSTM outputs
                outputs, (hidden, cell) = self.model.lstm(sequence_tensor)
                
                # Get final classification
                classification_output = self.model.classifier(outputs[:, -1, :])
                probabilities = torch.softmax(classification_output, dim=1)
                fake_confidence = probabilities[0, 1].item()
                
                # Analyze sequence patterns
                sequence_analysis = self.analyze_lstm_patterns(outputs, hidden, cell)
                
                # Calculate temporal consistency metrics
                temporal_consistency = self.calculate_temporal_consistency(outputs)
                pattern_anomalies = self.detect_pattern_anomalies(outputs)
            
            result = {
                'confidence': float(fake_confidence),
                'sequence_consistency': temporal_consistency,
                'pattern_anomalies': pattern_anomalies,
                'temporal_dependencies': sequence_analysis['dependencies'],
                'lstm_hidden_states': sequence_analysis['hidden_analysis'],
                'sequence_length': len(feature_sequences),
                'processing_time': time.time() - start_time,
                'memory_persistence': self.calculate_memory_persistence(cell),
                'pattern_repetition_score': self.calculate_pattern_repetition(outputs)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"LSTM sequence analysis error: {str(e)}")
            raise
    
    def prepare_sequence_tensor(self, feature_sequences: List[np.ndarray]) -> torch.Tensor:
        """Prepare feature sequences for LSTM input"""
        # Ensure consistent sequence length
        if len(feature_sequences) > self.sequence_length:
            feature_sequences = feature_sequences[:self.sequence_length]
        elif len(feature_sequences) < self.sequence_length:
            # Pad sequence by repeating last frame
            last_feature = feature_sequences[-1]
            while len(feature_sequences) < self.sequence_length:
                feature_sequences.append(last_feature)
        
        # Stack and convert to tensor
        sequence_array = np.stack(feature_sequences, axis=0)
        sequence_tensor = torch.from_numpy(sequence_array).float().unsqueeze(0).to(self.device)
        
        return sequence_tensor
    
    def analyze_lstm_patterns(self, outputs, hidden, cell):
        """Analyze LSTM hidden states and patterns"""
        try:
            # Simple pattern analysis
            hidden_np = hidden.cpu().numpy()
            dependencies = []
            
            # Analyze hidden state variance across layers
            for layer in range(hidden_np.shape[0]):
                variance = np.var(hidden_np[layer])
                dependencies.append(float(variance))
            
            return {
                'dependencies': dependencies,
                'hidden_analysis': {
                    'mean': float(np.mean(hidden_np)),
                    'std': float(np.std(hidden_np)),
                    'max': float(np.max(hidden_np)),
                    'min': float(np.min(hidden_np))
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing LSTM patterns: {e}")
            return {'dependencies': [], 'hidden_analysis': {}}
    
    def calculate_temporal_consistency(self, outputs):
        """Calculate temporal consistency from LSTM outputs"""
        try:
            outputs_np = outputs.cpu().numpy()
            # Calculate variance across time steps
            consistency = 1.0 / (1.0 + np.var(outputs_np))
            return float(consistency)
        except Exception as e:
            logger.error(f"Error calculating temporal consistency: {e}")
            return 0.5
    
    def detect_pattern_anomalies(self, outputs):
        """Detect pattern anomalies in temporal sequence"""
        try:
            outputs_np = outputs.cpu().numpy()
            # Simple anomaly detection based on z-score
            mean = np.mean(outputs_np)
            std = np.std(outputs_np)
            anomalies = np.abs(outputs_np - mean) > (2 * std)
            return float(np.sum(anomalies) / outputs_np.size)
        except Exception as e:
            logger.error(f"Error detecting pattern anomalies: {e}")
            return 0.0
    
    def calculate_memory_persistence(self, cell):
        """Calculate LSTM cell state memory persistence"""
        try:
            cell_np = cell.cpu().numpy()
            # Measure how much information is retained
            persistence = float(np.mean(np.abs(cell_np)))
            return min(max(persistence, 0.0), 1.0)
        except Exception as e:
            logger.error(f"Error calculating memory persistence: {e}")
            return 0.5
    
    def calculate_pattern_repetition(self, outputs):
        """Calculate pattern repetition score"""
        try:
            outputs_np = outputs.cpu().numpy().squeeze()
            # Calculate autocorrelation as a measure of repetition
            if len(outputs_np.shape) > 1:
                outputs_flat = outputs_np.flatten()
            else:
                outputs_flat = outputs_np
            
            # Simple repetition score based on variance
            repetition = 1.0 / (1.0 + np.var(outputs_flat))
            return float(repetition)
        except Exception as e:
            logger.error(f"Error calculating pattern repetition: {e}")
            return 0.5

class TemporalLSTMModel(nn.Module):
    """LSTM model architecture for temporal deepfake detection"""
    
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(TemporalLSTMModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3 if num_layers > 1 else 0,
            bidirectional=True
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 256),  # *2 for bidirectional
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, x):
        lstm_out, (hidden, cell) = self.lstm(x)
        output = self.classifier(lstm_out[:, -1, :])
        return output, (hidden, cell)
