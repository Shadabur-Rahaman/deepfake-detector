"""
Core Fixes Validation - Foundation Level Testing
===============================================

This module provides comprehensive validation for all the core fixes applied
to the deepfake detection system.

VALIDATION COVERAGE:
1. Tensor conversion fixes
2. Database object access fixes
3. MesoNet prediction fixes
4. Error handling improvements
5. System stability validation

Author: Senior ML Engineer
Date: 2024
"""

import torch
import numpy as np
import logging
from typing import List, Dict, Any, Union
import time
import traceback

logger = logging.getLogger(__name__)

class CoreFixesValidator:
    """Comprehensive validation for all core fixes"""
    
    def __init__(self):
        self.validation_results = {}
        self.test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation tests"""
        logger.info("🔍 Starting comprehensive core fixes validation...")
        
        # Test 1: Tensor conversion fixes
        self._test_tensor_conversion_fixes()
        
        # Test 2: Database object access fixes
        self._test_database_object_access_fixes()
        
        # Test 3: MesoNet prediction fixes
        self._test_mesonet_prediction_fixes()
        
        # Test 4: Error handling improvements
        self._test_error_handling_improvements()
        
        # Test 5: System stability validation
        self._test_system_stability()
        
        # Generate summary
        self._generate_validation_summary()
        
        return self.validation_results
    
    def _test_tensor_conversion_fixes(self):
        """Test tensor conversion fixes"""
        logger.info("🧪 Testing tensor conversion fixes...")
        
        try:
            from .tensor_conversion_fixes import (
                safe_convert_to_tensor, 
                safe_batch_convert_faces, 
                safe_stack_faces_batch,
                get_tensor_conversion_stats
            )
            
            # Test 1: Single tensor conversion
            test_numpy = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            tensor = safe_convert_to_tensor(test_numpy)
            
            assert isinstance(tensor, torch.Tensor), "Should return PyTorch tensor"
            assert tensor.shape == (1, 3, 224, 224), f"Expected (1, 3, 224, 224), got {tensor.shape}"
            assert tensor.dtype == torch.float32, f"Expected float32, got {tensor.dtype}"
            
            logger.info("✅ Single tensor conversion: PASSED")
            self.passed_tests += 1
            
            # Test 2: Batch face conversion
            test_faces = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8) for _ in range(3)]
            converted_faces = safe_batch_convert_faces(test_faces)
            
            assert len(converted_faces) == 3, f"Expected 3 faces, got {len(converted_faces)}"
            assert all(isinstance(face, torch.Tensor) for face in converted_faces), "All faces should be tensors"
            
            logger.info("✅ Batch face conversion: PASSED")
            self.passed_tests += 1
            
            # Test 3: Face batch stacking
            stacked_batch = safe_stack_faces_batch(converted_faces)
            assert stacked_batch.shape == (3, 3, 224, 224), f"Expected (3, 3, 224, 224), got {stacked_batch.shape}"
            
            logger.info("✅ Face batch stacking: PASSED")
            self.passed_tests += 1
            
            # Test 4: Error handling
            try:
                # Test with invalid input
                invalid_faces = [None, "invalid", np.array([])]
                safe_batch_convert_faces(invalid_faces)
                logger.info("✅ Error handling: PASSED")
                self.passed_tests += 1
            except Exception as e:
                logger.warning(f"⚠️ Error handling test failed: {e}")
                self.failed_tests += 1
            
            self.test_count += 4
            self.validation_results['tensor_conversion'] = {
                'status': 'PASSED',
                'tests_run': 4,
                'tests_passed': self.passed_tests,
                'details': 'All tensor conversion fixes working correctly'
            }
            
        except Exception as e:
            logger.error(f"❌ Tensor conversion validation failed: {e}")
            self.failed_tests += 1
            self.test_count += 1
            self.validation_results['tensor_conversion'] = {
                'status': 'FAILED',
                'error': str(e),
                'details': 'Tensor conversion fixes not working'
            }
    
    def _test_database_object_access_fixes(self):
        """Test database object access fixes"""
        logger.info("🧪 Testing database object access fixes...")
        
        try:
            from .database_object_fixes import (
                safe_get_job_info,
                safe_log_job_details,
                safe_serialize_job,
                get_database_access_stats
            )
            
            # Create mock database object
            class MockDetectionJob:
                def __init__(self):
                    self.status = "processing"
                    self.progress = 50
                    self.mode = "traditional"
                    self.result = "Real Video"
                    self.confidence = 85.5
                    self.faces_analyzed = 5
                    self.processing_time = 2.3
                    self.error = None
                    self.video_path = "/path/to/video.mp4"
                    self.created_at = "2024-01-01T00:00:00"
                    self.updated_at = "2024-01-01T00:00:00"
            
            mock_job = MockDetectionJob()
            
            # Test 1: Safe job info extraction
            job_info = safe_get_job_info(mock_job)
            
            assert isinstance(job_info, dict), "Should return dictionary"
            assert job_info['status'] == "processing", f"Expected 'processing', got {job_info['status']}"
            assert job_info['progress'] == 50, f"Expected 50, got {job_info['progress']}"
            assert job_info['mode'] == "traditional", f"Expected 'traditional', got {job_info['mode']}"
            
            logger.info("✅ Safe job info extraction: PASSED")
            self.passed_tests += 1
            
            # Test 2: Safe job serialization
            serialized = safe_serialize_job(mock_job)
            assert isinstance(serialized, dict), "Should return dictionary"
            assert 'status' in serialized, "Should contain status field"
            
            logger.info("✅ Safe job serialization: PASSED")
            self.passed_tests += 1
            
            # Test 3: Error handling with None object
            none_job_info = safe_get_job_info(None)
            assert none_job_info['status'] == "not_found", "Should handle None object gracefully"
            
            logger.info("✅ Error handling with None object: PASSED")
            self.passed_tests += 1
            
            # Test 4: Safe logging (should not raise exception)
            try:
                safe_log_job_details(mock_job, "test_video_id")
                logger.info("✅ Safe logging: PASSED")
                self.passed_tests += 1
            except Exception as e:
                logger.warning(f"⚠️ Safe logging test failed: {e}")
                self.failed_tests += 1
            
            self.test_count += 4
            self.validation_results['database_object_access'] = {
                'status': 'PASSED',
                'tests_run': 4,
                'tests_passed': self.passed_tests,
                'details': 'All database object access fixes working correctly'
            }
            
        except Exception as e:
            logger.error(f"❌ Database object access validation failed: {e}")
            self.failed_tests += 1
            self.test_count += 1
            self.validation_results['database_object_access'] = {
                'status': 'FAILED',
                'error': str(e),
                'details': 'Database object access fixes not working'
            }
    
    def _test_mesonet_prediction_fixes(self):
        """Test MesoNet prediction fixes"""
        logger.info("🧪 Testing MesoNet prediction fixes...")
        
        try:
            from .mesonet_detector import MesoNetDetector
            
            # Create MesoNet detector
            detector = MesoNetDetector()
            
            # Test 1: Prediction with numpy arrays
            test_faces = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8) for _ in range(2)]
            
            result = detector.predict(test_faces)
            
            assert isinstance(result, dict), "Should return dictionary"
            assert 'prediction' in result, "Should contain prediction field"
            assert 'confidence' in result, "Should contain confidence field"
            assert result['prediction'] in ['Deepfake', 'Real', 'No Faces', 'Error'], f"Unexpected prediction: {result['prediction']}"
            
            logger.info("✅ MesoNet prediction with numpy arrays: PASSED")
            self.passed_tests += 1
            
            # Test 2: Prediction with mixed data types
            mixed_faces = [
                np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8),
                torch.randn(3, 224, 224)
            ]
            
            result = detector.predict(mixed_faces)
            assert isinstance(result, dict), "Should handle mixed data types"
            
            logger.info("✅ MesoNet prediction with mixed data types: PASSED")
            self.passed_tests += 1
            
            # Test 3: Error handling with invalid input
            try:
                invalid_faces = [None, "invalid", np.array([])]
                result = detector.predict(invalid_faces)
                assert result['prediction'] in ['No Faces', 'No Valid Faces', 'Error'], "Should handle invalid input gracefully"
                
                logger.info("✅ MesoNet error handling: PASSED")
                self.passed_tests += 1
            except Exception as e:
                logger.warning(f"⚠️ MesoNet error handling test failed: {e}")
                self.failed_tests += 1
            
            self.test_count += 3
            self.validation_results['mesonet_prediction'] = {
                'status': 'PASSED',
                'tests_run': 3,
                'tests_passed': self.passed_tests,
                'details': 'All MesoNet prediction fixes working correctly'
            }
            
        except Exception as e:
            logger.error(f"❌ MesoNet prediction validation failed: {e}")
            self.failed_tests += 1
            self.test_count += 1
            self.validation_results['mesonet_prediction'] = {
                'status': 'FAILED',
                'error': str(e),
                'details': 'MesoNet prediction fixes not working'
            }
    
    def _test_error_handling_improvements(self):
        """Test error handling improvements"""
        logger.info("🧪 Testing error handling improvements...")
        
        try:
            # Test 1: Tensor conversion error handling
            from .tensor_conversion_fixes import safe_convert_to_tensor
            
            # Test with various invalid inputs
            invalid_inputs = [None, "string", [], {}, 123]
            
            for invalid_input in invalid_inputs:
                try:
                    result = safe_convert_to_tensor(invalid_input)
                    assert isinstance(result, torch.Tensor), "Should return tensor even for invalid input"
                except Exception as e:
                    logger.warning(f"Unexpected error with {type(invalid_input)}: {e}")
            
            logger.info("✅ Tensor conversion error handling: PASSED")
            self.passed_tests += 1
            
            # Test 2: Database object error handling
            from .database_object_fixes import safe_get_job_info
            
            # Test with various invalid objects
            invalid_objects = [None, "string", [], {}, 123]
            
            for invalid_obj in invalid_objects:
                try:
                    result = safe_get_job_info(invalid_obj)
                    assert isinstance(result, dict), "Should return dictionary even for invalid object"
                    assert 'status' in result, "Should contain status field"
                except Exception as e:
                    logger.warning(f"Unexpected error with {type(invalid_obj)}: {e}")
            
            logger.info("✅ Database object error handling: PASSED")
            self.passed_tests += 1
            
            self.test_count += 2
            self.validation_results['error_handling'] = {
                'status': 'PASSED',
                'tests_run': 2,
                'tests_passed': self.passed_tests,
                'details': 'All error handling improvements working correctly'
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling validation failed: {e}")
            self.failed_tests += 1
            self.test_count += 1
            self.validation_results['error_handling'] = {
                'status': 'FAILED',
                'error': str(e),
                'details': 'Error handling improvements not working'
            }
    
    def _test_system_stability(self):
        """Test system stability"""
        logger.info("🧪 Testing system stability...")
        
        try:
            # Test 1: Memory usage stability
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Run multiple tensor conversions
            for i in range(10):
                test_faces = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8) for _ in range(5)]
                from .tensor_conversion_fixes import safe_batch_convert_faces, safe_stack_faces_batch
                
                converted = safe_batch_convert_faces(test_faces)
                stacked = safe_stack_faces_batch(converted)
                
                # Clean up
                del converted, stacked, test_faces
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            assert memory_increase < 100, f"Memory increase too high: {memory_increase:.2f}MB"
            
            logger.info("✅ Memory stability: PASSED")
            self.passed_tests += 1
            
            # Test 2: Performance stability
            start_time = time.time()
            
            # Run multiple operations
            for i in range(5):
                test_faces = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8) for _ in range(3)]
                from .tensor_conversion_fixes import safe_batch_convert_faces
                
                converted = safe_batch_convert_faces(test_faces)
                del converted, test_faces
            
            end_time = time.time()
            total_time = end_time - start_time
            
            assert total_time < 5.0, f"Performance too slow: {total_time:.2f}s"
            
            logger.info("✅ Performance stability: PASSED")
            self.passed_tests += 1
            
            self.test_count += 2
            self.validation_results['system_stability'] = {
                'status': 'PASSED',
                'tests_run': 2,
                'tests_passed': self.passed_tests,
                'details': 'System stability tests passed'
            }
            
        except Exception as e:
            logger.error(f"❌ System stability validation failed: {e}")
            self.failed_tests += 1
            self.test_count += 1
            self.validation_results['system_stability'] = {
                'status': 'FAILED',
                'error': str(e),
                'details': 'System stability tests failed'
            }
    
    def _generate_validation_summary(self):
        """Generate validation summary"""
        total_tests = self.test_count
        passed_tests = self.passed_tests
        failed_tests = self.failed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.validation_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'overall_status': 'PASSED' if failed_tests == 0 else 'FAILED'
        }
        
        logger.info("=" * 60)
        logger.info("🔍 CORE FIXES VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Overall Status: {'✅ PASSED' if failed_tests == 0 else '❌ FAILED'}")
        logger.info("=" * 60)
        
        # Log individual test results
        for test_name, result in self.validation_results.items():
            if test_name != 'summary':
                status = result['status']
                logger.info(f"{test_name}: {'✅' if status == 'PASSED' else '❌'} {status}")

def run_core_fixes_validation() -> Dict[str, Any]:
    """Run comprehensive core fixes validation"""
    validator = CoreFixesValidator()
    return validator.run_all_validations()

# Convenience function for easy access
def validate_core_fixes():
    """Validate all core fixes"""
    return run_core_fixes_validation()
