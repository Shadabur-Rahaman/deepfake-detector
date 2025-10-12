"""
Model Wrapper for Deepfake Detection
Fixes the 'dict' object is not callable error by ensuring models return tensors
"""

import torch
import torch.nn as nn
import numpy as np
import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelOutput:
    """Structured model output"""
    logits: torch.Tensor
    probabilities: torch.Tensor
    prediction: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class ModelWrapper:
    """
    Wrapper that ensures models return proper tensors instead of dicts
    """
    
    def __init__(self, model: Any, model_name: str, device: torch.device):
        self.model = model
        self.model_name = model_name
        self.device = device
        self.is_torch_model = isinstance(model, nn.Module)
        
    def __call__(self, input_data: Union[torch.Tensor, np.ndarray, List[np.ndarray]]) -> ModelOutput:
        """
        Call the model and ensure it returns proper tensor output
        """
        try:
            # Handle different input types
            if isinstance(input_data, list):
                # Process first face if list of faces
                if not input_data:
                    return self._create_empty_output()
                input_tensor = self._preprocess_face(input_data[0])
            elif isinstance(input_data, np.ndarray):
                input_tensor = self._preprocess_face(input_data)
            elif isinstance(input_data, torch.Tensor):
                input_tensor = input_data.to(self.device)
            else:
                logger.warning(f"Unsupported input type for {self.model_name}: {type(input_data)}")
                return self._create_empty_output()
            
            # Ensure input is on correct device
            if not input_tensor.is_cuda and self.device.type == 'cuda':
                input_tensor = input_tensor.cuda()
            elif input_tensor.is_cuda and self.device.type == 'cpu':
                input_tensor = input_tensor.cpu()
            
            # Run inference
            with torch.no_grad():
                if self.is_torch_model:
                    output = self._run_torch_model(input_tensor)
                else:
                    output = self._run_custom_model(input_tensor, input_data)
            
            return output
            
        except Exception as e:
            logger.error(f"Error in {self.model_name} inference: {e}")
            return self._create_empty_output()
    
    def _preprocess_face(self, face: np.ndarray) -> torch.Tensor:
        """Preprocess face for model input"""
        try:
            import cv2
            
            # Resize to 224x224 if needed
            if face.shape[:2] != (224, 224):
                face = cv2.resize(face, (224, 224))
            
            # Convert BGR to RGB if needed
            if len(face.shape) == 3 and face.shape[2] == 3:
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            
            # Normalize to [0, 1]
            face = face.astype(np.float32) / 255.0
            
            # Convert to tensor and add batch dimension
            face_tensor = torch.from_numpy(face).permute(2, 0, 1).unsqueeze(0)
            
            return face_tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Error preprocessing face for {self.model_name}: {e}")
            # Return dummy tensor
            return torch.randn(1, 3, 224, 224).to(self.device)
    
    def _run_torch_model(self, input_tensor: torch.Tensor) -> ModelOutput:
        """Run PyTorch model inference"""
        try:
            # Forward pass
            raw_output = self.model(input_tensor)
            
            # Handle different output types
            if isinstance(raw_output, dict):
                # Extract logits from dict
                logits = raw_output.get('logits', raw_output.get('output', raw_output.get('prediction')))
                if logits is None:
                    # Try to find any tensor in the dict
                    for key, value in raw_output.items():
                        if isinstance(value, torch.Tensor):
                            logits = value
                            break
                
                if logits is None:
                    logger.warning(f"Could not extract logits from dict output in {self.model_name}")
                    return self._create_empty_output()
                
                metadata = {k: v for k, v in raw_output.items() if k != 'logits'}
            else:
                logits = raw_output
                metadata = None
            
            # Ensure logits is a tensor
            if not isinstance(logits, torch.Tensor):
                logger.warning(f"Model {self.model_name} returned non-tensor output: {type(logits)}")
                return self._create_empty_output()
            
            # Get probabilities
            if logits.dim() > 1:
                logits = logits.squeeze()
            
            if logits.numel() == 1:
                # Binary classification
                prob = torch.sigmoid(logits).item()
                probabilities = torch.tensor([1 - prob, prob])
                prediction = "Deepfake" if prob > 0.5 else "Real"
                confidence = max(prob, 1 - prob)
            else:
                # Multi-class classification
                probabilities = torch.softmax(logits, dim=0)
                pred_class = torch.argmax(probabilities).item()
                confidence = probabilities[pred_class].item()
                prediction = "Deepfake" if pred_class == 1 else "Real"
            
            return ModelOutput(
                logits=logits,
                probabilities=probabilities,
                prediction=prediction,
                confidence=confidence,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error running torch model {self.model_name}: {e}")
            return self._create_empty_output()
    
    def _run_custom_model(self, input_tensor: torch.Tensor, original_input: Any) -> ModelOutput:
        """Run custom model inference"""
        try:
            # Try different calling conventions
            if hasattr(self.model, 'predict'):
                result = self.model.predict(original_input)
            elif hasattr(self.model, 'detect'):
                result = self.model.detect(original_input)
            elif hasattr(self.model, '__call__'):
                result = self.model(original_input)
            else:
                logger.warning(f"Model {self.model_name} has no callable interface")
                return self._create_empty_output()
            
            # Convert result to ModelOutput
            if isinstance(result, dict):
                confidence = result.get('confidence', result.get('score', 0.5))
                prediction = result.get('prediction', result.get('label', 'Unknown'))
                
                # Convert confidence to tensor format
                if confidence > 1:
                    confidence = confidence / 100.0
                
                prob_deepfake = confidence if prediction.lower() in ['deepfake', 'fake'] else 1 - confidence
                probabilities = torch.tensor([1 - prob_deepfake, prob_deepfake])
                logits = torch.logit(probabilities.clamp(min=1e-7, max=1-1e-7))
                
                return ModelOutput(
                    logits=logits,
                    probabilities=probabilities,
                    prediction=prediction,
                    confidence=confidence,
                    metadata=result
                )
            
            elif isinstance(result, (int, float)):
                confidence = float(result)
                if confidence > 1:
                    confidence = confidence / 100.0
                
                prob_deepfake = confidence
                probabilities = torch.tensor([1 - prob_deepfake, prob_deepfake])
                logits = torch.logit(probabilities.clamp(min=1e-7, max=1-1e-7))
                prediction = "Deepfake" if confidence > 0.5 else "Real"
                
                return ModelOutput(
                    logits=logits,
                    probabilities=probabilities,
                    prediction=prediction,
                    confidence=confidence
                )
            
            else:
                logger.warning(f"Unsupported result type from {self.model_name}: {type(result)}")
                return self._create_empty_output()
                
        except Exception as e:
            logger.error(f"Error running custom model {self.model_name}: {e}")
            return self._create_empty_output()
    
    def _create_empty_output(self) -> ModelOutput:
        """Create empty output for error cases"""
        dummy_logits = torch.tensor([0.0, 0.0])
        dummy_probs = torch.tensor([0.5, 0.5])
        
        return ModelOutput(
            logits=dummy_logits,
            probabilities=dummy_probs,
            prediction="Error",
            confidence=0.0,
            metadata={"error": f"Model {self.model_name} failed"}
        )


class EnsembleModelWrapper:
    """
    Wrapper for ensemble models that ensures proper tensor output
    """
    
    def __init__(self, models: Dict[str, ModelWrapper], weights: Optional[Dict[str, float]] = None):
        self.models = models
        self.weights = weights or {name: 1.0 for name in models.keys()}
        self.device = next(iter(models.values())).device if models else torch.device('cpu')
        
        # Normalize weights
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {name: weight / total_weight for name, weight in self.weights.items()}
    
    def __call__(self, input_data: Any) -> ModelOutput:
        """Run ensemble inference"""
        if not self.models:
            return ModelOutput(
                logits=torch.tensor([0.0, 0.0]),
                probabilities=torch.tensor([0.5, 0.5]),
                prediction="No Models",
                confidence=0.0
            )
        
        # Collect outputs from all models
        outputs = []
        valid_models = []
        
        for name, model_wrapper in self.models.items():
            try:
                output = model_wrapper(input_data)
                if output.confidence > 0:  # Only use valid outputs
                    outputs.append(output)
                    valid_models.append(name)
            except Exception as e:
                logger.warning(f"Model {name} failed in ensemble: {e}")
        
        if not outputs:
            return ModelOutput(
                logits=torch.tensor([0.0, 0.0]),
                probabilities=torch.tensor([0.5, 0.5]),
                prediction="All Models Failed",
                confidence=0.0
            )
        
        # Weighted ensemble
        weighted_logits = torch.zeros_like(outputs[0].logits)
        total_weight = 0.0
        
        for i, output in enumerate(outputs):
            model_name = valid_models[i]
            weight = self.weights.get(model_name, 1.0)
            weighted_logits += weight * output.logits
            total_weight += weight
        
        if total_weight > 0:
            weighted_logits /= total_weight
        
        # Convert to probabilities
        probabilities = torch.softmax(weighted_logits, dim=0)
        pred_class = torch.argmax(probabilities).item()
        confidence = probabilities[pred_class].item()
        prediction = "Deepfake" if pred_class == 1 else "Real"
        
        # Collect metadata from all models
        metadata = {
            'ensemble_size': len(outputs),
            'models_used': valid_models,
            'individual_outputs': [
                {
                    'model': name,
                    'prediction': output.prediction,
                    'confidence': output.confidence
                }
                for name, output in zip(valid_models, outputs)
            ]
        }
        
        return ModelOutput(
            logits=weighted_logits,
            probabilities=probabilities,
            prediction=prediction,
            confidence=confidence,
            metadata=metadata
        )


def wrap_model(model: Any, model_name: str, device: torch.device) -> ModelWrapper:
    """
    Wrap a model to ensure it returns proper tensor output
    """
    return ModelWrapper(model, model_name, device)


def wrap_ensemble_models(models: Dict[str, Any], device: torch.device, weights: Optional[Dict[str, float]] = None) -> EnsembleModelWrapper:
    """
    Wrap multiple models into an ensemble
    """
    wrapped_models = {}
    for name, model in models.items():
        wrapped_models[name] = wrap_model(model, name, device)
    
    return EnsembleModelWrapper(wrapped_models, weights)
