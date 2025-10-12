"""
Model Diagnostics - Debugging and Health Check Tools
==================================================

This module provides comprehensive diagnostic tools for debugging model failures
and identifying root causes of ensemble prediction issues.

Features:
- Individual model health checks
- Tensor shape and device validation
- Model output format verification
- Performance benchmarking
- Error stack trace capture
- Batch diagnostic execution
"""

import logging
import time
import traceback
from typing import Dict, List, Optional, Any, Tuple
import torch
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DiagnosticStatus(Enum):
    """Status of diagnostic tests"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"

@dataclass
class ModelDiagnosticResult:
    """Result of a single model diagnostic test"""
    model_name: str
    status: DiagnosticStatus
    test_name: str
    details: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None

@dataclass
class BatchDiagnosticResult:
    """Result of batch diagnostic execution"""
    total_models: int
    passed: int
    failed: int
    warnings: int
    skipped: int
    results: List[ModelDiagnosticResult]
    total_execution_time: float
    summary: str

class ModelDiagnostics:
    """
    Comprehensive model diagnostic system for debugging ensemble failures.
    """
    
    def __init__(self):
        self.dummy_input = self._create_dummy_input()
        self.expected_output_shapes = {
            'efficientnet_b0': (1, 2),
            'custom_finetuned': (1, 1),
            'efficientnet_finetuned': (1, 2),
            'resnet50': (1, 2),
            'densenet121': (1, 2)
        }
    
    def _create_dummy_input(self) -> torch.Tensor:
        """Create a dummy input tensor for testing models"""
        return torch.randn(1, 3, 224, 224)
    
    def run_single_model_diagnostics(self, model, model_name: str, device: str = "cpu") -> ModelDiagnosticResult:
        """
        Run comprehensive diagnostics on a single model.
        
        Args:
            model: The model to test
            model_name: Name of the model
            device: Device to run on ("cpu" or "cuda")
            
        Returns:
            ModelDiagnosticResult with detailed test results
        """
        start_time = time.time()
        details = {}
        error = None
        status = DiagnosticStatus.PASS
        
        try:
            # Test 1: Model device placement
            model_device = str(next(model.parameters()).device)
            details['device'] = model_device
            details['expected_device'] = device
            
            if model_device != device:
                status = DiagnosticStatus.WARNING
                details['device_mismatch'] = f"Model on {model_device}, expected {device}"
            
            # Test 2: Model evaluation mode
            model.eval()
            details['eval_mode'] = True
            
            # Test 3: Input tensor validation
            dummy_input = self.dummy_input.to(device)
            details['input_shape'] = list(dummy_input.shape)
            details['input_dtype'] = str(dummy_input.dtype)
            
            # Test 4: Model forward pass
            with torch.no_grad():
                output = model(dummy_input)
            
            # ✅ ENHANCED OUTPUT VALIDATION: Comprehensive tensor shape and value validation
            if isinstance(output, torch.Tensor):
                details['output_shape'] = list(output.shape)
                details['output_dtype'] = str(output.dtype)
                details['output_range'] = [float(output.min()), float(output.max())]
                
                # ✅ COMPREHENSIVE SHAPE VALIDATION: Check against expected shapes
                expected_shape = self.expected_output_shapes.get(model_name)
                if expected_shape:
                    if output.shape != expected_shape:
                        status = DiagnosticStatus.WARNING
                        details['shape_mismatch'] = f"Expected {expected_shape}, got {output.shape}"
                        
                        # ✅ SHAPE COMPATIBILITY CHECK: Check if shapes are compatible for batch processing
                        if len(output.shape) == len(expected_shape):
                            # Check if only batch dimension differs
                            compatible = True
                            for i in range(1, len(output.shape)):
                                if output.shape[i] != expected_shape[i]:
                                    compatible = False
                                    break
                            if compatible:
                                details['shape_note'] = "Shape mismatch only in batch dimension - may be acceptable"
                            else:
                                status = DiagnosticStatus.FAIL
                                details['shape_error'] = "Incompatible output shape for model architecture"
                        else:
                            status = DiagnosticStatus.FAIL
                            details['shape_error'] = "Output dimension count doesn't match expected"
                
                # ✅ ROBUST VALUE VALIDATION: Check for invalid values
                if torch.isnan(output).any():
                    status = DiagnosticStatus.FAIL
                    details['nan_output'] = "Model output contains NaN values"
                    details['nan_count'] = int(torch.isnan(output).sum().item())
                
                if torch.isinf(output).any():
                    status = DiagnosticStatus.WARNING
                    details['inf_output'] = "Model output contains infinite values"
                    details['inf_count'] = int(torch.isinf(output).sum().item())
                
                # ✅ ADVANCED PROBABILITY VALIDATION: Comprehensive probability checks
                if output.shape[-1] > 1:
                    try:
                        # Test softmax stability
                        probs = torch.softmax(output, dim=-1)
                        prob_sum = probs.sum(dim=-1)
                        details['probability_sum'] = float(prob_sum.mean().item())
                        details['probability_std'] = float(prob_sum.std().item())
                        
                        # Check probability validity
                        if abs(prob_sum.mean().item() - 1.0) > 0.01:
                            status = DiagnosticStatus.WARNING
                            details['invalid_probabilities'] = f"Probabilities sum to {prob_sum.mean().item():.4f}, not 1.0"
                        
                        # Check for extreme probabilities
                        max_prob = probs.max().item()
                        min_prob = probs.min().item()
                        details['max_probability'] = max_prob
                        details['min_probability'] = min_prob
                        
                        if max_prob > 0.999:
                            details['probability_note'] = "Very high confidence prediction (may indicate overfitting)"
                        if min_prob < 1e-6:
                            details['probability_note'] = "Very low probability values (may cause numerical instability)"
                        
                        # Check for uniform predictions (all classes equal)
                        prob_std = probs.std(dim=-1).mean().item()
                        if prob_std < 0.01:
                            status = DiagnosticStatus.WARNING
                            details['uniform_predictions'] = "Model predictions are nearly uniform (low discrimination)"
                            
                    except Exception as prob_error:
                        status = DiagnosticStatus.FAIL
                        details['probability_error'] = f"Probability calculation failed: {prob_error}"
                
                # ✅ TENSOR PROPERTIES VALIDATION: Check tensor metadata
                details['requires_grad'] = output.requires_grad
                details['device'] = str(output.device)
                details['memory_usage'] = f"{output.element_size() * output.nelement() / 1024:.2f} KB"
                
                # ✅ GRADIENT FLOW VALIDATION: Check if gradients are properly flowing
                if output.requires_grad and output.grad_fn is None:
                    status = DiagnosticStatus.WARNING
                    details['gradient_warning'] = "Output requires grad but has no gradient function"
            
            else:
                status = DiagnosticStatus.FAIL
                details['invalid_output_type'] = f"Expected tensor, got {type(output)}"
                
                # ✅ COMPLEX OUTPUT HANDLING: Handle tuple/dict outputs
                if isinstance(output, (tuple, list)):
                    details['output_type'] = f"Tuple/List with {len(output)} elements"
                    details['element_types'] = [type(elem).__name__ for elem in output]
                elif isinstance(output, dict):
                    details['output_type'] = f"Dictionary with keys: {list(output.keys())}"
                else:
                    details['output_type'] = f"Unexpected type: {type(output)}"
            
            # Test 8: Memory usage
            if torch.cuda.is_available() and device == "cuda":
                memory_allocated = torch.cuda.memory_allocated() / 1024**2  # MB
                memory_reserved = torch.cuda.memory_reserved() / 1024**2  # MB
                details['gpu_memory_allocated_mb'] = memory_allocated
                details['gpu_memory_reserved_mb'] = memory_reserved
            
        except Exception as e:
            status = DiagnosticStatus.FAIL
            error = str(e)
            details['exception'] = error
            details['traceback'] = traceback.format_exc()
            logger.exception(f"Model {model_name} diagnostic failed")
        
        execution_time = time.time() - start_time
        details['execution_time'] = execution_time
        
        return ModelDiagnosticResult(
            model_name=model_name,
            status=status,
            test_name="comprehensive_diagnostic",
            details=details,
            execution_time=execution_time,
            error=error
        )
    
    def run_batch_diagnostics(self, models: Dict[str, Any], device: str = "cpu") -> BatchDiagnosticResult:
        """
        Run diagnostics on multiple models in batch.
        
        Args:
            models: Dictionary of {model_name: model} pairs
            device: Device to run on
            
        Returns:
            BatchDiagnosticResult with comprehensive results
        """
        start_time = time.time()
        results = []
        
        logger.info(f"Starting batch diagnostics for {len(models)} models on {device}")
        
        for model_name, model in models.items():
            try:
                result = self.run_single_model_diagnostics(model, model_name, device)
                results.append(result)
                
                status_emoji = {
                    DiagnosticStatus.PASS: "✅",
                    DiagnosticStatus.FAIL: "❌",
                    DiagnosticStatus.WARNING: "⚠️",
                    DiagnosticStatus.SKIP: "⏭️"
                }[result.status]
                
                logger.info(f"{status_emoji} {model_name}: {result.status.value} "
                           f"({result.execution_time:.2f}s)")
                
            except Exception as e:
                logger.error(f"Failed to run diagnostics for {model_name}: {e}")
                results.append(ModelDiagnosticResult(
                    model_name=model_name,
                    status=DiagnosticStatus.FAIL,
                    test_name="batch_diagnostic",
                    details={'error': str(e)},
                    execution_time=0.0,
                    error=str(e)
                ))
        
        # Calculate summary statistics
        total_models = len(results)
        passed = sum(1 for r in results if r.status == DiagnosticStatus.PASS)
        failed = sum(1 for r in results if r.status == DiagnosticStatus.FAIL)
        warnings = sum(1 for r in results if r.status == DiagnosticStatus.WARNING)
        skipped = sum(1 for r in results if r.status == DiagnosticStatus.SKIP)
        
        total_execution_time = time.time() - start_time
        
        # Generate summary
        if failed == 0 and warnings == 0:
            summary = f"All {total_models} models passed diagnostics"
        elif failed == 0:
            summary = f"{passed} passed, {warnings} warnings, {skipped} skipped"
        else:
            summary = f"{passed} passed, {failed} failed, {warnings} warnings, {skipped} skipped"
        
        logger.info(f"Batch diagnostics completed: {summary} ({total_execution_time:.2f}s)")
        
        return BatchDiagnosticResult(
            total_models=total_models,
            passed=passed,
            failed=failed,
            warnings=warnings,
            skipped=skipped,
            results=results,
            total_execution_time=total_execution_time,
            summary=summary
        )
    
    def diagnose_ensemble_failure(self, models: Dict[str, Any], device: str = "cpu") -> Dict[str, Any]:
        """
        Diagnose why ensemble prediction is failing.
        
        Args:
            models: Dictionary of models to test
            device: Device to run on
            
        Returns:
            Dictionary with failure analysis
        """
        logger.info("Starting ensemble failure diagnosis")
        
        batch_result = self.run_batch_diagnostics(models, device)
        
        # Analyze results for common failure patterns
        failure_analysis = {
            'total_models': batch_result.total_models,
            'healthy_models': batch_result.passed,
            'failed_models': batch_result.failed,
            'warning_models': batch_result.warnings,
            'failure_rate': batch_result.failed / batch_result.total_models if batch_result.total_models > 0 else 0,
            'common_issues': [],
            'recommendations': []
        }
        
        # Identify common issues
        issues = []
        for result in batch_result.results:
            if result.status == DiagnosticStatus.FAIL:
                if 'nan_output' in result.details:
                    issues.append('NaN outputs detected')
                if 'invalid_output_type' in result.details:
                    issues.append('Invalid output types')
                if 'shape_mismatch' in result.details:
                    issues.append('Output shape mismatches')
                if 'exception' in result.details:
                    issues.append('Runtime exceptions')
        
        failure_analysis['common_issues'] = list(set(issues))
        
        # Generate recommendations
        recommendations = []
        if failure_analysis['failure_rate'] > 0.5:
            recommendations.append("More than 50% of models are failing - check model loading and device placement")
        if 'NaN outputs' in failure_analysis['common_issues']:
            recommendations.append("Models producing NaN outputs - check for uninitialized weights or invalid inputs")
        if 'Output shape mismatches' in failure_analysis['common_issues']:
            recommendations.append("Output shape mismatches - verify model architecture and input preprocessing")
        if 'Runtime exceptions' in failure_analysis['common_issues']:
            recommendations.append("Runtime exceptions - check model compatibility and CUDA setup")
        
        failure_analysis['recommendations'] = recommendations
        
        logger.info(f"Ensemble failure analysis: {failure_analysis['failure_rate']*100:.1f}% failure rate")
        
        return failure_analysis

# Global diagnostics instance
_diagnostics = None

def get_model_diagnostics() -> ModelDiagnostics:
    """Get the global model diagnostics instance."""
    global _diagnostics
    if _diagnostics is None:
        _diagnostics = ModelDiagnostics()
    return _diagnostics

def run_quick_diagnostics(models: Dict[str, Any], device: str = "cpu") -> Dict[str, Any]:
    """
    Quick diagnostic function for immediate use.
    
    Args:
        models: Dictionary of {model_name: model} pairs
        device: Device to run on
        
    Returns:
        Dictionary with diagnostic summary
    """
    diagnostics = get_model_diagnostics()
    batch_result = diagnostics.run_batch_diagnostics(models, device)
    
    return {
        'summary': batch_result.summary,
        'total_models': batch_result.total_models,
        'passed': batch_result.passed,
        'failed': batch_result.failed,
        'warnings': batch_result.warnings,
        'execution_time': batch_result.total_execution_time,
        'details': [
            {
                'model': r.model_name,
                'status': r.status.value,
                'execution_time': r.execution_time,
                'error': r.error
            }
            for r in batch_result.results
        ]
    }
