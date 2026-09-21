# backend/app/tests/test_model_loading.py - Unit Tests for Model Loading System

import pytest
import logging
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.model_availability import (
    initialize_model_availability, get_availability_status, 
    get_installation_hints, TIMM_AVAILABLE, YOLO_AVAILABLE, 
    TORCHVISION_AVAILABLE, VIT_AVAILABLE, LSTM_AVAILABLE, RESNET_AVAILABLE
)
from services.model_loader import ModelLoader, ModelLoadResult, get_model_loader

class TestModelAvailability:
    """Test model availability detection"""
    
    def test_availability_flags_are_defined(self):
        """Test that all availability flags are defined and boolean"""
        flags = [TIMM_AVAILABLE, YOLO_AVAILABLE, TORCHVISION_AVAILABLE, 
                VIT_AVAILABLE, LSTM_AVAILABLE, RESNET_AVAILABLE]
        
        for flag in flags:
            assert isinstance(flag, bool), f"Flag {flag} should be boolean"
    
    def test_initialize_model_availability_returns_dict(self):
        """Test that initialize_model_availability returns a proper dictionary"""
        status = initialize_model_availability()
        
        assert isinstance(status, dict)
        expected_keys = ['timm', 'yolo', 'torchvision', 'vit', 'lstm', 'resnet']
        for key in expected_keys:
            assert key in status
            assert isinstance(status[key], bool)
    
    def test_get_availability_status(self):
        """Test get_availability_status returns current status"""
        status = get_availability_status()
        
        assert isinstance(status, dict)
        expected_keys = ['timm', 'yolo', 'torchvision', 'vit', 'lstm', 'resnet']
        for key in expected_keys:
            assert key in status
            assert isinstance(status[key], bool)
    
    def test_get_installation_hints(self):
        """Test get_installation_hints returns proper hints"""
        hints = get_installation_hints()
        
        assert isinstance(hints, dict)
        # Should have hints for unavailable models
        for model, hint in hints.items():
            assert isinstance(model, str)
            assert isinstance(hint, str)
            assert len(hint) > 0

class TestModelLoader:
    """Test model loader functionality"""
    
    def test_model_loader_initialization(self):
        """Test ModelLoader initializes correctly"""
        loader = ModelLoader(device="cpu")
        
        assert loader.device == "cpu"
        assert isinstance(loader.loaded_models, dict)
        assert isinstance(loader.availability_status, dict)
        assert isinstance(loader.installation_hints, dict)
    
    def test_safe_load_success(self):
        """Test safe_load with successful model loading"""
        loader = ModelLoader(device="cpu")
        
        def mock_load_func():
            return "mock_model"
        
        result = loader.safe_load("test_model", mock_load_func)
        
        assert isinstance(result, ModelLoadResult)
        assert result.success is True
        assert result.model == "mock_model"
        assert result.error_message is None
        assert result.model_type == "test_model"
        assert result.dependencies_met is True
    
    def test_safe_load_failure(self):
        """Test safe_load with failed model loading"""
        loader = ModelLoader(device="cpu")
        
        def mock_load_func():
            raise RuntimeError("Model loading failed")
        
        result = loader.safe_load("test_model", mock_load_func)
        
        assert isinstance(result, ModelLoadResult)
        assert result.success is False
        assert result.model is None
        assert "Model loading failed" in result.error_message
        assert result.model_type == "test_model"
        assert result.dependencies_met is True
    
    def test_safe_load_missing_dependencies(self):
        """Test safe_load with missing dependencies"""
        loader = ModelLoader(device="cpu")
        
        # Mock availability status to show missing dependencies
        loader.availability_status = {'timm': False, 'yolo': True}
        
        def mock_load_func():
            return "mock_model"
        
        result = loader.safe_load("test_model", mock_load_func, dependencies=['timm'])
        
        assert isinstance(result, ModelLoadResult)
        assert result.success is False
        assert result.model is None
        assert "Missing dependencies" in result.error_message
        assert result.dependencies_met is False
    
    def test_load_all_models_returns_dict(self):
        """Test load_all_models returns a dictionary of results"""
        loader = ModelLoader(device="cpu")
        
        # Mock the individual load methods to avoid actual model loading
        with patch.object(loader, 'load_efficientnet_b0') as mock_eff, \
             patch.object(loader, 'load_yolov8_face') as mock_yolo, \
             patch.object(loader, 'load_mesonet') as mock_mesonet, \
             patch.object(loader, 'load_resnet50') as mock_resnet, \
             patch.object(loader, 'load_vit') as mock_vit, \
             patch.object(loader, 'load_vivit') as mock_vivit, \
             patch.object(loader, 'load_lstm') as mock_lstm:
            
            # Mock successful results
            mock_result = ModelLoadResult(True, "mock_model", None, "test", True)
            mock_eff.return_value = mock_result
            mock_yolo.return_value = mock_result
            mock_mesonet.return_value = mock_result
            mock_resnet.return_value = mock_result
            mock_vit.return_value = mock_result
            mock_vivit.return_value = mock_result
            mock_lstm.return_value = mock_result
            
            results = loader.load_all_models()
            
            assert isinstance(results, dict)
            expected_models = ['efficientnet_b0', 'yolov8_face', 'mesonet', 
                             'resnet50', 'vit', 'vivit', 'lstm']
            for model in expected_models:
                assert model in results
                assert isinstance(results[model], ModelLoadResult)
    
    def test_get_loaded_models(self):
        """Test get_loaded_models returns only successful models"""
        loader = ModelLoader(device="cpu")
        
        # Mock loaded models with mixed success/failure
        loader.loaded_models = {
            'model1': ModelLoadResult(True, "model1", None, "model1", True),
            'model2': ModelLoadResult(False, None, "Error", "model2", True),
            'model3': ModelLoadResult(True, "model3", None, "model3", True)
        }
        
        loaded = loader.get_loaded_models()
        
        assert isinstance(loaded, dict)
        assert 'model1' in loaded
        assert 'model3' in loaded
        assert 'model2' not in loaded
        assert loaded['model1'] == "model1"
        assert loaded['model3'] == "model3"
    
    def test_get_model_status(self):
        """Test get_model_status returns detailed status"""
        loader = ModelLoader(device="cpu")
        
        # Mock loaded models
        loader.loaded_models = {
            'model1': ModelLoadResult(True, "model1", None, "model1", True),
            'model2': ModelLoadResult(False, None, "Error", "model2", False)
        }
        
        status = loader.get_model_status()
        
        assert isinstance(status, dict)
        assert 'model1' in status
        assert 'model2' in status
        
        # Check model1 status
        assert status['model1']['loaded'] is True
        assert status['model1']['model_available'] is True
        assert status['model1']['dependencies_met'] is True
        assert status['model1']['error'] is None
        
        # Check model2 status
        assert status['model2']['loaded'] is False
        assert status['model2']['model_available'] is False
        assert status['model2']['dependencies_met'] is False
        assert status['model2']['error'] == "Error"
    
    def test_get_startup_summary(self):
        """Test get_startup_summary returns comprehensive summary"""
        loader = ModelLoader(device="cpu")
        
        # Mock loaded models
        loader.loaded_models = {
            'model1': ModelLoadResult(True, "model1", None, "model1", True),
            'model2': ModelLoadResult(False, None, "Error", "model2", False),
            'model3': ModelLoadResult(False, None, "Missing deps", "model3", False)
        }
        
        summary = loader.get_startup_summary()
        
        assert isinstance(summary, dict)
        assert 'total_models_attempted' in summary
        assert 'successful_models' in summary
        assert 'failed_models' in summary
        assert 'missing_dependencies' in summary
        assert 'ensemble_models' in summary
        assert 'availability_status' in summary
        assert 'installation_hints' in summary
        assert 'device' in summary
        
        assert summary['total_models_attempted'] == 3
        assert 'model1' in summary['successful_models']
        assert 'model2' in summary['failed_models']
        assert 'model3' in summary['missing_dependencies']

class TestGlobalModelLoader:
    """Test global model loader functions"""
    
    def test_get_model_loader_singleton(self):
        """Test get_model_loader returns singleton instance"""
        loader1 = get_model_loader()
        loader2 = get_model_loader()
        
        assert loader1 is loader2
        assert isinstance(loader1, ModelLoader)
    
    @patch('services.model_loader.load_all_models')
    def test_load_all_models_global(self, mock_load_all):
        """Test global load_all_models function"""
        mock_load_all.return_value = {'test': ModelLoadResult(True, "test", None, "test", True)}
        
        from services.model_loader import load_all_models
        results = load_all_models()
        
        assert isinstance(results, dict)
        mock_load_all.assert_called_once()
    
    @patch('services.model_loader.get_model_loader')
    def test_get_loaded_models_global(self, mock_get_loader):
        """Test global get_loaded_models function"""
        mock_loader = MagicMock()
        mock_loader.get_loaded_models.return_value = {'test': 'model'}
        mock_get_loader.return_value = mock_loader
        
        from services.model_loader import get_loaded_models
        models = get_loaded_models()
        
        assert models == {'test': 'model'}
        mock_loader.get_loaded_models.assert_called_once()
    
    @patch('services.model_loader.get_model_loader')
    def test_get_startup_summary_global(self, mock_get_loader):
        """Test global get_startup_summary function"""
        mock_loader = MagicMock()
        mock_loader.get_startup_summary.return_value = {'test': 'summary'}
        mock_get_loader.return_value = mock_loader
        
        from services.model_loader import get_startup_summary
        summary = get_startup_summary()
        
        assert summary == {'test': 'summary'}
        mock_loader.get_startup_summary.assert_called_once()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
