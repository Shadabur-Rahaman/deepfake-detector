"""
Bias Test System 2025 - Comprehensive Bias Detection and Validation
================================================================

This module provides comprehensive testing to ensure the detection system
is not biased toward any particular classification and can properly
distinguish between real and fake content.

Author: AI Assistant
Date: 2025
"""

import numpy as np
import cv2
import torch
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
import random

logger = logging.getLogger(__name__)

@dataclass
class BiasTestResult:
    """Result of bias testing"""
    test_name: str
    passed: bool
    confidence_range: Tuple[float, float]
    prediction_accuracy: float
    bias_detected: bool
    details: Dict[str, Any]
    recommendations: List[str]

class BiasTestType(Enum):
    """Types of bias tests"""
    REAL_CONTENT_BIAS = "real_content_bias"
    FAKE_CONTENT_BIAS = "fake_content_bias"
    CONFIDENCE_BIAS = "confidence_bias"
    THRESHOLD_BIAS = "threshold_bias"
    MODEL_BIAS = "model_bias"

class BiasTestSystem2025:
    """
    Comprehensive bias testing system for deepfake detection.
    
    Features:
    - Real content bias testing
    - Fake content bias testing
    - Confidence distribution analysis
    - Threshold validation
    - Model performance analysis
    """
    
    def __init__(self):
        self.test_results = []
        self.bias_threshold = 0.1  # 10% bias threshold
        
    def run_comprehensive_bias_tests(self) -> List[BiasTestResult]:
        """Run all bias tests and return results"""
        logger.info("🧪 Starting comprehensive bias testing...")
        
        test_results = []
        
        # Test 1: Real content bias test
        test_results.append(self._test_real_content_bias())
        
        # Test 2: Fake content bias test
        test_results.append(self._test_fake_content_bias())
        
        # Test 3: Confidence distribution test
        test_results.append(self._test_confidence_distribution())
        
        # Test 4: Threshold validation test
        test_results.append(self._test_threshold_validation())
        
        # Test 5: Model consistency test
        test_results.append(self._test_model_consistency())
        
        self.test_results = test_results
        
        # Generate summary
        self._generate_bias_summary()
        
        return test_results
    
    def _test_real_content_bias(self) -> BiasTestResult:
        """Test for bias toward classifying everything as real"""
        logger.info("🧪 Testing real content bias...")
        
        # Generate synthetic real-looking content
        test_faces = self._generate_synthetic_real_faces(50)
        
        # Run detection on synthetic real content
        from .ground_truth_validator_2025 import validate_authentic_content
        from .unbiased_scoring_2025 import calculate_unbiased_score
        
        real_predictions = 0
        fake_predictions = 0
        confidences = []
        
        for faces in test_faces:
            # Test ground truth validation
            validation_result = validate_authentic_content(faces)
            
            # Create mock ensemble predictions
            mock_predictions = {
                'model1': ('Real Face', 0.3 + random.uniform(-0.1, 0.1)),
                'model2': ('Real Face', 0.4 + random.uniform(-0.1, 0.1)),
                'model3': ('Real Face', 0.35 + random.uniform(-0.1, 0.1))
            }
            
            # Test unbiased scoring
            scoring_result = calculate_unbiased_score(mock_predictions)
            
            if scoring_result.prediction == 'Real Face':
                real_predictions += 1
            else:
                fake_predictions += 1
            
            confidences.append(scoring_result.confidence)
        
        # Calculate bias metrics
        real_bias = real_predictions / len(test_faces)
        confidence_avg = np.mean(confidences)
        confidence_std = np.std(confidences)
        
        # Determine if bias is detected
        bias_detected = real_bias > (1.0 - self.bias_threshold)
        
        recommendations = []
        if bias_detected:
            recommendations.append("System shows strong bias toward real content classification")
            recommendations.append("Review ground truth validator thresholds")
            recommendations.append("Check confidence calibration settings")
        
        return BiasTestResult(
            test_name="Real Content Bias Test",
            passed=not bias_detected,
            confidence_range=(min(confidences), max(confidences)),
            prediction_accuracy=real_bias,
            bias_detected=bias_detected,
            details={
                'real_predictions': real_predictions,
                'fake_predictions': fake_predictions,
                'confidence_mean': confidence_avg,
                'confidence_std': confidence_std,
                'bias_threshold': self.bias_threshold
            },
            recommendations=recommendations
        )
    
    def _test_fake_content_bias(self) -> BiasTestResult:
        """Test for bias toward classifying everything as fake"""
        logger.info("🧪 Testing fake content bias...")
        
        # Generate synthetic fake-looking content
        test_faces = self._generate_synthetic_fake_faces(50)
        
        # Run detection on synthetic fake content
        from .ground_truth_validator_2025 import validate_authentic_content
        from .unbiased_scoring_2025 import calculate_unbiased_score
        
        real_predictions = 0
        fake_predictions = 0
        confidences = []
        
        for faces in test_faces:
            # Test ground truth validation
            validation_result = validate_authentic_content(faces)
            
            # Create mock ensemble predictions for fake content
            mock_predictions = {
                'model1': ('Deepfake Detected', 0.7 + random.uniform(-0.1, 0.1)),
                'model2': ('Deepfake Detected', 0.8 + random.uniform(-0.1, 0.1)),
                'model3': ('Deepfake Detected', 0.75 + random.uniform(-0.1, 0.1))
            }
            
            # Test unbiased scoring
            scoring_result = calculate_unbiased_score(mock_predictions)
            
            if scoring_result.prediction == 'Real Face':
                real_predictions += 1
            else:
                fake_predictions += 1
            
            confidences.append(scoring_result.confidence)
        
        # Calculate bias metrics
        fake_bias = fake_predictions / len(test_faces)
        confidence_avg = np.mean(confidences)
        confidence_std = np.std(confidences)
        
        # Determine if bias is detected
        bias_detected = fake_bias > (1.0 - self.bias_threshold)
        
        recommendations = []
        if bias_detected:
            recommendations.append("System shows strong bias toward fake content classification")
            recommendations.append("Review ensemble scoring methods")
            recommendations.append("Check model weight distributions")
        
        return BiasTestResult(
            test_name="Fake Content Bias Test",
            passed=not bias_detected,
            confidence_range=(min(confidences), max(confidences)),
            prediction_accuracy=fake_bias,
            bias_detected=bias_detected,
            details={
                'real_predictions': real_predictions,
                'fake_predictions': fake_predictions,
                'confidence_mean': confidence_avg,
                'confidence_std': confidence_std,
                'bias_threshold': self.bias_threshold
            },
            recommendations=recommendations
        )
    
    def _test_confidence_distribution(self) -> BiasTestResult:
        """Test for bias in confidence score distributions"""
        logger.info("🧪 Testing confidence distribution bias...")
        
        # Test with various confidence levels
        test_cases = [
            ('Low Confidence Real', 0.2, 0.3),
            ('Medium Confidence Real', 0.4, 0.5),
            ('High Confidence Real', 0.6, 0.7),
            ('Low Confidence Fake', 0.3, 0.4),
            ('Medium Confidence Fake', 0.5, 0.6),
            ('High Confidence Fake', 0.7, 0.8)
        ]
        
        from .unbiased_scoring_2025 import calculate_unbiased_score
        
        confidence_ranges = []
        prediction_consistency = []
        
        for case_name, min_conf, max_conf in test_cases:
            case_confidences = []
            
            for _ in range(10):  # 10 tests per case
                # Generate mock predictions with specified confidence range
                mock_predictions = {
                    'model1': ('Real Face' if min_conf < 0.5 else 'Deepfake Detected', 
                              min_conf + random.uniform(0, max_conf - min_conf)),
                    'model2': ('Real Face' if min_conf < 0.5 else 'Deepfake Detected', 
                              min_conf + random.uniform(0, max_conf - min_conf)),
                    'model3': ('Real Face' if min_conf < 0.5 else 'Deepfake Detected', 
                              min_conf + random.uniform(0, max_conf - min_conf))
                }
                
                scoring_result = calculate_unbiased_score(mock_predictions)
                case_confidences.append(scoring_result.confidence)
            
            confidence_ranges.append((case_name, min(case_confidences), max(case_confidences)))
            
            # Check if predictions are consistent
            consistency = len(set([c > 0.5 for c in case_confidences])) == 1
            prediction_consistency.append(consistency)
        
        # Analyze confidence distribution
        all_confidences = [conf for _, min_conf, max_conf in confidence_ranges 
                          for _ in range(10) 
                          for conf in [min_conf + random.uniform(0, max_conf - min_conf)]]
        
        confidence_mean = np.mean(all_confidences)
        confidence_std = np.std(all_confidences)
        
        # Check for bias in confidence distribution
        # If most confidences are clustered around 0.3-0.4, there's likely bias
        low_conf_count = sum(1 for c in all_confidences if c < 0.4)
        bias_detected = low_conf_count / len(all_confidences) > 0.8
        
        recommendations = []
        if bias_detected:
            recommendations.append("Confidence scores are biased toward low values")
            recommendations.append("Review confidence calibration methods")
            recommendations.append("Check if system is being overly conservative")
        
        return BiasTestResult(
            test_name="Confidence Distribution Test",
            passed=not bias_detected,
            confidence_range=(min(all_confidences), max(all_confidences)),
            prediction_accuracy=np.mean(prediction_consistency),
            bias_detected=bias_detected,
            details={
                'confidence_mean': confidence_mean,
                'confidence_std': confidence_std,
                'low_confidence_ratio': low_conf_count / len(all_confidences),
                'case_ranges': confidence_ranges,
                'prediction_consistency': prediction_consistency
            },
            recommendations=recommendations
        )
    
    def _test_threshold_validation(self) -> BiasTestResult:
        """Test if thresholds are properly calibrated"""
        logger.info("🧪 Testing threshold validation...")
        
        # Test various confidence levels around typical thresholds
        test_thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        
        from .unbiased_scoring_2025 import calculate_unbiased_score
        
        threshold_performance = {}
        
        for threshold in test_thresholds:
            correct_predictions = 0
            total_predictions = 0
            
            # Test with known real content
            for _ in range(20):
                mock_predictions = {
                    'model1': ('Real Face', threshold - 0.1 + random.uniform(-0.05, 0.05)),
                    'model2': ('Real Face', threshold - 0.05 + random.uniform(-0.05, 0.05)),
                    'model3': ('Real Face', threshold + random.uniform(-0.05, 0.05))
                }
                
                scoring_result = calculate_unbiased_score(mock_predictions)
                
                # Check if prediction is correct (should be Real Face for this test)
                if scoring_result.confidence < threshold and scoring_result.prediction == 'Real Face':
                    correct_predictions += 1
                elif scoring_result.confidence >= threshold and scoring_result.prediction == 'Deepfake Detected':
                    correct_predictions += 1
                
                total_predictions += 1
            
            # Test with known fake content
            for _ in range(20):
                mock_predictions = {
                    'model1': ('Deepfake Detected', threshold + 0.1 + random.uniform(-0.05, 0.05)),
                    'model2': ('Deepfake Detected', threshold + 0.05 + random.uniform(-0.05, 0.05)),
                    'model3': ('Deepfake Detected', threshold + random.uniform(-0.05, 0.05))
                }
                
                scoring_result = calculate_unbiased_score(mock_predictions)
                
                # Check if prediction is correct (should be Deepfake Detected for this test)
                if scoring_result.confidence >= threshold and scoring_result.prediction == 'Deepfake Detected':
                    correct_predictions += 1
                elif scoring_result.confidence < threshold and scoring_result.prediction == 'Real Face':
                    correct_predictions += 1
                
                total_predictions += 1
            
            accuracy = correct_predictions / total_predictions
            threshold_performance[threshold] = accuracy
        
        # Find optimal threshold
        optimal_threshold = max(threshold_performance, key=threshold_performance.get)
        max_accuracy = threshold_performance[optimal_threshold]
        
        # Check if current thresholds are reasonable
        bias_detected = max_accuracy < 0.7  # Less than 70% accuracy indicates bias
        
        recommendations = []
        if bias_detected:
            recommendations.append(f"Threshold performance is poor (max accuracy: {max_accuracy:.2f})")
            recommendations.append(f"Consider using threshold around {optimal_threshold}")
            recommendations.append("Review threshold calibration in detection modes")
        
        return BiasTestResult(
            test_name="Threshold Validation Test",
            passed=not bias_detected,
            confidence_range=(min(threshold_performance.keys()), max(threshold_performance.keys())),
            prediction_accuracy=max_accuracy,
            bias_detected=bias_detected,
            details={
                'threshold_performance': threshold_performance,
                'optimal_threshold': optimal_threshold,
                'max_accuracy': max_accuracy
            },
            recommendations=recommendations
        )
    
    def _test_model_consistency(self) -> BiasTestResult:
        """Test for consistency across different models"""
        logger.info("🧪 Testing model consistency...")
        
        # Test with same input across different model configurations
        test_inputs = [
            ('Real Content', 0.3, 0.4),
            ('Fake Content', 0.6, 0.7),
            ('Uncertain Content', 0.4, 0.6)
        ]
        
        from .unbiased_scoring_2025 import calculate_unbiased_score
        
        consistency_scores = []
        
        for input_type, min_conf, max_conf in test_inputs:
            input_predictions = []
            
            # Test same input with different model weight distributions
            for _ in range(10):
                mock_predictions = {
                    'model1': ('Real Face' if min_conf < 0.5 else 'Deepfake Detected', 
                              min_conf + random.uniform(0, max_conf - min_conf)),
                    'model2': ('Real Face' if min_conf < 0.5 else 'Deepfake Detected', 
                              min_conf + random.uniform(0, max_conf - min_conf)),
                    'model3': ('Real Face' if min_conf < 0.5 else 'Deepfake Detected', 
                              min_conf + random.uniform(0, max_conf - min_conf))
                }
                
                scoring_result = calculate_unbiased_score(mock_predictions)
                input_predictions.append((scoring_result.prediction, scoring_result.confidence))
            
            # Calculate consistency for this input type
            predictions = [pred for pred, conf in input_predictions]
            confidences = [conf for pred, conf in input_predictions]
            
            prediction_consistency = len(set(predictions)) == 1  # All predictions should be same
            confidence_consistency = np.std(confidences) < 0.1  # Low variance in confidence
            
            consistency_scores.append(prediction_consistency and confidence_consistency)
        
        overall_consistency = np.mean(consistency_scores)
        bias_detected = overall_consistency < 0.8  # Less than 80% consistency indicates bias
        
        recommendations = []
        if bias_detected:
            recommendations.append("Model predictions are inconsistent across similar inputs")
            recommendations.append("Review model ensemble weighting")
            recommendations.append("Check for random factors in scoring")
        
        return BiasTestResult(
            test_name="Model Consistency Test",
            passed=not bias_detected,
            confidence_range=(0.0, 1.0),
            prediction_accuracy=overall_consistency,
            bias_detected=bias_detected,
            details={
                'consistency_scores': consistency_scores,
                'overall_consistency': overall_consistency
            },
            recommendations=recommendations
        )
    
    def _generate_synthetic_real_faces(self, count: int) -> List[List[np.ndarray]]:
        """Generate synthetic real-looking face data for testing"""
        faces_list = []
        
        for _ in range(count):
            faces = []
            # Generate 5-10 faces per test case
            num_faces = random.randint(5, 10)
            
            for _ in range(num_faces):
                # Create synthetic face-like image
                face = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
                # Add some structure to make it more face-like
                face[20:44, 20:44] = np.random.randint(100, 200, (24, 24, 3), dtype=np.uint8)
                faces.append(face)
            
            faces_list.append(faces)
        
        return faces_list
    
    def _generate_synthetic_fake_faces(self, count: int) -> List[List[np.ndarray]]:
        """Generate synthetic fake-looking face data for testing"""
        faces_list = []
        
        for _ in range(count):
            faces = []
            # Generate 5-10 faces per test case
            num_faces = random.randint(5, 10)
            
            for _ in range(num_faces):
                # Create synthetic fake-looking image with more uniform patterns
                face = np.random.randint(50, 150, (64, 64, 3), dtype=np.uint8)
                # Add more uniform structure (characteristic of some fake content)
                face[15:49, 15:49] = np.random.randint(80, 120, (34, 34, 3), dtype=np.uint8)
                faces.append(face)
            
            faces_list.append(faces)
        
        return faces_list
    
    def _generate_bias_summary(self):
        """Generate summary of bias test results"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        bias_detected_count = sum(1 for result in self.test_results if result.bias_detected)
        
        logger.info("🧪 Bias Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed Tests: {passed_tests}")
        logger.info(f"   Failed Tests: {total_tests - passed_tests}")
        logger.info(f"   Bias Detected: {bias_detected_count}")
        
        if bias_detected_count > 0:
            logger.warning("⚠️  BIAS DETECTED IN DETECTION SYSTEM!")
            logger.warning("   The following issues were found:")
            
            for result in self.test_results:
                if result.bias_detected:
                    logger.warning(f"   - {result.test_name}")
                    for rec in result.recommendations:
                        logger.warning(f"     • {rec}")
        else:
            logger.info("✅ No significant bias detected in the system")

# Global instance for easy access
bias_test_system_2025 = BiasTestSystem2025()

def run_bias_tests() -> List[BiasTestResult]:
    """Convenience function to run all bias tests"""
    return bias_test_system_2025.run_comprehensive_bias_tests()

def test_system_bias() -> Dict[str, Any]:
    """Quick bias test function"""
    results = run_bias_tests()
    
    summary = {
        'total_tests': len(results),
        'passed_tests': sum(1 for r in results if r.passed),
        'bias_detected': any(r.bias_detected for r in results),
        'test_results': [
            {
                'name': r.test_name,
                'passed': r.passed,
                'bias_detected': r.bias_detected,
                'accuracy': r.prediction_accuracy,
                'recommendations': r.recommendations
            }
            for r in results
        ]
    }
    
    return summary
