# backend/app/tests/test_deterministic_behavior.py - Deterministic Behavior Regression Tests

import asyncio
import pytest
import numpy as np
import cv2
import torch
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from services.deterministic_config import setup_deterministic_inference, get_deterministic_config
from services.deterministic_ensemble_detector import DeterministicEnsembleDetector
from services.deterministic_face_detector import detect_faces_deterministic
from services.deterministic_deepfake_detector import DeterministicDeepfakeDetector

class TestDeterministicBehavior:
    """Test suite for deterministic behavior verification"""
    
    @pytest.fixture(autouse=True)
    def setup_deterministic_environment(self):
        """Setup deterministic environment for all tests"""
        setup_deterministic_inference(seed=42, enable=True)
        yield
        # Cleanup after each test
    
    @pytest.fixture
    def test_image(self):
        """Create a deterministic test image"""
        # Create a simple test image with known properties
        image = np.zeros((224, 224, 3), dtype=np.uint8)
        # Add some deterministic patterns
        image[50:150, 50:150] = [128, 128, 128]  # Gray square
        image[100:120, 100:120] = [255, 255, 255]  # White square
        return image
    
    @pytest.fixture
    def test_faces(self, test_image):
        """Create test faces from the test image"""
        # Simulate face detection by cropping the test image
        faces = [test_image[50:150, 50:150]]  # Single face crop
        return faces
    
    def test_deterministic_seeds(self):
        """Test that seeds are set correctly"""
        config = get_deterministic_config()
        
        assert config.seed == 42
        assert config.enable_deterministic == True
        assert config._initialized == True
        
        # Test that PyTorch is configured for deterministic behavior
        assert torch.backends.cudnn.deterministic == True
        assert torch.backends.cudnn.benchmark == False
    
    def test_preprocessing_hash_consistency(self, test_image):
        """Test that identical inputs produce identical preprocessing hashes"""
        config = get_deterministic_config()
        
        # Generate hash multiple times
        hash1 = config.generate_preprocessing_hash(test_image)
        hash2 = config.generate_preprocessing_hash(test_image)
        hash3 = config.generate_preprocessing_hash(test_image)
        
        # All hashes should be identical
        assert hash1 == hash2 == hash3
        assert len(hash1) == 16  # Should be 16 characters
    
    def test_preprocessing_deterministic(self, test_image):
        """Test that preprocessing produces identical results"""
        from services.deterministic_deepfake_detector import DeterministicDeepfakeDetector
        
        detector = DeterministicDeepfakeDetector()
        
        # Preprocess the same image multiple times
        result1 = detector.preprocess_face_deterministic(test_image)
        result2 = detector.preprocess_face_deterministic(test_image)
        result3 = detector.preprocess_face_deterministic(test_image)
        
        # All results should be identical
        assert torch.allclose(result1, result2, atol=1e-6)
        assert torch.allclose(result2, result3, atol=1e-6)
        assert torch.allclose(result1, result3, atol=1e-6)
    
    def test_face_detection_deterministic(self, test_image):
        """Test that face detection produces consistent results"""
        # Run face detection multiple times
        faces1, coords1 = detect_faces_deterministic(test_image)
        faces2, coords2 = detect_faces_deterministic(test_image)
        faces3, coords3 = detect_faces_deterministic(test_image)
        
        # Results should be consistent (may be empty, but should be the same)
        assert len(faces1) == len(faces2) == len(faces3)
        assert len(coords1) == len(coords2) == len(coords3)
        
        # If faces are detected, they should be identical
        if faces1:
            for i in range(len(faces1)):
                assert np.array_equal(faces1[i], faces2[i])
                assert np.array_equal(faces2[i], faces3[i])
    
    @pytest.mark.asyncio
    async def test_ensemble_detection_deterministic(self, test_faces):
        """Test that ensemble detection produces identical results"""
        detector = DeterministicEnsembleDetector()
        await detector.initialize_models()
        
        # Run ensemble detection multiple times
        result1 = await detector.detect_ensemble(test_faces, frame_id=0)
        result2 = await detector.detect_ensemble(test_faces, frame_id=0)
        result3 = await detector.detect_ensemble(test_faces, frame_id=0)
        
        # Preprocessing hashes should be identical
        assert result1.preproc_hash == result2.preproc_hash == result3.preproc_hash
        
        # Model results should be identical (within floating point precision)
        for model_name in result1.model_results:
            if model_name in result2.model_results and model_name in result3.model_results:
                r1 = result1.model_results[model_name]
                r2 = result2.model_results[model_name]
                r3 = result3.model_results[model_name]
                
                assert r1.prediction == r2.prediction == r3.prediction
                assert abs(r1.confidence - r2.confidence) < 1e-5
                assert abs(r2.confidence - r3.confidence) < 1e-5
                assert abs(r1.raw_output - r2.raw_output) < 1e-5
                assert abs(r2.raw_output - r3.raw_output) < 1e-5
        
        # Fusion results should be identical
        assert abs(result1.fusion_raw - result2.fusion_raw) < 1e-5
        assert abs(result2.fusion_raw - result3.fusion_raw) < 1e-5
        assert result1.final_prediction == result2.final_prediction == result3.final_prediction
        assert abs(result1.final_confidence - result2.final_confidence) < 1e-5
        assert abs(result2.final_confidence - result3.final_confidence) < 1e-5
    
    def test_model_weights_consistency(self):
        """Test that model weights are consistent"""
        config = get_deterministic_config()
        weights = config.get_model_weights()
        
        # Weights should sum to approximately 1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 1e-6
        
        # All weights should be positive
        for weight in weights.values():
            assert weight > 0
    
    def test_thresholds_consistency(self):
        """Test that thresholds are within valid ranges"""
        config = get_deterministic_config()
        thresholds = config.get_thresholds()
        
        # Deepfake threshold should be between 0 and 1
        assert 0 <= thresholds.get("deepfake_threshold", 0.5) <= 1
        
        # Min confidence should be between 0 and 1
        assert 0 <= thresholds.get("min_confidence_for_fake", 0.7) <= 1
        
        # Temporal smoothing alpha should be between 0 and 1
        assert 0 <= thresholds.get("temporal_smoothing_alpha", 0.3) <= 1
    
    @pytest.mark.asyncio
    async def test_temporal_smoothing_consistency(self, test_faces):
        """Test that temporal smoothing produces consistent results"""
        detector = DeterministicEnsembleDetector()
        await detector.initialize_models()
        
        # Run detection multiple times with same input
        results = []
        for i in range(5):
            result = await detector.detect_ensemble(test_faces, frame_id=i)
            results.append(result)
        
        # All results should have the same preprocessing hash
        preproc_hashes = [r.preproc_hash for r in results]
        assert len(set(preproc_hashes)) == 1  # All should be identical
        
        # Raw fusion results should be identical
        fusion_raws = [r.fusion_raw for r in results]
        for i in range(1, len(fusion_raws)):
            assert abs(fusion_raws[0] - fusion_raws[i]) < 1e-5
    
    def test_config_persistence(self):
        """Test that configuration can be saved and loaded"""
        config = get_deterministic_config()
        
        # Update configuration
        config.update_config({
            "test_value": 123,
            "model_weights": {
                "efficientnet_b0": 0.3,
                "mesonet": 0.3,
                "yolov8_face": 0.2,
                "resnet50": 0.2
            }
        })
        
        # Check that values were updated
        assert config.config_data["test_value"] == 123
        assert config.get_model_weights()["efficientnet_b0"] == 0.3
        
        # Reset to default
        config.update_config({
            "test_value": None,
            "model_weights": {
                "efficientnet_b0": 0.25,
                "mesonet": 0.20,
                "yolov8_face": 0.15,
                "resnet50": 0.15,
                "vit": 0.10,
                "vivit": 0.10,
                "lstm": 0.05
            }
        })
    
    def test_deterministic_info_completeness(self):
        """Test that deterministic info contains all required fields"""
        config = get_deterministic_config()
        info = config.get_deterministic_info()
        
        required_fields = [
            "seed", "enable_deterministic", "initialized",
            "pytorch_deterministic", "pytorch_benchmark", "cuda_available",
            "environment_variables", "config_file", "model_weights", "thresholds"
        ]
        
        for field in required_fields:
            assert field in info, f"Missing field: {field}"
        
        # Check specific values
        assert info["seed"] == 42
        assert info["enable_deterministic"] == True
        assert info["initialized"] == True
        assert info["pytorch_deterministic"] == True
        assert info["pytorch_benchmark"] == False

class TestRegressionConsistency:
    """Test suite for regression consistency across runs"""
    
    def test_identical_inputs_produce_identical_outputs(self):
        """Test that identical inputs always produce identical outputs"""
        # This test should be run multiple times to ensure consistency
        config = get_deterministic_config()
        
        # Create a test image
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        # Generate hash multiple times
        hashes = []
        for _ in range(10):
            hash_val = config.generate_preprocessing_hash(test_image)
            hashes.append(hash_val)
        
        # All hashes should be identical
        assert len(set(hashes)) == 1, f"Hash inconsistency: {hashes}"
    
    def test_model_initialization_consistency(self):
        """Test that model initialization is consistent"""
        config = get_deterministic_config()
        
        # Check that configuration is consistent
        weights1 = config.get_model_weights()
        weights2 = config.get_model_weights()
        
        assert weights1 == weights2
        
        thresholds1 = config.get_thresholds()
        thresholds2 = config.get_thresholds()
        
        assert thresholds1 == thresholds2

if __name__ == "__main__":
    # Run tests directly
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    
    # Setup deterministic environment
    setup_deterministic_inference(seed=42, enable=True)
    
    # Run basic tests
    test_suite = TestDeterministicBehavior()
    test_suite.setup_deterministic_environment()
    
    print("Running deterministic behavior tests...")
    
    # Test seeds
    test_suite.test_deterministic_seeds()
    print("[OK] Seed test passed")
    
    # Test preprocessing hash
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    test_suite.test_preprocessing_hash_consistency(test_image)
    print("[OK] Preprocessing hash test passed")
    
    # Test configuration
    test_suite.test_model_weights_consistency()
    print("[OK] Model weights test passed")
    
    test_suite.test_thresholds_consistency()
    print("[OK] Thresholds test passed")
    
    test_suite.test_deterministic_info_completeness()
    print("[OK] Deterministic info test passed")
    
    print("[COMPLETE] All deterministic behavior tests passed!")
