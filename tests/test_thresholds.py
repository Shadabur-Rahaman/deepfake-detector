"""
Unit Tests for Detection Threshold Corrections
=============================================

Tests that mode thresholds match README specifications (45%/50%/55%)
and that threshold logic correctly classifies content.
"""

import pytest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.mvp_detection_modes_2025 import (
    MVPAggressiveDetector2025,
    MVPHybridDetector2025,
    MVPConservativeDetector2025,
    DetectionMode
)

class TestThresholds:
    """Test detection threshold corrections"""
    
    def test_aggressive_threshold_45_percent(self):
        """Test that aggressive mode uses 45% threshold as per README"""
        detector = MVPAggressiveDetector2025()
        assert detector.ai_detection_threshold == 0.45, f"Expected 0.45, got {detector.ai_detection_threshold}"
    
    def test_hybrid_threshold_50_percent(self):
        """Test that hybrid mode uses 50% threshold as per README"""
        detector = MVPHybridDetector2025()
        assert detector.ai_detection_threshold == 0.50, f"Expected 0.50, got {detector.ai_detection_threshold}"
    
    def test_conservative_threshold_55_percent(self):
        """Test that conservative mode uses 55% threshold as per README"""
        detector = MVPConservativeDetector2025()
        assert detector.ai_detection_threshold == 0.55, f"Expected 0.55, got {detector.ai_detection_threshold}"
    
    def test_threshold_classification_logic_aggressive(self):
        """Test threshold classification logic for aggressive mode"""
        detector = MVPAggressiveDetector2025()
        
        # Test cases around 45% threshold
        test_cases = [
            (0.40, "Authentic Video"),  # Below threshold
            (0.45, "AI-Generated Content Detected"),  # At threshold
            (0.50, "AI-Generated Content Detected"),  # Above threshold
            (0.60, "AI-Generated Content Detected"),  # Well above threshold
        ]
        
        for confidence, expected in test_cases:
            # Mock the finalize decision method
            result = detector._finalize_decision(
                ensemble_result=None,
                validation_result=None,
                detection_scores=[('test_model', confidence, 1.0)],
                processing_time=1.0,
                faces_detected=1
            )
            
            assert result.prediction == expected, f"Confidence {confidence} should predict '{expected}', got '{result.prediction}'"
    
    def test_threshold_classification_logic_hybrid(self):
        """Test threshold classification logic for hybrid mode"""
        detector = MVPHybridDetector2025()
        
        # Test cases around 50% threshold
        test_cases = [
            (0.45, "Authentic Video"),  # Below threshold
            (0.50, "AI-Generated Content Detected"),  # At threshold
            (0.55, "AI-Generated Content Detected"),  # Above threshold
            (0.60, "AI-Generated Content Detected"),  # Well above threshold
        ]
        
        for confidence, expected in test_cases:
            result = detector._finalize_decision(
                ensemble_result=None,
                validation_result=None,
                detection_scores=[('test_model', confidence, 1.0)],
                processing_time=1.0,
                faces_detected=1
            )
            
            assert result.prediction == expected, f"Confidence {confidence} should predict '{expected}', got '{result.prediction}'"
    
    def test_threshold_classification_logic_conservative(self):
        """Test threshold classification logic for conservative mode"""
        detector = MVPConservativeDetector2025()
        
        # Test cases around 55% threshold
        test_cases = [
            (0.50, "Authentic Video"),  # Below threshold
            (0.55, "AI-Generated Content Detected"),  # At threshold
            (0.60, "AI-Generated Content Detected"),  # Above threshold
            (0.70, "AI-Generated Content Detected"),  # Well above threshold
        ]
        
        for confidence, expected in test_cases:
            result = detector._finalize_decision(
                ensemble_result=None,
                validation_result=None,
                detection_scores=[('test_model', confidence, 1.0)],
                processing_time=1.0,
                faces_detected=1
            )
            
            assert result.prediction == expected, f"Confidence {confidence} should predict '{expected}', got '{result.prediction}'"
    
    def test_mode_differentiation(self):
        """Test that different modes produce different results for borderline cases"""
        aggressive = MVPAggressiveDetector2025()
        hybrid = MVPHybridDetector2025()
        conservative = MVPConservativeDetector2025()
        
        # Test borderline confidence that should trigger different classifications
        borderline_confidence = 0.52  # Between aggressive (45%) and conservative (55%)
        
        aggressive_result = aggressive._finalize_decision(
            ensemble_result=None,
            validation_result=None,
            detection_scores=[('test_model', borderline_confidence, 1.0)],
            processing_time=1.0,
            faces_detected=1
        )
        
        hybrid_result = hybrid._finalize_decision(
            ensemble_result=None,
            validation_result=None,
            detection_scores=[('test_model', borderline_confidence, 1.0)],
            processing_time=1.0,
            faces_detected=1
        )
        
        conservative_result = conservative._finalize_decision(
            ensemble_result=None,
            validation_result=None,
            detection_scores=[('test_model', borderline_confidence, 1.0)],
            processing_time=1.0,
            faces_detected=1
        )
        
        # Aggressive should detect as fake (52% > 45%)
        assert aggressive_result.prediction == "AI-Generated Content Detected"
        
        # Hybrid should detect as fake (52% > 50%)
        assert hybrid_result.prediction == "AI-Generated Content Detected"
        
        # Conservative should detect as authentic (52% < 55%)
        assert conservative_result.prediction == "Authentic Video"
        
        # Verify modes are differentiated
        assert aggressive_result.prediction != conservative_result.prediction

if __name__ == "__main__":
    pytest.main([__file__])
