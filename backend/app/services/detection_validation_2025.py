"""
Detection Validation 2025 - Comprehensive Testing Suite
=====================================================

This module provides comprehensive validation and testing for the improved
deepfake detection system to ensure it produces realistic confidence scores
and proper distinction between real and fake content.

Features:
- Comprehensive test suite for detection logic
- Confidence score validation
- Bias detection and correction
- Performance benchmarking
- Real vs fake content distinction testing
"""

import numpy as np
import torch
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)

class TestResult(Enum):
    """Test result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"

@dataclass
class ValidationResult:
    """Result of validation test"""
    test_name: str
    status: TestResult
    score: float
    message: str
    details: Dict[str, Any]
    execution_time: float

@dataclass
class ValidationSummary:
    """Summary of validation results"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    overall_score: float
    execution_time: float
    results: List[ValidationResult]

class DetectionValidator2025:
    """
    Comprehensive validation suite for 2025 detection improvements.
    
    Features:
    - Confidence score validation
    - Bias detection and correction
    - Performance benchmarking
    - Real vs fake distinction testing
    """
    
    def __init__(self):
        self.test_results = []
        self.validation_start_time = None
        
    def run_comprehensive_validation(self) -> ValidationSummary:
        """Run comprehensive validation suite"""
        self.validation_start_time = time.time()
        self.test_results = []
        
        logger.info("🧪 Starting comprehensive detection validation...")
        
        # Test 1: Confidence Score Distribution
        self._test_confidence_score_distribution()
        
        # Test 2: Real vs Fake Distinction
        self._test_real_vs_fake_distinction()
        
        # Test 3: Ensemble Calibration
        self._test_ensemble_calibration()
        
        # Test 4: Temporal Consistency
        self._test_temporal_consistency()
        
        # Test 5: Model Agreement Analysis
        self._test_model_agreement()
        
        # Test 6: Bias Detection
        self._test_bias_detection()
        
        # Test 7: Performance Benchmarking
        self._test_performance_benchmarking()
        
        # Test 8: Edge Case Handling
        self._test_edge_case_handling()
        
        # Calculate summary
        summary = self._calculate_validation_summary()
        
        logger.info("✅ Comprehensive validation completed")
        logger.info(f"   📊 Overall Score: {summary.overall_score:.2f}%")
        logger.info(f"   ✅ Passed: {summary.passed_tests}/{summary.total_tests}")
        logger.info(f"   ❌ Failed: {summary.failed_tests}")
        logger.info(f"   ⚠️ Warnings: {summary.warning_tests}")
        
        return summary
    
    def _test_confidence_score_distribution(self):
        """Test confidence score distribution for realistic values"""
        test_name = "Confidence Score Distribution"
        start_time = time.time()
        
        try:
            # Generate synthetic test data
            test_faces = self._generate_synthetic_faces(50)
            
            # Test with different detection modes
            from .deepfake_detector import detector
            
            confidence_scores = []
            
            for face in test_faces:
                try:
                    result, confidence = detector.detect_deepfake([face])
                    confidence_scores.append(confidence)
                except Exception as e:
                    logger.warning(f"Detection failed for test face: {e}")
                    continue
            
            if not confidence_scores:
                self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                    "No confidence scores generated", {}, time.time() - start_time)
                return
            
            # Analyze confidence distribution
            confidence_array = np.array(confidence_scores)
            
            # Check for bias toward 60-70% range
            bias_range_60_70 = np.sum((confidence_array >= 0.6) & (confidence_array <= 0.7))
            bias_percentage = (bias_range_60_70 / len(confidence_array)) * 100
            
            # Check for realistic distribution
            mean_confidence = np.mean(confidence_array)
            std_confidence = np.std(confidence_array)
            min_confidence = np.min(confidence_array)
            max_confidence = np.max(confidence_array)
            
            # Validation criteria
            score = 100.0
            issues = []
            
            # Check for bias toward 60-70% range (should be <30%)
            if bias_percentage > 30:
                score -= 40
                issues.append(f"High bias toward 60-70% range: {bias_percentage:.1f}%")
            
            # Check for realistic mean (should be around 0.5, not stuck at 0.65)
            if abs(mean_confidence - 0.5) > 0.2:
                score -= 30
                issues.append(f"Mean confidence too far from 0.5: {mean_confidence:.3f}")
            
            # Check for sufficient variance (should have reasonable spread)
            if std_confidence < 0.1:
                score -= 20
                issues.append(f"Insufficient variance: {std_confidence:.3f}")
            
            # Check for realistic range (should span reasonable range)
            if max_confidence - min_confidence < 0.3:
                score -= 10
                issues.append(f"Limited confidence range: {max_confidence - min_confidence:.3f}")
            
            status = TestResult.PASS if score >= 70 else TestResult.FAIL
            if score >= 50 and score < 70:
                status = TestResult.WARNING
            
            details = {
                "confidence_distribution": {
                    "mean": float(mean_confidence),
                    "std": float(std_confidence),
                    "min": float(min_confidence),
                    "max": float(max_confidence),
                    "bias_60_70_percentage": float(bias_percentage)
                },
                "issues": issues
            }
            
            message = f"Confidence distribution analysis: mean={mean_confidence:.3f}, std={std_confidence:.3f}"
            if issues:
                message += f", issues: {len(issues)}"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", {}, time.time() - start_time)
    
    def _test_real_vs_fake_distinction(self):
        """Test ability to distinguish between real and fake content"""
        test_name = "Real vs Fake Distinction"
        start_time = time.time()
        
        try:
            # Generate synthetic real and fake faces
            real_faces = self._generate_synthetic_faces(25, face_type="real")
            fake_faces = self._generate_synthetic_faces(25, face_type="fake")
            
            from .deepfake_detector import detector
            
            # Test real faces
            real_results = []
            for face in real_faces:
                try:
                    result, confidence = detector.detect_deepfake([face])
                    real_results.append((result, confidence))
                except Exception as e:
                    logger.warning(f"Detection failed for real face: {e}")
                    continue
            
            # Test fake faces
            fake_results = []
            for face in fake_faces:
                try:
                    result, confidence = detector.detect_deepfake([face])
                    fake_results.append((result, confidence))
                except Exception as e:
                    logger.warning(f"Detection failed for fake face: {e}")
                    continue
            
            if not real_results or not fake_results:
                self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                    "Insufficient test results", {}, time.time() - start_time)
                return
            
            # Analyze distinction capability
            real_confidences = [conf for _, conf in real_results]
            fake_confidences = [conf for _, conf in fake_results]
            
            real_mean = np.mean(real_confidences)
            fake_mean = np.mean(fake_confidences)
            
            # Calculate distinction score
            distinction_score = abs(real_mean - fake_mean)
            
            # Check for proper classification
            real_correct = sum(1 for result, _ in real_results if "Real" in result or "Authentic" in result)
            fake_correct = sum(1 for result, _ in fake_results if "Deepfake" in result or "Fake" in result)
            
            real_accuracy = real_correct / len(real_results) if real_results else 0
            fake_accuracy = fake_correct / len(fake_results) if fake_results else 0
            
            # Overall score calculation
            score = 100.0
            issues = []
            
            # Check distinction capability
            if distinction_score < 0.2:
                score -= 40
                issues.append(f"Poor distinction: {distinction_score:.3f}")
            
            # Check real face accuracy
            if real_accuracy < 0.6:
                score -= 30
                issues.append(f"Low real face accuracy: {real_accuracy:.3f}")
            
            # Check fake face accuracy
            if fake_accuracy < 0.6:
                score -= 30
                issues.append(f"Low fake face accuracy: {fake_accuracy:.3f}")
            
            status = TestResult.PASS if score >= 70 else TestResult.FAIL
            if score >= 50 and score < 70:
                status = TestResult.WARNING
            
            details = {
                "distinction_analysis": {
                    "real_mean_confidence": float(real_mean),
                    "fake_mean_confidence": float(fake_mean),
                    "distinction_score": float(distinction_score),
                    "real_accuracy": float(real_accuracy),
                    "fake_accuracy": float(fake_accuracy)
                },
                "issues": issues
            }
            
            message = f"Distinction analysis: real={real_mean:.3f}, fake={fake_mean:.3f}, distinction={distinction_score:.3f}"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", {}, time.time() - start_time)
    
    def _test_ensemble_calibration(self):
        """Test ensemble calibration effectiveness"""
        test_name = "Ensemble Calibration"
        start_time = time.time()
        
        try:
            from .confidence_calibration_2025 import get_calibration_summary
            
            # Get calibration summary
            calibration_summary = get_calibration_summary()
            
            if "message" in calibration_summary:
                self._add_test_result(test_name, TestResult.SKIP, 0.0, 
                                    "No calibration history available", {}, time.time() - start_time)
                return
            
            # Analyze calibration metrics
            avg_ece = calibration_summary.get("average_ece", 1.0)
            avg_reliability = calibration_summary.get("average_reliability", 0.0)
            
            score = 100.0
            issues = []
            
            # Check ECE (Expected Calibration Error) - lower is better
            if avg_ece > 0.1:
                score -= 40
                issues.append(f"High ECE: {avg_ece:.3f}")
            
            # Check reliability score - higher is better
            if avg_reliability < 0.8:
                score -= 30
                issues.append(f"Low reliability: {avg_reliability:.3f}")
            
            status = TestResult.PASS if score >= 70 else TestResult.FAIL
            if score >= 50 and score < 70:
                status = TestResult.WARNING
            
            details = {
                "calibration_metrics": {
                    "average_ece": float(avg_ece),
                    "average_reliability": float(avg_reliability),
                    "total_calibrations": calibration_summary.get("total_calibrations", 0)
                },
                "issues": issues
            }
            
            message = f"Calibration metrics: ECE={avg_ece:.3f}, Reliability={avg_reliability:.3f}"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", {}, time.time() - start_time)
    
    def _test_temporal_consistency(self):
        """Test temporal consistency in video processing"""
        test_name = "Temporal Consistency"
        start_time = time.time()
        
        try:
            # Generate sequential faces with variations
            sequential_faces = self._generate_sequential_faces(20)
            
            from .modern_preprocessing_2025 import preprocess_faces_modern_2025
            
            # Test preprocessing with temporal smoothing
            result = preprocess_faces_modern_2025(
                sequential_faces,
                apply_quality_filtering=True,
                apply_temporal_smoothing=True
            )
            
            temporal_consistency = result.temporal_consistency
            
            score = 100.0
            issues = []
            
            # Check temporal consistency
            if temporal_consistency < 0.7:
                score -= 40
                issues.append(f"Low temporal consistency: {temporal_consistency:.3f}")
            
            status = TestResult.PASS if score >= 70 else TestResult.FAIL
            if score >= 50 and score < 70:
                status = TestResult.WARNING
            
            details = {
                "temporal_analysis": {
                    "temporal_consistency": float(temporal_consistency),
                    "faces_processed": len(result.processed_faces),
                    "faces_filtered": result.faces_filtered,
                    "preprocessing_time": float(result.preprocessing_time)
                },
                "issues": issues
            }
            
            message = f"Temporal consistency: {temporal_consistency:.3f}"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", {}, time.time() - start_time)
    
    def _test_model_agreement(self):
        """Test model agreement in ensemble predictions"""
        test_name = "Model Agreement"
        start_time = time.time()
        
        try:
            # Generate test faces
            test_faces = self._generate_synthetic_faces(20)
            
            from .unbiased_scoring_2025 import get_scoring_summary
            
            # Get scoring summary
            scoring_summary = get_scoring_summary()
            
            if "message" in scoring_summary:
                self._add_test_result(test_name, TestResult.SKIP, 0.0, 
                                    "No scoring history available", {}, time.time() - start_time)
                return
            
            # Analyze model agreement
            avg_agreement = scoring_summary.get("average_agreement", 0.0)
            avg_uncertainty = scoring_summary.get("average_uncertainty", 1.0)
            
            score = 100.0
            issues = []
            
            # Check model agreement
            if avg_agreement < 0.7:
                score -= 40
                issues.append(f"Low model agreement: {avg_agreement:.3f}")
            
            # Check uncertainty (lower is better for agreement)
            if avg_uncertainty > 0.3:
                score -= 30
                issues.append(f"High uncertainty: {avg_uncertainty:.3f}")
            
            status = TestResult.PASS if score >= 70 else TestResult.FAIL
            if score >= 50 and score < 70:
                status = TestResult.WARNING
            
            details = {
                "agreement_analysis": {
                    "average_agreement": float(avg_agreement),
                    "average_uncertainty": float(avg_uncertainty),
                    "total_scores": scoring_summary.get("total_scores", 0)
                },
                "issues": issues
            }
            
            message = f"Model agreement: {avg_agreement:.3f}, uncertainty: {avg_uncertainty:.3f}"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", {}, time.time() - start_time)
    
    def _test_bias_detection(self):
        """Test for bias detection and correction"""
        test_name = "Bias Detection"
        start_time = time.time()
        
        try:
            # Test with different types of content
            test_cases = [
                ("real_content", self._generate_synthetic_faces(15, face_type="real")),
                ("fake_content", self._generate_synthetic_faces(15, face_type="fake")),
                ("mixed_content", self._generate_synthetic_faces(10, face_type="real") + 
                                self._generate_synthetic_faces(10, face_type="fake"))
            ]
            
            from .deepfake_detector import detector
            
            all_results = []
            
            for case_name, faces in test_cases:
                case_results = []
                for face in faces:
                    try:
                        result, confidence = detector.detect_deepfake([face])
                        case_results.append(confidence)
                    except Exception as e:
                        logger.warning(f"Detection failed for {case_name}: {e}")
                        continue
                
                if case_results:
                    all_results.append((case_name, case_results))
            
            if not all_results:
                self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                    "No test results generated", {}, time.time() - start_time)
                return
            
            # Analyze bias
            bias_scores = []
            for case_name, confidences in all_results:
                mean_conf = np.mean(confidences)
                bias_scores.append((case_name, mean_conf))
            
            # Check for bias toward specific ranges
            score = 100.0
            issues = []
            
            # Check if all cases are stuck in 60-70% range
            stuck_in_range = all(0.6 <= mean_conf <= 0.7 for _, mean_conf in bias_scores)
            if stuck_in_range:
                score -= 50
                issues.append("All cases stuck in 60-70% range")
            
            # Check for reasonable variance across cases
            confidences = [mean_conf for _, mean_conf in bias_scores]
            variance = np.var(confidences)
            if variance < 0.01:
                score -= 30
                issues.append(f"Low variance across cases: {variance:.4f}")
            
            status = TestResult.PASS if score >= 70 else TestResult.FAIL
            if score >= 50 and score < 70:
                status = TestResult.WARNING
            
            details = {
                "bias_analysis": {
                    "case_results": {case_name: float(mean_conf) for case_name, mean_conf in bias_scores},
                    "variance": float(variance),
                    "stuck_in_range": stuck_in_range
                },
                "issues": issues
            }
            
            message = f"Bias analysis: variance={variance:.4f}, stuck_in_range={stuck_in_range}"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", {}, time.time() - start_time)
    
    def _test_performance_benchmarking(self):
        """Test performance and timing"""
        test_name = "Performance Benchmarking"
        start_time = time.time()
        
        try:
            # Generate test faces
            test_faces = self._generate_synthetic_faces(10)
            
            from .deepfake_detector import detector
            
            # Benchmark detection performance
            detection_times = []
            for face in test_faces:
                try:
                    start_time_detection = time.time()
                    result, confidence = detector.detect_deepfake([face])
                    end_time_detection = time.time()
                    
                    detection_times.append(end_time_detection - start_time_detection)
                except Exception as e:
                    logger.warning(f"Detection failed during benchmarking: {e}")
                    continue
            
            if not detection_times:
                self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                    "No detection times recorded", {}, time.time() - start_time)
                return
            
            # Analyze performance
            mean_time = np.mean(detection_times)
            std_time = np.std(detection_times)
            max_time = np.max(detection_times)
            
            score = 100.0
            issues = []
            
            # Check average detection time (should be reasonable)
            if mean_time > 5.0:  # More than 5 seconds is too slow
                score -= 40
                issues.append(f"Slow detection: {mean_time:.2f}s average")
            
            # Check for consistent timing
            if std_time > mean_time * 0.5:  # High variance in timing
                score -= 20
                issues.append(f"Inconsistent timing: std={std_time:.2f}s")
            
            # Check for outliers
            if max_time > mean_time * 3:  # Significant outliers
                score -= 20
                issues.append(f"Timing outliers: max={max_time:.2f}s")
            
            status = TestResult.PASS if score >= 70 else TestResult.FAIL
            if score >= 50 and score < 70:
                status = TestResult.WARNING
            
            details = {
                "performance_analysis": {
                    "mean_detection_time": float(mean_time),
                    "std_detection_time": float(std_time),
                    "max_detection_time": float(max_time),
                    "total_detections": len(detection_times)
                },
                "issues": issues
            }
            
            message = f"Performance: mean={mean_time:.2f}s, std={std_time:.2f}s"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", {}, time.time() - start_time)
    
    def _test_edge_case_handling(self):
        """Test edge case handling"""
        test_name = "Edge Case Handling"
        start_time = time.time()
        
        try:
            from .deepfake_detector import detector
            
            # Test various edge cases
            edge_cases = [
                ("empty_list", []),
                ("single_face", self._generate_synthetic_faces(1)),
                ("many_faces", self._generate_synthetic_faces(50)),
                ("invalid_faces", [None, np.array([]), np.zeros((10, 10, 3))])
            ]
            
            successful_handling = 0
            total_cases = len(edge_cases)
            
            for case_name, faces in edge_cases:
                try:
                    result, confidence = detector.detect_deepfake(faces)
                    successful_handling += 1
                    logger.info(f"Edge case '{case_name}' handled successfully")
                except Exception as e:
                    logger.warning(f"Edge case '{case_name}' failed: {e}")
            
            handling_rate = successful_handling / total_cases
            score = handling_rate * 100
            
            status = TestResult.PASS if score >= 80 else TestResult.FAIL
            if score >= 60 and score < 80:
                status = TestResult.WARNING
            
            details = {
                "edge_case_analysis": {
                    "successful_handling": successful_handling,
                    "total_cases": total_cases,
                    "handling_rate": float(handling_rate)
                }
            }
            
            message = f"Edge case handling: {successful_handling}/{total_cases} ({handling_rate:.1%})"
            
            self._add_test_result(test_name, status, score, message, details, time.time() - start_time)
            
        except Exception as e:
            self._add_test_result(test_name, TestResult.FAIL, 0.0, 
                                f"Test failed with exception: {e}", time.time() - start_time)
    
    def _generate_synthetic_faces(self, count: int, face_type: str = "mixed") -> List[np.ndarray]:
        """Generate synthetic faces for testing"""
        faces = []
        
        for i in range(count):
            # Generate random face-like image
            if face_type == "real":
                # Generate more natural-looking faces
                face = np.random.randint(50, 200, (224, 224, 3), dtype=np.uint8)
                # Add some structure
                face[50:174, 50:174] = np.random.randint(100, 255, (124, 124, 3), dtype=np.uint8)
            elif face_type == "fake":
                # Generate more artificial-looking faces
                face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
                # Add some artificial patterns
                face[::10, :] = 255
                face[:, ::10] = 255
            else:
                # Mixed content
                face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            
            faces.append(face)
        
        return faces
    
    def _generate_sequential_faces(self, count: int) -> List[np.ndarray]:
        """Generate sequential faces with variations for temporal testing"""
        faces = []
        base_face = np.random.randint(100, 200, (224, 224, 3), dtype=np.uint8)
        
        for i in range(count):
            # Add slight variations to base face
            variation = np.random.randint(-20, 20, (224, 224, 3))
            face = np.clip(base_face + variation, 0, 255).astype(np.uint8)
            faces.append(face)
        
        return faces
    
    def _add_test_result(self, test_name: str, status: TestResult, score: float, 
                        message: str, details: Dict[str, Any], execution_time: float):
        """Add test result to results list"""
        result = ValidationResult(
            test_name=test_name,
            status=status,
            score=score,
            message=message,
            details=details,
            execution_time=execution_time
        )
        self.test_results.append(result)
        
        # Log result
        status_emoji = {
            TestResult.PASS: "✅",
            TestResult.FAIL: "❌",
            TestResult.WARNING: "⚠️",
            TestResult.SKIP: "⏭️"
        }
        
        logger.info(f"{status_emoji[status]} {test_name}: {score:.1f}% - {message}")
    
    def _calculate_validation_summary(self) -> ValidationSummary:
        """Calculate validation summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == TestResult.PASS)
        failed_tests = sum(1 for r in self.test_results if r.status == TestResult.FAIL)
        warning_tests = sum(1 for r in self.test_results if r.status == TestResult.WARNING)
        
        overall_score = np.mean([r.score for r in self.test_results]) if self.test_results else 0.0
        execution_time = time.time() - self.validation_start_time if self.validation_start_time else 0.0
        
        return ValidationSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            overall_score=overall_score,
            execution_time=execution_time,
            results=self.test_results
        )
    
    def save_validation_report(self, summary: ValidationSummary, filepath: str):
        """Save validation report to file"""
        try:
            report = {
                "validation_summary": {
                    "total_tests": summary.total_tests,
                    "passed_tests": summary.passed_tests,
                    "failed_tests": summary.failed_tests,
                    "warning_tests": summary.warning_tests,
                    "overall_score": summary.overall_score,
                    "execution_time": summary.execution_time,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "test_results": [
                    {
                        "test_name": result.test_name,
                        "status": result.status.value,
                        "score": result.score,
                        "message": result.message,
                        "details": result.details,
                        "execution_time": result.execution_time
                    }
                    for result in summary.results
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📄 Validation report saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")

# Global validator instance
detection_validator_2025 = DetectionValidator2025()

# Convenience functions
def run_detection_validation() -> ValidationSummary:
    """Run comprehensive detection validation"""
    return detection_validator_2025.run_comprehensive_validation()

def save_validation_report(summary: ValidationSummary, filepath: str = "validation_report_2025.json"):
    """Save validation report to file"""
    detection_validator_2025.save_validation_report(summary, filepath)
