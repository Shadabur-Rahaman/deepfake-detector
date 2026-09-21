"""
Unit Tests for Classifier Dimension Auto-Rebuild
===============================================

Tests the automatic classifier rebuilding functionality that fixes dimension
mismatches between ImageNet checkpoints (1000 classes) and binary classification (2 classes).
"""

import pytest
import torch
import torch.nn as nn
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.enhanced_model_loader import EnhancedModelLoader

class TestClassifierRebuild:
    """Test classifier dimension auto-rebuild functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.loader = EnhancedModelLoader(device="cpu")
    
    def test_classifier_dimension_auto_rebuild(self):
        """Test that classifier is rebuilt when dimensions mismatch"""
        # Mock model with 1000-class classifier
        mock_model = Mock()
        mock_model.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(1280, 1000)  # ImageNet classifier
        )
        
        # Mock state dict with 1000-class weights
        mock_state_dict = {
            'classifier.1.weight': torch.randn(1000, 1280),
            'classifier.1.bias': torch.randn(1000),
            'features.0.weight': torch.randn(32, 3, 3, 3)
        }
        
        with patch('torchvision.models.efficientnet_b0') as mock_efficientnet:
            mock_efficientnet.return_value = mock_model
            
            with patch('torch.load') as mock_load:
                mock_load.return_value = mock_state_dict
                
                with patch('builtins.open', Mock()):
                    # Test the rebuild logic
                    model_path = "test_model.pth"
                    config = {"architecture": "efficientnet_b0"}
                    
                    # This should trigger classifier rebuild
                    result = self.loader._load_efficientnet_model(model_path, config)
                    
                    # Verify classifier was rebuilt
                    assert result.classifier[1].out_features == 2  # Binary classification
                    assert result.classifier[1].in_features == 1280  # Input features preserved
    
    def test_classifier_no_rebuild_when_correct(self):
        """Test that classifier is not rebuilt when dimensions are correct"""
        # Mock model with 2-class classifier (correct)
        mock_model = Mock()
        mock_model.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(1280, 2)  # Binary classifier
        )
        
        # Mock state dict with 2-class weights
        mock_state_dict = {
            'classifier.1.weight': torch.randn(2, 1280),
            'classifier.1.bias': torch.randn(2),
            'features.0.weight': torch.randn(32, 3, 3, 3)
        }
        
        with patch('torchvision.models.efficientnet_b0') as mock_efficientnet:
            mock_efficientnet.return_value = mock_model
            
            with patch('torch.load') as mock_load:
                mock_load.return_value = mock_state_dict
                
                with patch('builtins.open', Mock()):
                    model_path = "test_model.pth"
                    config = {"architecture": "efficientnet_b0"}
                    
                    result = self.loader._load_efficientnet_model(model_path, config)
                    
                    # Verify classifier was not rebuilt (still 2 classes)
                    assert result.classifier[1].out_features == 2
    
    def test_model_output_shape_verification(self):
        """Test that model output shape is verified after loading"""
        # Create a mock model that returns wrong shape
        mock_model = Mock()
        mock_model.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(1280, 3)  # Wrong: 3 classes instead of 2
        )
        
        # Mock forward pass to return wrong shape
        def mock_forward(x):
            return torch.randn(x.size(0), 3)  # Wrong output shape
        
        mock_model.forward = mock_forward
        mock_model.to.return_value = mock_model
        mock_model.eval.return_value = mock_model
        
        with patch('torchvision.models.efficientnet_b0') as mock_efficientnet:
            mock_efficientnet.return_value = mock_model
            
            with patch('torch.load') as mock_load:
                mock_load.return_value = {'features.0.weight': torch.randn(32, 3, 3, 3)}
                
                with patch('builtins.open', Mock()):
                    with patch('torch.no_grad'):
                        model_path = "test_model.pth"
                        config = {"architecture": "efficientnet_b0"}
                        
                        # This should log a warning about wrong output shape
                        with patch('logging.Logger.warning') as mock_warning:
                            result = self.loader._load_efficientnet_model(model_path, config)
                            
                            # Verify warning was logged
                            mock_warning.assert_called()
                            warning_call = mock_warning.call_args[0][0]
                            assert "Model output shape" in warning_call
                            assert "expected (1, 2)" in warning_call

if __name__ == "__main__":
    pytest.main([__file__])
