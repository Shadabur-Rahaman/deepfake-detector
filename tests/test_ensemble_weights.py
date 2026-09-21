"""
Unit Tests for Ensemble Weight Validation
========================================

Tests that ensemble weights sum to 1.0 and are properly distributed
across model categories as specified in the README.
"""

import pytest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.enhanced_model_loader import EnhancedModelLoader

class TestEnsembleWeights:
    """Test ensemble weight validation and distribution"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.loader = EnhancedModelLoader(device="cpu")
    
    def test_weights_sum_to_one(self):
        """Test that ensemble weights sum to 1.0"""
        total_weight = sum(cfg['weight'] for cfg in self.loader.model_configs.values())
        assert abs(total_weight - 1.0) < 0.01, f"Weights sum to {total_weight}, expected 1.0"
    
    def test_traditional_models_weight_distribution(self):
        """Test that traditional models have ~40% total weight"""
        traditional_models = [
            'efficientnet_b0', 'efficientnet_b4', 'efficientnet_b7',
            'resnet50', 'resnet101', 'resnet152',
            'densenet121', 'inception_v3'
        ]
        
        traditional_weight = sum(
            cfg['weight'] for name, cfg in self.loader.model_configs.items()
            if name in traditional_models
        )
        
        # Should be approximately 40% (0.40)
        assert 0.35 <= traditional_weight <= 0.45, f"Traditional models weight {traditional_weight:.3f}, expected ~0.40"
    
    def test_specialized_models_weight_distribution(self):
        """Test that specialized deepfake models have ~35% total weight"""
        specialized_models = [
            'mesonet', 'xception', 'capsule_net', 'f3net',
            'ffd', 'srm', 'recce', 'spsl'
        ]
        
        specialized_weight = sum(
            cfg['weight'] for name, cfg in self.loader.model_configs.items()
            if name in specialized_models
        )
        
        # Should be approximately 35% (0.35)
        assert 0.30 <= specialized_weight <= 0.40, f"Specialized models weight {specialized_weight:.3f}, expected ~0.35"
    
    def test_modern_models_weight_distribution(self):
        """Test that modern transformer models have ~25% total weight"""
        modern_models = [
            'vision_transformer', 'swin_transformer', 'convnext',
            'deit', 'beit'
        ]
        
        modern_weight = sum(
            cfg['weight'] for name, cfg in self.loader.model_configs.items()
            if name in modern_models
        )
        
        # Should be approximately 25% (0.25)
        assert 0.20 <= modern_weight <= 0.30, f"Modern models weight {modern_weight:.3f}, expected ~0.25"
    
    def test_no_dominant_model(self):
        """Test that no single model dominates the ensemble"""
        max_weight = max(cfg['weight'] for cfg in self.loader.model_configs.values())
        
        # No single model should have more than 15% weight
        assert max_weight <= 0.15, f"Dominant model has {max_weight:.3f} weight, should be <= 0.15"
    
    def test_all_weights_positive(self):
        """Test that all model weights are positive"""
        for name, cfg in self.loader.model_configs.items():
            assert cfg['weight'] > 0, f"Model {name} has non-positive weight: {cfg['weight']}"
    
    def test_model_count(self):
        """Test that we have the expected number of models configured"""
        model_count = len(self.loader.model_configs)
        
        # Should have 25+ models as advertised
        assert model_count >= 25, f"Expected 25+ models, got {model_count}"
    
    def test_model_categories_represented(self):
        """Test that all model categories are represented"""
        model_types = set(cfg['type'] for cfg in self.loader.model_configs.values())
        
        expected_types = {
            'efficientnet', 'resnet', 'mesonet', 'xception',
            'capsule', 'f3net', 'ffd', 'srm', 'recce', 'spsl',
            'vision_transformer', 'swin_transformer', 'convnext',
            'deit', 'beit', 'densenet', 'inception', 'custom'
        }
        
        # Should have diverse model types
        assert len(model_types) >= 8, f"Expected diverse model types, got {len(model_types)}"
        
        # Should include key model types
        assert 'efficientnet' in model_types, "Missing EfficientNet models"
        assert 'resnet' in model_types, "Missing ResNet models"
        assert 'mesonet' in model_types, "Missing MesoNet models"
    
    def test_weight_normalization_handles_errors(self):
        """Test that weight normalization handles edge cases"""
        # Create a loader with intentionally wrong weights
        loader = EnhancedModelLoader(device="cpu")
        
        # Manually set wrong weights that don't sum to 1.0
        loader.model_configs['test_model'] = {
            'path': 'test.pth',
            'type': 'efficientnet',
            'architecture': 'efficientnet_b0',
            'input_size': (224, 224),
            'weight': 0.5  # This will make total > 1.0
        }
        
        # The setup should handle normalization
        total_weight = sum(cfg['weight'] for cfg in loader.model_configs.values())
        
        # Should still be close to 1.0 (within tolerance)
        assert abs(total_weight - 1.0) < 0.01, f"Normalized weights sum to {total_weight}, expected ~1.0"

if __name__ == "__main__":
    pytest.main([__file__])
