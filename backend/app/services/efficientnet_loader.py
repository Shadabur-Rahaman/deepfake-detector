import os
import torch
import torch.nn as nn
import logging
from typing import Dict, Any, Optional, Tuple, Union

logger = logging.getLogger("services.efficientnet_loader")

# Global cache to avoid double-loading
_LOADED_MODEL = None
_LOADED_CHECKPOINTS = set()  # Track loaded checkpoints to avoid duplicate logging

def create_efficientnet_model(num_classes: int = 2) -> nn.Module:
    """
    Create EfficientNet-B0 model with proper classifier head.
    
    Args:
        num_classes: Number of output classes (default: 2 for binary classification)
        
    Returns:
        EfficientNet model with correct classifier head
    """
    try:
        import timm
        model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=num_classes)
        logger.info(f"Created EfficientNet-B0 model with {num_classes} classes using timm")
        return model
    except ImportError:
        logger.warning("timm not available, falling back to torchvision EfficientNet")
        from torchvision.models import efficientnet_b0
        model = efficientnet_b0(weights=None)
        # Replace classifier with correct number of classes
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, num_classes)
        logger.info(f"Created EfficientNet-B0 model with {num_classes} classes using torchvision")
        return model
    except Exception as e:
        logger.warning(f"timm failed ({e}), falling back to torchvision EfficientNet")
        try:
            from torchvision.models import efficientnet_b0
            model = efficientnet_b0(weights=None)
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(num_ftrs, num_classes)
            logger.info(f"Created EfficientNet-B0 model with {num_classes} classes using torchvision fallback")
            return model
        except Exception as e2:
            logger.error(f"Both timm and torchvision failed: {e2}")
            raise

def detect_num_classes_from_checkpoint(state_dict: Dict[str, Any]) -> int:
    """
    Detect the number of classes from checkpoint classifier layer.
    
    Args:
        state_dict: Model state dictionary
        
    Returns:
        Number of classes detected from classifier layer
    """
    # Look for classifier layers in the state dict
    classifier_keys = [k for k in state_dict.keys() if 'classifier' in k.lower()]
    
    for key in classifier_keys:
        if 'weight' in key and len(state_dict[key].shape) == 2:
            # This is likely the classifier weight layer
            num_classes = state_dict[key].shape[0]
            logger.info(f"Detected {num_classes} classes from checkpoint classifier layer: {key}")
            return num_classes
    
    # Default to 2 classes if not detected
    logger.info("Could not detect number of classes from checkpoint, defaulting to 2")
    return 2

def clean_state_dict(state_dict: Dict[str, Any], target_model: nn.Module) -> Dict[str, Any]:
    """
    Clean and remap state dictionary to match target model architecture.
    
    Args:
        state_dict: Source state dictionary
        target_model: Target model to match
        
    Returns:
        Cleaned state dictionary compatible with target model
    """
    target_sd = target_model.state_dict()
    cleaned_sd = {}
    
    # Track used keys to avoid duplicates
    used_keys = set()
    
    # First pass: exact name matches
    for target_key, target_tensor in target_sd.items():
        if target_key in state_dict:
            source_tensor = state_dict[target_key]
            if source_tensor.shape == target_tensor.shape:
                cleaned_sd[target_key] = source_tensor
                used_keys.add(target_key)
                continue
    
    # Second pass: shape-based matching for unmatched keys
    for target_key, target_tensor in target_sd.items():
        if target_key in cleaned_sd:
            continue
            
        target_shape = target_tensor.shape
        
        # Find best matching source tensor by shape
        best_match = None
        best_key = None
        
        for source_key, source_tensor in state_dict.items():
            if source_key in used_keys:
                continue
                
            if source_tensor.shape == target_shape:
                best_match = source_tensor
                best_key = source_key
                break
        
        if best_match is not None:
            cleaned_sd[target_key] = best_match
            used_keys.add(best_key)
            logger.debug(f"Remapped {best_key} -> {target_key} (shape: {target_shape})")
    
    return cleaned_sd

def load_checkpoint_with_conversion(
    model: nn.Module, 
    ckpt_path: str, 
    device: str = "cpu"
) -> Tuple[nn.Module, bool]:
    """
    Load checkpoint with automatic conversion and cleanup.
    
    Args:
        model: Model to load weights into
        ckpt_path: Path to checkpoint file
        device: Target device
        
    Returns:
        Tuple of (loaded_model, was_converted)
    """
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
    
    # Load checkpoint
    logger.info(f"Loading checkpoint: {os.path.basename(ckpt_path)}")
    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    
    # Extract state dict
    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    elif isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint
    
    # Detect number of classes from checkpoint
    detected_classes = detect_num_classes_from_checkpoint(state_dict)
    
    # Create model with correct number of classes if needed
    if detected_classes != 2:  # Assuming we want 2 classes for binary classification
        logger.info(f"Checkpoint has {detected_classes} classes, creating model with 2 classes")
        model = create_efficientnet_model(num_classes=2)
    
    # Clean and remap state dictionary
    cleaned_state_dict = clean_state_dict(state_dict, model)
    
    # Load state dict with strict=False
    missing_keys, unexpected_keys = model.load_state_dict(cleaned_state_dict, strict=False)
    
    # Log key mismatches only once per checkpoint
    checkpoint_id = os.path.basename(ckpt_path)
    if checkpoint_id not in _LOADED_CHECKPOINTS:
        if missing_keys or unexpected_keys:
            logger.info(f"Model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
            if missing_keys:
                logger.debug(f"Missing keys: {missing_keys[:5]}{'...' if len(missing_keys) > 5 else ''}")
            if unexpected_keys:
                logger.debug(f"Unexpected keys: {unexpected_keys[:5]}{'...' if len(unexpected_keys) > 5 else ''}")
        else:
            logger.info("Model loaded successfully with no key mismatches")
        
        _LOADED_CHECKPOINTS.add(checkpoint_id)
    
    # Save converted checkpoint if there were significant changes
    was_converted = False
    if missing_keys or unexpected_keys:
        converted_path = os.path.splitext(ckpt_path)[0] + "_converted.pth"
        try:
            torch.save(cleaned_state_dict, converted_path)
            logger.info(f"[OK] Saved converted checkpoint to: {os.path.basename(converted_path)}")
            was_converted = True
        except Exception as e:
            logger.warning(f"Failed to save converted checkpoint: {e}")
    
    return model, was_converted

def load_efficientnet_once(ckpt_path: str, device: str = "cpu", num_classes: int = 2) -> Optional[nn.Module]:
    """
    Load EfficientNet model with improved checkpoint handling.
    
    Args:
        ckpt_path: Path to checkpoint file
        device: Target device (cpu/cuda)
        num_classes: Number of output classes
        
    Returns:
        Loaded model or None if loading failed
    """
    global _LOADED_MODEL
    
    if _LOADED_MODEL is not None:
        # Reduced logging to avoid duplicates
        return _LOADED_MODEL
    
    try:
        # Create model
        model = create_efficientnet_model(num_classes=num_classes)
        
        # Load checkpoint with conversion
        model, was_converted = load_checkpoint_with_conversion(model, ckpt_path, device)
        
        # Move to device and set to eval mode
        model = model.to(device).eval()
        
        # Cache the model
        _LOADED_MODEL = model
        
        conversion_status = " (converted)" if was_converted else ""
        logger.info(f"[OK] EfficientNet model loaded and moved to {device}{conversion_status}")
        
        return _LOADED_MODEL
        
    except Exception as e:
        logger.error(f"Failed to load EfficientNet model: {e}")
        return None

def reset_model_cache():
    """Reset the global model cache (useful for testing)."""
    global _LOADED_MODEL, _LOADED_CHECKPOINTS
    _LOADED_MODEL = None
    _LOADED_CHECKPOINTS.clear()
    logger.info("Model cache reset")

def get_model_info() -> Dict[str, Any]:
    """Get information about the currently loaded model."""
    if _LOADED_MODEL is None:
        return {"loaded": False}
    
    return {
        "loaded": True,
        "device": str(next(_LOADED_MODEL.parameters()).device),
        "num_parameters": sum(p.numel() for p in _LOADED_MODEL.parameters()),
        "model_class": _LOADED_MODEL.__class__.__name__
    }