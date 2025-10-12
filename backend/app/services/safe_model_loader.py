import os
import torch
import torchvision.models as models
from torchvision.models.efficientnet import efficientnet_b0
import logging

logger = logging.getLogger(__name__)

def safe_load_efficientnet_b0():
    """Safely load EfficientNet-B0 with error handling"""
    try:
        # Method 1: Try with pretrained=False first
        print("Attempting to load EfficientNet-B0 without pretrained weights...")
        model = efficientnet_b0(pretrained=False)
        print("EfficientNet-B0 loaded without pretrained weights")
        return model
        
    except Exception as e1:
        print(f"Method 1 failed: {e1}")
        
        try:
            # Method 2: Try with weights=None
            print("Attempting to load EfficientNet-B0 with weights=None...")
            model = efficientnet_b0(weights=None)
            print("EfficientNet-B0 loaded with weights=None")
            return model
            
        except Exception as e2:
            print(f"Method 2 failed: {e2}")
            
            try:
                # Method 3: Try creating from scratch
                print("Attempting to create EfficientNet-B0 from scratch...")
                from torchvision.models.efficientnet import EfficientNet
                from torchvision.models.efficientnet import _efficientnet_conf
                
                # Get configuration
                inverted_residual_setting, last_channel = _efficientnet_conf("efficientnet_b0", width_mult=1.0, depth_mult=1.0, dropout=0.2)
                
                # Create model
                model = EfficientNet(inverted_residual_setting, 0.2, last_channel)
                print("EfficientNet-B0 created from scratch")
                return model
                
            except Exception as e3:
                print(f"Method 3 failed: {e3}")
                
                # Method 4: Use ResNet as fallback
                print("Using ResNet-18 as fallback...")
                model = models.resnet18(pretrained=False)
                print("ResNet-18 fallback loaded")
                return model

def safe_load_any_model(model_name="efficientnet_b0"):
    """Safely load any model with multiple fallback strategies"""
    model_loaders = {
        "efficientnet_b0": safe_load_efficientnet_b0,
        "resnet18": lambda: models.resnet18(pretrained=False),
        "resnet34": lambda: models.resnet34(pretrained=False),
        "densenet121": lambda: models.densenet121(pretrained=False),
    }
    
    if model_name in model_loaders:
        return model_loaders[model_name]()
    else:
        print(f"Unknown model {model_name}, using ResNet-18 fallback")
        return models.resnet18(pretrained=False)
