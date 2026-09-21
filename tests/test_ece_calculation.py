"""
Unit Tests for ECE (Expected Calibration Error) Calculation
==========================================================

Tests the ECE calculation functionality to ensure calibration quality
measurement is accurate and meets the target ECE < 0.1.
"""

import pytest
import numpy as np
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.confidence_calibration_2025 import CalibrationValidator

class TestECECalculation:
    """Test ECE calculation functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = CalibrationValidator(n_bins=10)
    
    def test_perfect_calibration_ece_zero(self):
        """Test ECE calculation with perfectly calibrated predictions"""
        # Perfect calibration: confidence = accuracy
        predictions = np.array([0, 0, 1, 1, 1, 0, 1, 1, 0, 1])
        confidences = np.array([0.2, 0.3, 0.7, 0.8, 0.9, 0.1, 0.6, 0.8, 0.4, 0.7])
        
        results = self.validator.calculate_ece(predictions, confidences)
        
        # ECE should be very low for well-calibrated predictions
        assert results['ece'] < 0.1, f"ECE should be < 0.1 for well-calibrated data, got {results['ece']}"
        assert 'mce' in results, "MCE should be included in results"
        assert 'reliability_score' in results, "Reliability score should be included"
        assert 0 <= results['reliability_score'] <= 1, "Reliability score should be between 0 and 1"
    
    def test_poor_calibration_high_ece(self):
        """Test ECE calculation with poorly calibrated predictions"""
        # Poor calibration: overconfident predictions
        predictions = np.array([0, 0, 1, 1, 0, 0, 1, 0, 0, 1])  # Mostly 0s
        confidences = np.array([0.9, 0.8, 0.9, 0.8, 0.9, 0.8, 0.9, 0.8, 0.9, 0.8])  # High confidence
        
        results = self.validator.calculate_ece(predictions, confidences)
        
        # ECE should be high for poorly calibrated predictions
        assert results['ece'] > 0.2, f"ECE should be > 0.2 for poorly calibrated data, got {results['ece']}"
    
    def test_edge_cases(self):
        """Test ECE calculation with edge cases"""
        # All zeros
        predictions = np.array([0, 0, 0, 0, 0])
        confidences = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        results = self.validator.calculate_ece(predictions, confidences)
        assert 'ece' in results
        assert 0 <= results['ece'] <= 1
        
        # All ones
        predictions = np.array([1, 1, 1, 1, 1])
        confidences = np.array([0.5, 0.6, 0.7, 0.8, 0.9])
        
        results = self.validator.calculate_ece(predictions, confidences)
        assert 'ece' in results
        assert 0 <= results['ece'] <= 1
    
    def test_single_bin_ece(self):
        """Test ECE calculation with single bin (all same confidence)"""
        predictions = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        confidences = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        
        results = self.validator.calculate_ece(predictions, confidences)
        
        # Should handle single bin case gracefully
        assert 'ece' in results
        assert 0 <= results['ece'] <= 1
        assert len(results['bin_metrics']) <= 1, "Should have at most 1 bin"
    
    def test_bin_metrics_structure(self):
        """Test that bin metrics have correct structure"""
        predictions = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        confidences = np.array([0.1, 0.2, 0.7, 0.8, 0.3, 0.9, 0.4, 0.6])
        
        results = self.validator.calculate_ece(predictions, confidences)
        
        # Check bin metrics structure
        assert 'bin_metrics' in results
        assert len(results['bin_metrics']) > 0, "Should have at least one bin"
        
        for bin_metric in results['bin_metrics']:
            required_fields = ['bin_idx', 'bin_range', 'count', 'accuracy', 'avg_confidence', 'calibration_error']
            for field in required_fields:
                assert field in bin_metric, f"Missing field {field} in bin metric"
            
            assert bin_metric['count'] >= 0, "Bin count should be non-negative"
            assert 0 <= bin_metric['accuracy'] <= 1, "Bin accuracy should be between 0 and 1"
            assert 0 <= bin_metric['avg_confidence'] <= 1, "Bin confidence should be between 0 and 1"
    
    def test_reliability_diagram_generation(self):
        """Test reliability diagram data generation"""
        predictions = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        confidences = np.array([0.1, 0.2, 0.7, 0.8, 0.3, 0.9, 0.4, 0.6])
        
        diagram_data = self.validator.generate_reliability_diagram(predictions, confidences)
        
        # Check diagram data structure
        assert 'ece' in diagram_data
        assert 'reliability_diagram_data' in diagram_data
        assert 'perfectly_calibrated_line' in diagram_data
        
        reliability_data = diagram_data['reliability_diagram_data']
        required_fields = ['bin_centers', 'accuracies', 'confidences', 'counts']
        for field in required_fields:
            assert field in reliability_data, f"Missing field {field} in reliability diagram data"
            assert len(reliability_data[field]) > 0, f"Field {field} should not be empty"
    
    def test_input_validation(self):
        """Test input validation for ECE calculation"""
        # Mismatched lengths
        predictions = np.array([0, 1, 0])
        confidences = np.array([0.5, 0.6])  # Different length
        
        with pytest.raises(AssertionError):
            self.validator.calculate_ece(predictions, confidences)
        
        # Invalid confidence values
        predictions = np.array([0, 1, 0])
        confidences = np.array([1.5, -0.1, 0.8])  # Invalid values
        
        with pytest.raises(AssertionError):
            self.validator.calculate_ece(predictions, confidences)
    
    def test_target_ece_threshold(self):
        """Test that ECE calculation can identify well-calibrated models"""
        # Create data that should meet ECE < 0.1 target
        np.random.seed(42)
        n_samples = 1000
        
        # Generate well-calibrated data
        true_probs = np.random.uniform(0.1, 0.9, n_samples)
        predictions = np.random.binomial(1, true_probs)
        confidences = true_probs + np.random.normal(0, 0.05, n_samples)  # Small noise
        confidences = np.clip(confidences, 0.01, 0.99)  # Clamp to valid range
        
        results = self.validator.calculate_ece(predictions, confidences)
        
        # Should meet ECE < 0.1 target for well-calibrated data
        assert results['ece'] < 0.1, f"ECE {results['ece']:.4f} should be < 0.1 for well-calibrated data"
        assert results['reliability_score'] > 0.9, f"Reliability score {results['reliability_score']:.4f} should be > 0.9"

if __name__ == "__main__":
    pytest.main([__file__])
