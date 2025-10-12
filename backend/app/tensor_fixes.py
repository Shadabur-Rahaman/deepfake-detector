"""
Tensor Processing Fixes for Deepfake Detection
Fixes tensor-related issues in the detection pipeline
"""

import torch
import numpy as np
import logging
from typing import List, Tuple, Optional, Union

logger = logging.getLogger(__name__)

class TensorProcessor:
    """Enhanced tensor processor with robust error handling"""
    
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.default_input_size = (224, 224)
        
    def safe_tensor_conversion(self, data: Union[np.ndarray, torch.Tensor, List]) -> torch.Tensor:
        """Safely convert various data types to tensor"""
        try:
            if isinstance(data, torch.Tensor):
                return data.to(self.device)
            elif isinstance(data, np.ndarray):
                # Ensure proper dtype and shape
                if data.dtype != np.float32:
                    data = data.astype(np.float32)
                return torch.from_numpy(data).to(self.device)
            elif isinstance(data, list):
                # Convert list to numpy first, then to tensor
                np_data = np.array(data, dtype=np.float32)
                return torch.from_numpy(np_data).to(self.device)
            else:
                raise ValueError(f"Unsupported data type: {type(data)}")
        except Exception as e:
            logger.error(f"[ERROR] Tensor conversion failed: {e}")
            # Return fallback tensor
            return torch.randn(1, 3, 224, 224).to(self.device)
    
    def normalize_tensor(self, tensor: torch.Tensor, mean: List[float] = None, std: List[float] = None) -> torch.Tensor:
        """Normalize tensor with proper mean and std"""
        try:
            if mean is None:
                mean = [0.485, 0.456, 0.406]  # ImageNet mean
            if std is None:
                std = [0.229, 0.224, 0.225]   # ImageNet std
            
            # Ensure tensor is in correct format
            if tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)  # Add batch dimension
            
            # Normalize
            mean_tensor = torch.tensor(mean).view(1, 3, 1, 1).to(tensor.device)
            std_tensor = torch.tensor(std).view(1, 3, 1, 1).to(tensor.device)
            
            return (tensor - mean_tensor) / std_tensor
            
        except Exception as e:
            logger.error(f"[ERROR] Tensor normalization failed: {e}")
            return tensor
    
    def preprocess_face_robust(self, face: np.ndarray) -> torch.Tensor:
        """Robust face preprocessing with error handling"""
        try:
            if face is None or face.size == 0:
                logger.warning("[WARNING] Empty face input, using fallback")
                return torch.randn(1, 3, 224, 224).to(self.device)
            
            # Ensure face is in correct format
            if len(face.shape) != 3 or face.shape[2] != 3:
                logger.warning(f"[WARNING] Invalid face shape: {face.shape}, reshaping")
                if len(face.shape) == 2:
                    # Grayscale to RGB
                    face = np.stack([face] * 3, axis=2)
                elif face.shape[2] != 3:
                    # Convert to RGB
                    face = face[:, :, :3]
            
            # Resize to standard size
            import cv2
            face_resized = cv2.resize(face, self.default_input_size)
            
            # Convert BGR to RGB if needed
            if face_resized.shape[2] == 3:
                face_resized = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            
            # Convert to float and normalize to [0, 1]
            face_normalized = face_resized.astype(np.float32) / 255.0
            
            # Convert to tensor and add batch dimension
            face_tensor = torch.from_numpy(face_normalized).permute(2, 0, 1).unsqueeze(0)
            
            # Move to device
            face_tensor = face_tensor.to(self.device)
            
            # Apply normalization
            face_tensor = self.normalize_tensor(face_tensor)
            
            return face_tensor
            
        except Exception as e:
            logger.error(f"[ERROR] Face preprocessing failed: {e}")
            return torch.randn(1, 3, 224, 224).to(self.device)
    
    def safe_model_inference(self, model: torch.nn.Module, input_tensor: torch.Tensor) -> torch.Tensor:
        """Safe model inference with error handling"""
        try:
            if model is None:
                logger.warning("[WARNING] Model is None, returning fallback output")
                return torch.tensor([0.5]).to(self.device)
            
            # Ensure model is in eval mode
            model.eval()
            
            # Ensure input tensor is on correct device
            input_tensor = input_tensor.to(self.device)
            
            with torch.no_grad():
                try:
                    output = model(input_tensor)
                    
                    # Ensure output is a tensor
                    if not isinstance(output, torch.Tensor):
                        logger.warning(f"[WARNING] Model output is not a tensor: {type(output)}")
                        return torch.tensor([0.5]).to(self.device)
                    
                    # Handle different output shapes
                    if output.dim() > 1:
                        output = output.squeeze()
                    
                    # Ensure output is 1D
                    if output.dim() == 0:
                        output = output.unsqueeze(0)
                    
                    return output
                    
                except Exception as inference_error:
                    logger.error(f"[ERROR] Model inference failed: {inference_error}")
                    return torch.tensor([0.5]).to(self.device)
                    
        except Exception as e:
            logger.error(f"[ERROR] Safe model inference failed: {e}")
            return torch.tensor([0.5]).to(self.device)
    
    def process_model_output(self, output: torch.Tensor, model_name: str = "unknown") -> Tuple[float, str, float]:
        """Process model output to get prediction, confidence, and raw output"""
        try:
            # Convert to numpy for easier processing
            if isinstance(output, torch.Tensor):
                output_np = output.cpu().numpy()
            else:
                output_np = np.array(output)
            
            # Handle different output formats
            if len(output_np.shape) > 1:
                output_np = output_np.flatten()
            
            # Get the main prediction value
            if len(output_np) == 1:
                raw_output = float(output_np[0])
            elif len(output_np) == 2:
                # Binary classification output
                raw_output = float(output_np[1])  # Probability of positive class
            else:
                # Multi-class output, take the maximum
                raw_output = float(np.max(output_np))
            
            # Apply sigmoid if needed (for logits)
            if raw_output < 0 or raw_output > 1:
                raw_output = 1.0 / (1.0 + np.exp(-raw_output))  # Sigmoid
            
            # Ensure raw_output is in valid range
            raw_output = max(0.0, min(1.0, raw_output))
            
            # Determine prediction and confidence
            if raw_output >= 0.7:
                prediction = "Deepfake Detected"
                confidence = raw_output * 100
            elif raw_output <= 0.3:
                prediction = "Real Face"
                confidence = (1.0 - raw_output) * 100
            else:
                prediction = "Uncertain"
                confidence = 50.0
            
            # Ensure confidence is in valid range
            confidence = max(0.0, min(100.0, confidence))
            
            logger.debug(f"🔍 {model_name}: raw={raw_output:.4f}, pred={prediction}, conf={confidence:.2f}%")
            
            return raw_output, prediction, confidence
            
        except Exception as e:
            logger.error(f"[ERROR] Model output processing failed for {model_name}: {e}")
            return 0.5, "Processing Error", 0.0

# Global tensor processor instance
tensor_processor = TensorProcessor()

def get_tensor_processor(device: str = "cpu") -> TensorProcessor:
    """Get tensor processor instance"""
    global tensor_processor
    if str(tensor_processor.device) != device:
        tensor_processor = TensorProcessor(device)
    return tensor_processor

def fix_tensor_issues():
    """Apply comprehensive tensor fixes"""
    try:
        # Set PyTorch to deterministic mode for consistent results
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        
        # Set random seeds for reproducibility
        torch.manual_seed(42)
        np.random.seed(42)
        
        logger.info("[OK] Tensor processing fixes applied successfully")
        
    except Exception as e:
        logger.error(f"[ERROR] Tensor fixes failed: {e}")

# Apply fixes immediately
fix_tensor_issues()
