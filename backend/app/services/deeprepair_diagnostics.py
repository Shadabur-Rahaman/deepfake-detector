# backend/app/services/deeprepair_diagnostics.py
# DeepRepair & Reality Inspector v1.0 - Diagnostic & Reporting System

"""
Comprehensive diagnostic system for runtime error detection and auto-repair monitoring.

Usage:
    from backend.app.services.deeprepair_diagnostics import get_full_diagnostic_report
    
    # Get comprehensive diagnostic report
    report = get_full_diagnostic_report()
    print(report)
"""

import logging
import sys
import torch
import platform
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    try:
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": sys.version,
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else "N/A",
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
            "cpu_count": torch.get_num_threads(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {"error": str(e)}

def get_model_loader_status() -> Dict[str, Any]:
    """Get status of model loader and loaded models"""
    try:
        from .enhanced_model_loader import get_enhanced_loader
        
        loader = get_enhanced_loader()
        
        return {
            "device": str(loader.device),
            "loaded_models": list(loader.models.keys()),
            "model_count": len(loader.models),
            "available_models": list(loader.model_configs.keys()),
            "total_configured_models": len(loader.model_configs),
            "ensemble_weights": {k: v for k, v in loader.ensemble_weights.items()}
        }
    except Exception as e:
        logger.error(f"Failed to get model loader status: {e}")
        return {"error": str(e)}

def get_repair_statistics() -> Dict[str, Any]:
    """Get auto-repair statistics"""
    try:
        from .realtime_repair_monitor import get_repair_monitor
        
        monitor = get_repair_monitor()
        stats = monitor.get_repair_stats()
        issues = monitor.detect_recurring_issues()
        
        return {
            "repair_stats": stats,
            "recurring_issues": issues,
            "health_status": "HEALTHY" if len(issues) == 0 else "WARNING"
        }
    except Exception as e:
        logger.error(f"Failed to get repair statistics: {e}")
        return {"error": str(e)}

def check_model_input_sizes() -> Dict[str, Any]:
    """Verify model input size configurations"""
    try:
        from .enhanced_model_loader import get_enhanced_loader
        
        loader = get_enhanced_loader()
        
        input_sizes = {}
        for model_name, config in loader.model_configs.items():
            input_sizes[model_name] = {
                "input_size": config.get("input_size"),
                "architecture": config.get("architecture"),
                "type": config.get("type")
            }
        
        # Check for mismatches
        mismatches = []
        expected_sizes = {
            "efficientnet_b0": (224, 224),
            "efficientnet_b4": (380, 380),
            "efficientnet_b7": (600, 600),
            "inception_v3": (299, 299),
        }
        
        for model_name, expected_size in expected_sizes.items():
            if model_name in input_sizes:
                actual_size = input_sizes[model_name]["input_size"]
                if actual_size != expected_size:
                    mismatches.append({
                        "model": model_name,
                        "expected": expected_size,
                        "actual": actual_size
                    })
        
        return {
            "input_sizes": input_sizes,
            "mismatches": mismatches,
            "status": "OK" if len(mismatches) == 0 else "MISMATCH_DETECTED"
        }
    except Exception as e:
        logger.error(f"Failed to check model input sizes: {e}")
        return {"error": str(e)}

def run_tensor_preprocessing_test() -> Dict[str, Any]:
    """Run a test of tensor preprocessing pipeline"""
    try:
        import numpy as np
        from .enhanced_model_loader import get_enhanced_loader
        
        loader = get_enhanced_loader()
        
        # Create test face
        test_face = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        
        # Test different input sizes
        test_sizes = [(224, 224), (299, 299), (380, 380)]
        results = {}
        
        for size in test_sizes:
            try:
                tensor = loader.preprocess_face(test_face, input_size=size)
                results[f"{size[0]}x{size[1]}"] = {
                    "success": True,
                    "output_shape": str(tensor.shape),
                    "output_dtype": str(tensor.dtype),
                    "output_device": str(tensor.device),
                    "value_range": f"[{tensor.min().item():.3f}, {tensor.max().item():.3f}]"
                }
            except Exception as e:
                results[f"{size[0]}x{size[1]}"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "test_results": results,
            "status": "OK" if all(r["success"] for r in results.values()) else "ERRORS_DETECTED"
        }
    except Exception as e:
        logger.error(f"Failed to run preprocessing test: {e}")
        return {"error": str(e)}

def get_full_diagnostic_report() -> str:
    """Generate comprehensive diagnostic report"""
    report_lines = [
        "\n" + "="*100,
        "🩺 DeepRepair & Reality Inspector v1.0 - Full Diagnostic Report",
        "="*100,
        ""
    ]
    
    # System Information
    report_lines.append("📋 SYSTEM INFORMATION")
    report_lines.append("-" * 100)
    system_info = get_system_info()
    if "error" not in system_info:
        report_lines.append(f"OS: {system_info['os']} ({system_info['os_version']})")
        report_lines.append(f"Python: {system_info['python_version'].split()[0]}")
        report_lines.append(f"PyTorch: {system_info['pytorch_version']}")
        report_lines.append(f"CUDA Available: {system_info['cuda_available']}")
        if system_info['cuda_available']:
            report_lines.append(f"CUDA Version: {system_info['cuda_version']}")
            report_lines.append(f"GPU: {system_info['cuda_device_name']}")
        report_lines.append(f"CPU Threads: {system_info['cpu_count']}")
    else:
        report_lines.append(f"❌ Error: {system_info['error']}")
    report_lines.append("")
    
    # Model Loader Status
    report_lines.append("🤖 MODEL LOADER STATUS")
    report_lines.append("-" * 100)
    model_status = get_model_loader_status()
    if "error" not in model_status:
        report_lines.append(f"Device: {model_status['device']}")
        report_lines.append(f"Loaded Models: {model_status['model_count']}/{model_status['total_configured_models']}")
        report_lines.append(f"Models: {', '.join(model_status['loaded_models'][:5])}{'...' if len(model_status['loaded_models']) > 5 else ''}")
    else:
        report_lines.append(f"❌ Error: {model_status['error']}")
    report_lines.append("")
    
    # Auto-Repair Statistics
    report_lines.append("🔧 AUTO-REPAIR STATISTICS")
    report_lines.append("-" * 100)
    repair_stats = get_repair_statistics()
    if "error" not in repair_stats:
        stats = repair_stats['repair_stats']
        report_lines.append(f"Total Repairs: {stats['total_repairs']}")
        report_lines.append(f"Runtime: {stats['runtime_seconds']}s")
        report_lines.append(f"Repair Rate: {stats['repairs_per_minute']:.2f} repairs/min")
        report_lines.append(f"Health Status: {repair_stats['health_status']}")
        
        if stats['repair_counts']:
            report_lines.append("\nRepair Breakdown:")
            for repair_type, count in stats['repair_counts'].items():
                if count > 0:
                    report_lines.append(f"  • {repair_type}: {count}")
        
        if repair_stats['recurring_issues']:
            report_lines.append("\n⚠️ Recurring Issues:")
            for issue in repair_stats['recurring_issues']:
                report_lines.append(f"  • {issue}")
    else:
        report_lines.append(f"❌ Error: {repair_stats['error']}")
    report_lines.append("")
    
    # Model Input Size Validation
    report_lines.append("📏 MODEL INPUT SIZE VALIDATION")
    report_lines.append("-" * 100)
    input_size_check = check_model_input_sizes()
    if "error" not in input_size_check:
        report_lines.append(f"Status: {input_size_check['status']}")
        if input_size_check['mismatches']:
            report_lines.append("\n⚠️ Input Size Mismatches Detected:")
            for mismatch in input_size_check['mismatches']:
                report_lines.append(f"  • {mismatch['model']}: expected {mismatch['expected']}, got {mismatch['actual']}")
        else:
            report_lines.append("✅ All model input sizes configured correctly")
    else:
        report_lines.append(f"❌ Error: {input_size_check['error']}")
    report_lines.append("")
    
    # Preprocessing Pipeline Test
    report_lines.append("🧪 PREPROCESSING PIPELINE TEST")
    report_lines.append("-" * 100)
    test_results = run_tensor_preprocessing_test()
    if "error" not in test_results:
        report_lines.append(f"Status: {test_results['status']}")
        report_lines.append("\nTest Results:")
        for size, result in test_results['test_results'].items():
            if result['success']:
                report_lines.append(f"  ✅ {size}: {result['output_shape']} {result['value_range']}")
            else:
                report_lines.append(f"  ❌ {size}: {result['error']}")
    else:
        report_lines.append(f"❌ Error: {test_results['error']}")
    report_lines.append("")
    
    report_lines.append("="*100)
    report_lines.append(f"Report generated at: {datetime.now().isoformat()}")
    report_lines.append("="*100)
    
    return "\n".join(report_lines)

def print_diagnostic_report():
    """Print the full diagnostic report to console"""
    print(get_full_diagnostic_report())

# Auto-run diagnostic on import if DEBUG mode enabled
if __name__ == "__main__":
    print_diagnostic_report()

