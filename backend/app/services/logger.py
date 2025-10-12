# backend/app/services/logger.py - Production-Grade Logging Module

import logging
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
import traceback

class ProductionLogger:
    """Production-grade logging with standardized format and structured output"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        # Statistics
        self.stats = {
            'info_count': 0,
            'warning_count': 0,
            'error_count': 0,
            'debug_count': 0
        }
    
    def _setup_handlers(self):
        """Setup console and file handlers with production formatting"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Production formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional structured data"""
        self.stats['info_count'] += 1
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data"""
        self.stats['warning_count'] += 1
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception and structured data"""
        self.stats['error_count'] += 1
        if exception:
            message = f"{message} | Exception: {str(exception)}"
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.error(message)
        
        # Log full traceback for errors
        if exception:
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data"""
        self.stats['debug_count'] += 1
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.debug(message)
    
    def _format_kwargs(self, kwargs: Dict[str, Any]) -> str:
        """Format keyword arguments as structured data"""
        try:
            # Filter out non-serializable values
            filtered_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, (str, int, float, bool, list, dict)):
                    filtered_kwargs[key] = value
                else:
                    filtered_kwargs[key] = str(value)
            
            return json.dumps(filtered_kwargs, separators=(',', ':'))
        except Exception:
            return str(kwargs)
    
    def log_inference_start(self, model_name: str, batch_size: int, device: str):
        """Log inference start with structured data"""
        self.info(
            "Inference started",
            model_name=model_name,
            batch_size=batch_size,
            device=device,
            timestamp=datetime.now().isoformat()
        )
    
    def log_inference_result(self, 
                           model_name: str,
                           prediction: str,
                           confidence: float,
                           raw_probability: float,
                           calibrated_probability: float,
                           processing_time: float,
                           is_uncertain: bool = False):
        """Log inference result with structured data"""
        self.info(
            "Inference completed",
            model_name=model_name,
            prediction=prediction,
            confidence=confidence,
            raw_probability=raw_probability,
            calibrated_probability=calibrated_probability,
            processing_time=processing_time,
            is_uncertain=is_uncertain
        )
    
    def log_preprocessing(self, 
                        input_shape: tuple,
                        output_shape: tuple,
                        tensor_range: tuple,
                        processing_time: float):
        """Log preprocessing with structured data"""
        self.info(
            "Preprocessing completed",
            input_shape=input_shape,
            output_shape=output_shape,
            tensor_range=tensor_range,
            processing_time=processing_time
        )
    
    def log_face_detection(self, 
                          frame_shape: tuple,
                          faces_detected: int,
                          bounding_boxes: list,
                          processing_time: float):
        """Log face detection with structured data"""
        self.info(
            "Face detection completed",
            frame_shape=frame_shape,
            faces_detected=faces_detected,
            bounding_boxes=bounding_boxes,
            processing_time=processing_time
        )
    
    def log_model_loading(self, 
                         model_name: str,
                         success: bool,
                         device: str,
                         loading_time: float,
                         error_message: Optional[str] = None):
        """Log model loading with structured data"""
        if success:
            self.info(
                "Model loaded successfully",
                model_name=model_name,
                device=device,
                loading_time=loading_time
            )
        else:
            self.error(
                "Model loading failed",
                model_name=model_name,
                device=device,
                loading_time=loading_time,
                error_message=error_message
            )
    
    def log_ensemble_result(self, 
                           frame_id: int,
                           model_results: Dict[str, Any],
                           fusion_result: Dict[str, Any],
                           processing_time: float):
        """Log ensemble result with structured data"""
        self.info(
            "Ensemble detection completed",
            frame_id=frame_id,
            model_results=model_results,
            fusion_result=fusion_result,
            processing_time=processing_time
        )
    
    def log_connection_lifecycle(self, 
                                event: str,
                                client_id: Optional[str] = None,
                                reason: Optional[str] = None,
                                duration: Optional[float] = None):
        """Log connection lifecycle events"""
        self.info(
            f"Connection {event}",
            client_id=client_id,
            reason=reason,
            duration=duration,
            timestamp=datetime.now().isoformat()
        )
    
    def log_tensor_validation(self, 
                            tensor_shape: tuple,
                            min_value: float,
                            max_value: float,
                            mean_value: float,
                            std_value: float,
                            is_valid: bool):
        """Log tensor validation with structured data"""
        if is_valid:
            self.debug(
                "Tensor validation passed",
                tensor_shape=tensor_shape,
                min_value=min_value,
                max_value=max_value,
                mean_value=mean_value,
                std_value=std_value
            )
        else:
            self.warning(
                "Tensor validation failed",
                tensor_shape=tensor_shape,
                min_value=min_value,
                max_value=max_value,
                mean_value=mean_value,
                std_value=std_value
            )
    
    def log_deterministic_mode(self, enabled: bool, seed: Optional[int] = None):
        """Log deterministic mode status"""
        self.info(
            f"Deterministic mode {'enabled' if enabled else 'disabled'}",
            enabled=enabled,
            seed=seed,
            timestamp=datetime.now().isoformat()
        )
    
    def log_calibration(self, 
                       raw_probability: float,
                       calibrated_probability: float,
                       temperature: float,
                       model_name: str):
        """Log probability calibration"""
        self.debug(
            "Probability calibration applied",
            raw_probability=raw_probability,
            calibrated_probability=calibrated_probability,
            temperature=temperature,
            model_name=model_name
        )
    
    def log_threshold_decision(self, 
                              probability: float,
                              threshold: float,
                              prediction: str,
                              confidence: float,
                              is_uncertain: bool):
        """Log threshold decision"""
        self.info(
            "Threshold decision applied",
            probability=probability,
            threshold=threshold,
            prediction=prediction,
            confidence=confidence,
            is_uncertain=is_uncertain
        )
    
    def log_model_disagreement(self, 
                              model_probabilities: Dict[str, float],
                              disagreement_threshold: float,
                              models_agree: bool):
        """Log model disagreement detection"""
        if not models_agree:
            self.warning(
                "Model disagreement detected",
                model_probabilities=model_probabilities,
                disagreement_threshold=disagreement_threshold,
                models_agree=models_agree
            )
        else:
            self.debug(
                "Model agreement confirmed",
                model_probabilities=model_probabilities,
                disagreement_threshold=disagreement_threshold,
                models_agree=models_agree
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        return {
            **self.stats,
            'total_logs': sum(self.stats.values()),
            'logger_name': self.logger.name,
            'logger_level': self.logger.level
        }

# Global logger instances
def get_logger(name: str) -> ProductionLogger:
    """Get a production logger instance"""
    return ProductionLogger(name)

# Module-level loggers for different components
preprocessing_logger = get_logger("preprocessing")
inference_logger = get_logger("inference")
ensemble_logger = get_logger("ensemble")
face_detection_logger = get_logger("face_detection")
model_loading_logger = get_logger("model_loading")
connection_logger = get_logger("connection")

# Suppress specific warnings that are expected behavior
def suppress_expected_warnings():
    """Suppress warnings that are expected behavior after fixes"""
    import warnings
    
    # Suppress tensor normalization warnings (fixed in preprocessing)
    warnings.filterwarnings("ignore", message=".*torch.Tensor inputs should be normalized.*")
    warnings.filterwarnings("ignore", message=".*max value is.*")
    warnings.filterwarnings("ignore", message=".*dividing by 255.*")
    
    # Suppress CUDA warnings that are expected
    warnings.filterwarnings("ignore", message=".*Skipping registering GPU devices.*")
    warnings.filterwarnings("ignore", message=".*could not load the CUDA driver.*")
    warnings.filterwarnings("ignore", message=".*Unable to register cuDNN factory.*")
    warnings.filterwarnings("ignore", message=".*Unable to register cuBLAS factory.*")
    warnings.filterwarnings("ignore", message=".*Duplicate PluggableDeviceFactory.*")
    warnings.filterwarnings("ignore", message=".*factory already been registered.*")
    warnings.filterwarnings("ignore", message=".*computation placer already registered.*")
    warnings.filterwarnings("ignore", message=".*duplicate registration.*")
    warnings.filterwarnings("ignore", message=".*Unable to register.*factory.*")
    warnings.filterwarnings("ignore", message=".*cuDNN.*")
    warnings.filterwarnings("ignore", message=".*cuBLAS.*")
    warnings.filterwarnings("ignore", message=".*LooseVersion.*")
    
    # Suppress general warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)

# Initialize warning suppression
suppress_expected_warnings()
