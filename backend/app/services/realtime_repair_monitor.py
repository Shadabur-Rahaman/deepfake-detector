# backend/app/services/realtime_repair_monitor.py
# DeepRepair & Reality Inspector v1.0 - Real-Time Auto-Repair Monitor

import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RepairType(Enum):
    """Types of auto-repairs performed"""
    TENSOR_SHAPE = "tensor_shape"
    NORMALIZATION = "normalization"
    DEVICE_TRANSFER = "device_transfer"
    DTYPE_CONVERSION = "dtype_conversion"
    INPUT_SIZE_MISMATCH = "input_size_mismatch"
    DIMENSION_CORRECTION = "dimension_correction"

@dataclass
class RepairEvent:
    """Record of a single auto-repair event"""
    timestamp: float
    repair_type: RepairType
    original_value: str
    repaired_value: str
    success: bool
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0

class RealtimeRepairMonitor:
    """
    Real-time monitoring and logging of auto-repair events during inference.
    
    Features:
    - Track all auto-repair operations
    - Log repair statistics
    - Detect recurring issues
    - Generate diagnostic reports
    """
    
    def __init__(self):
        self.repair_history: List[RepairEvent] = []
        self.repair_counts: Dict[RepairType, int] = {rt: 0 for rt in RepairType}
        self.total_repairs = 0
        self.start_time = time.time()
    
    def log_repair(
        self, 
        repair_type: RepairType, 
        original: str, 
        repaired: str, 
        success: bool = True,
        error: Optional[str] = None,
        processing_time: float = 0.0
    ):
        """Log a repair event"""
        event = RepairEvent(
            timestamp=time.time(),
            repair_type=repair_type,
            original_value=original,
            repaired_value=repaired,
            success=success,
            error_message=error,
            processing_time_ms=processing_time * 1000
        )
        
        self.repair_history.append(event)
        if success:
            self.repair_counts[repair_type] += 1
            self.total_repairs += 1
        
        # Log to console
        status = "✅" if success else "❌"
        logger.info(f"{status} [AUTO-REPAIR] {repair_type.value.upper()}: {original} → {repaired}")
        if not success and error:
            logger.error(f"   Error: {error}")
    
    def get_repair_stats(self) -> Dict:
        """Get repair statistics"""
        runtime = time.time() - self.start_time
        
        return {
            "total_repairs": self.total_repairs,
            "runtime_seconds": round(runtime, 2),
            "repairs_per_minute": round((self.total_repairs / runtime) * 60, 2) if runtime > 0 else 0,
            "repair_counts": {rt.value: count for rt, count in self.repair_counts.items()},
            "recent_repairs": [
                {
                    "type": event.repair_type.value,
                    "original": event.original_value,
                    "repaired": event.repaired_value,
                    "success": event.success,
                    "time_ms": round(event.processing_time_ms, 2)
                }
                for event in self.repair_history[-10:]  # Last 10 repairs
            ]
        }
    
    def detect_recurring_issues(self) -> List[str]:
        """Detect patterns in repair history"""
        issues = []
        
        # Check if any repair type is happening too frequently
        for repair_type, count in self.repair_counts.items():
            if count > 10:
                issues.append(
                    f"High frequency of {repair_type.value} repairs ({count} times). "
                    f"Consider investigating root cause."
                )
        
        # Check for recent failures
        recent_failures = [e for e in self.repair_history[-20:] if not e.success]
        if len(recent_failures) > 5:
            issues.append(
                f"Multiple repair failures detected ({len(recent_failures)} in last 20 attempts). "
                f"System may require manual intervention."
            )
        
        return issues
    
    def generate_diagnostic_report(self) -> str:
        """Generate a comprehensive diagnostic report"""
        stats = self.get_repair_stats()
        issues = self.detect_recurring_issues()
        
        report = [
            "\n" + "="*80,
            "🩺 DeepRepair & Reality Inspector v1.0 - Diagnostic Report",
            "="*80,
            f"Runtime: {stats['runtime_seconds']}s",
            f"Total Auto-Repairs: {stats['total_repairs']}",
            f"Repair Rate: {stats['repairs_per_minute']:.2f} repairs/min",
            "",
            "📊 Repair Breakdown:",
        ]
        
        for repair_type, count in stats['repair_counts'].items():
            if count > 0:
                percentage = (count / self.total_repairs * 100) if self.total_repairs > 0 else 0
                report.append(f"  • {repair_type}: {count} ({percentage:.1f}%)")
        
        if issues:
            report.append("")
            report.append("⚠️ Detected Issues:")
            for issue in issues:
                report.append(f"  • {issue}")
        else:
            report.append("")
            report.append("✅ No recurring issues detected")
        
        report.append("="*80)
        
        return "\n".join(report)
    
    def reset(self):
        """Reset monitoring state"""
        self.repair_history.clear()
        self.repair_counts = {rt: 0 for rt in RepairType}
        self.total_repairs = 0
        self.start_time = time.time()
        logger.info("🔄 Repair monitor reset")

# Global monitor instance
_global_monitor = RealtimeRepairMonitor()

def get_repair_monitor() -> RealtimeRepairMonitor:
    """Get the global repair monitor instance"""
    return _global_monitor

def log_tensor_shape_repair(original_shape: str, repaired_shape: str, success: bool = True, error: Optional[str] = None):
    """Convenience function for logging tensor shape repairs"""
    _global_monitor.log_repair(
        RepairType.TENSOR_SHAPE,
        original_shape,
        repaired_shape,
        success,
        error
    )

def log_normalization_repair(original_range: str, repaired_range: str, success: bool = True, error: Optional[str] = None):
    """Convenience function for logging normalization repairs"""
    _global_monitor.log_repair(
        RepairType.NORMALIZATION,
        original_range,
        repaired_range,
        success,
        error
    )

def log_device_transfer_repair(original_device: str, repaired_device: str, success: bool = True, error: Optional[str] = None):
    """Convenience function for logging device transfer repairs"""
    _global_monitor.log_repair(
        RepairType.DEVICE_TRANSFER,
        original_device,
        repaired_device,
        success,
        error
    )

def print_diagnostic_report():
    """Print the current diagnostic report"""
    print(_global_monitor.generate_diagnostic_report())

