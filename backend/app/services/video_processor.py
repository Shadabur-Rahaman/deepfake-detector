# app/services/video_processor.py - Production Video Processor

import os
from typing import List, Tuple, Union, Any, Dict, Optional
import logging
import sys
import time
import asyncio
import functools
import warnings

# ✅ STARTUP OPTIMIZATION: Use centralized import cache instead of redundant imports
try:
    from .import_manager import get_cached_imports
    import_cache = get_cached_imports()
    
    # Get cached imports
    torch = import_cache['torch']
    cv2 = import_cache['cv2']
    np = import_cache['numpy']
    
    # Fallback direct imports if cache fails
    if np is None:
        import numpy as np
    
    print("[OK] LooseVersion compatibility fix applied in video_processor")
    
except ImportError:
    # Fallback imports if cache not available
    import cv2
    import numpy as np
    import torch
    print("[INFO] Using fallback imports in video_processor")

# Try to import scikit-image for advanced texture analysis
try:
    from skimage.feature import local_binary_pattern
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("[WARNING] scikit-image not available. Install with: pip install scikit-image")

# Import face data validator for type conversion
try:
    from .face_data_validator import FaceDataValidator
    FACE_VALIDATOR_AVAILABLE = True
except ImportError:
    FACE_VALIDATOR_AVAILABLE = False
    print("[WARNING] FaceDataValidator not available")

# Monkey patch PyTorch warnings (with improved error handling)
try:
    import torch
    if hasattr(torch, '_C') and hasattr(torch._C, '_log_api_usage'):
        original_warn = torch._C._log_api_usage._warn
        def suppress_tensor_warnings(*args, **kwargs):
            if len(args) > 0 and isinstance(args[0], str):
                if "torch.Tensor inputs should be normalized" in args[0]:
                    return
                if "max value is" in args[0]:
                    return
                if "Dividing input by 255" in args[0]:
                    return
                if "should be normalized 0.0-1.0" in args[0]:
                    return
                if "but max value is" in args[0]:
                    return
                if "⚠️" in args[0] and "torch.Tensor" in args[0]:
                    return
            return original_warn(*args, **kwargs)
        torch._C._log_api_usage._warn = suppress_tensor_warnings
        print("PyTorch warning suppression applied successfully")
    else:
        print("PyTorch internal logging API not available, using alternative suppression")
        # Use alternative suppression methods
        if hasattr(torch, 'set_warn_always'):
            torch.set_warn_always(False)
except (ImportError, AttributeError, Exception) as e:
    # PyTorch version doesn't support this monkey patching, skip it
    print(f"PyTorch warning suppression not available: {e}")
    pass

# Suppress all torch tensor normalization warnings
warnings.filterwarnings("ignore", message=".*torch.Tensor inputs should be normalized.*")
warnings.filterwarnings("ignore", message=".*max value is.*")
warnings.filterwarnings("ignore", message=".*Dividing input by 255.*")
warnings.filterwarnings("ignore", message=".*dividing by 255.*")
warnings.filterwarnings("ignore", message=".*WARNING.*torch.Tensor.*")
warnings.filterwarnings("ignore", message=".*should be normalized 0.0-1.0.*")
warnings.filterwarnings("ignore", message=".*but max value is.*")
warnings.filterwarnings("ignore", message=".*⚠️.*torch.Tensor.*")
warnings.filterwarnings("ignore", message=".*WARNING ⚠️.*")
warnings.filterwarnings("ignore", message=".*torch.Tensor.*normalized.*")
warnings.filterwarnings("ignore", message=".*Dividing input by 255.*")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*normalized 0.0-1.0.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=UserWarning, module="torchvision")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.functional")
warnings.filterwarnings("ignore", category=UserWarning, module="ultralytics")
warnings.filterwarnings("ignore", category=UserWarning, module="yolo")
warnings.filterwarnings("ignore", category=UserWarning, module="torchvision.transforms")

# Set environment variables to suppress PyTorch warnings
os.environ.setdefault("PYTORCH_WARN_LEVEL", "0")
os.environ.setdefault("TORCH_WARN_LEVEL", "0")

# Suppress PyTorch warnings at the logging level
import logging
torch_logger = logging.getLogger("torch")
torch_logger.setLevel(logging.ERROR)

# Alternative approach: Suppress warnings using torch's built-in methods
try:
    import torch
    # Set torch to not show warnings
    torch.set_warn_always(False)
except (ImportError, AttributeError):
    pass

# Context manager to suppress warnings during tensor operations
class SuppressWarnings:
    def __enter__(self):
        warnings.filterwarnings("ignore", message=".*torch.Tensor inputs should be normalized.*")
        warnings.filterwarnings("ignore", message=".*max value is.*")
        warnings.filterwarnings("ignore", message=".*Dividing input by 255.*")
        return self
    
    def __exit__(self, *args):
        pass

# Override Python's warning system to catch and suppress torch warnings
import warnings
original_showwarning = warnings.showwarning
def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    if isinstance(message, str):
        if "torch.Tensor inputs should be normalized" in message:
            return
        if "max value is" in message:
            return
        if "Dividing input by 255" in message:
            return
        if "WARNING" in message and "torch.Tensor" in message:
            return
        if "normalized 0.0-1.0" in message:
            return
        if "should be normalized 0.0-1.0" in message:
            return
        if "but max value is" in message:
            return
        if "⚠️" in message and "torch.Tensor" in message:
            return
        if "WARNING ⚠️" in message:
            return
        if "torch.Tensor" in message and "normalized" in message:
            return
        if "dividing by 255" in message:
            return
        if "max value is" in message and "Dividing input by 255" in message:
            return
    return original_showwarning(message, category, filename, lineno, file, line)
warnings.showwarning = custom_showwarning

# Additional warning suppression for PyTorch transforms
warnings.filterwarnings("ignore", message=".*UserWarning.*")
warnings.filterwarnings("ignore", message=".*FutureWarning.*")
warnings.filterwarnings("ignore", message=".*DeprecationWarning.*")
warnings.filterwarnings("ignore", message=".*RuntimeWarning.*")

logger = logging.getLogger(__name__)

# ==================== FIX MTCNN LOOSEVERSION COMPATIBILITY ====================
try:
    from packaging.version import Version
    import sys
    import types
    import re
    
    class LooseVersion:
        """Complete LooseVersion compatibility class for MTCNN"""
        def __init__(self, vstring=None):
            self.version = []
            self.vstring = vstring
            if vstring:
                self.parse(vstring)
        
        def parse(self, vstring):
            """Parse version string into components"""
            self.vstring = vstring
            # Split version string into components
            components = re.split(r'[.-]', vstring)
            self.version = []
            for component in components:
                # Try to convert to int, fallback to string
                try:
                    self.version.append(int(component))
                except ValueError:
                    self.version.append(component)
        
        def __str__(self):
            return self.vstring
        
        def __repr__(self):
            return f"LooseVersion('{self.vstring}')"
        
        def __cmp__(self, other):
            """Compare with another version"""
            if isinstance(other, str):
                other = LooseVersion(other)
            elif not isinstance(other, LooseVersion):
                return NotImplemented
            
            # Compare version components
            for i in range(max(len(self.version), len(other.version))):
                a = self.version[i] if i < len(self.version) else 0
                b = other.version[i] if i < len(other.version) else 0
                
                # Handle mixed types
                if isinstance(a, int) and isinstance(b, str):
                    a = str(a)
                elif isinstance(a, str) and isinstance(b, int):
                    b = str(b)
                
                if a < b:
                    return -1
                elif a > b:
                    return 1
            return 0
        
        def __lt__(self, other):
            return self.__cmp__(other) < 0
        
        def __le__(self, other):
            return self.__cmp__(other) <= 0
        
        def __eq__(self, other):
            return self.__cmp__(other) == 0
        
        def __ne__(self, other):
            return self.__cmp__(other) != 0
        
        def __ge__(self, other):
            return self.__cmp__(other) >= 0
        
        def __gt__(self, other):
            return self.__cmp__(other) > 0
    
    # Create mock distutils module
    if 'distutils' not in sys.modules:
        mock_distutils = types.ModuleType('distutils')
        sys.modules['distutils'] = mock_distutils
    
    # Create mock distutils.version module
    mock_distutils_version = types.ModuleType('distutils.version')
    mock_distutils_version.LooseVersion = LooseVersion
    
    # Add it to sys.modules so imports work
    if 'distutils.version' not in sys.modules:
        sys.modules['distutils.version'] = mock_distutils_version
    
    logger.info("[OK] LooseVersion compatibility fix applied in video_processor")
except ImportError:
    logger.warning("[WARNING] packaging not available, LooseVersion fix skipped")
except Exception as e:
    logger.warning(f"[WARNING] LooseVersion fix failed: {e}")

# Compatibility implementation for to_thread (Python 3.11+ feature)
# This MUST be defined at module level to be available globally
try:
    # Try to use the built-in to_thread from asyncio (Python 3.11+)
    from asyncio import to_thread
    logger.debug("[OK] Using built-in asyncio.to_thread")
except ImportError:
    # Fallback implementation for earlier Python versions
    logger.debug("[WARNING] Creating compatibility to_thread implementation")
    async def to_thread(func, *args, **kwargs):
        """Compatibility implementation of asyncio.to_thread for Python < 3.11"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop is running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        def sync_wrapper():
            return func(*args, **kwargs)
        
        return await loop.run_in_executor(None, sync_wrapper)

# Ensure to_thread is available in the module's global namespace
globals()['to_thread'] = to_thread

# Also make it available as a module-level function
__all__ = ['extract_faces_from_video', 'to_thread']

# **ENABLED** - MTCNN enabled for better face detection
try:
    from services.mtcnn_python313_fix import MTCNN_Python313_Fix
    MTCNN_DETECTOR = MTCNN_Python313_Fix()
    MTCNN_AVAILABLE = MTCNN_DETECTOR.available if MTCNN_DETECTOR else False
    if MTCNN_AVAILABLE:
        print("✅ MTCNN enabled for face detection")
    else:
        print("⚠️ MTCNN not available - using YOLOv8 and OpenCV fallbacks")
except Exception as e:
    MTCNN_AVAILABLE = False
    MTCNN_DETECTOR = None
    print(f"⚠️ MTCNN failed to load: {e} - using YOLOv8 and OpenCV fallbacks")

# Enhanced YOLO availability check using centralized import management
try:
    from .import_manager import safe_import_yolo, IMPORT_STATUS
    YOLO = safe_import_yolo()
    YOLO_AVAILABLE = YOLO is not None
    if YOLO_AVAILABLE:
        print("[OK] YOLOv8 available for face detection")
    else:
        print("[WARNING] YOLOv8 not available")
except ImportError:
    # Fallback YOLO import
    try:
        from ultralytics import YOLO
        YOLO_AVAILABLE = True
        print("[OK] YOLOv8 available for face detection (fallback)")
    except ImportError:
        YOLO = None
        YOLO_AVAILABLE = False
        print("[WARNING] YOLOv8 not available")

MODEL_INPUT_SIZE = (224, 224)
YOLO_FACE_MODEL_PATH = "yolov8n-face.pt"  # path to YOLOv8 face weights

def get_safe_device():
    """✅ ENHANCED: Get a safe device for inference with comprehensive error handling and fallback"""
    try:
        # ✅ STEP 1: Use CUDA Safety Manager if available (preferred method)
        try:
            from .cuda_safety_manager import get_safe_device as cuda_safe_device
            safe_device = cuda_safe_device()
            logger.info(f"[OK] Using CUDA Safety Manager device: {safe_device}")
            return safe_device
        except ImportError:
            logger.debug("CUDA Safety Manager not available, using fallback")
        
        # ✅ STEP 2: Try to get device from global configuration if available
        try:
            # Try to import from main if available
            import sys
            if 'main' in sys.modules:
                from ..main import GLOBAL_DEVICE
                logger.info(f"[OK] Using global device configuration: {GLOBAL_DEVICE}")
                return GLOBAL_DEVICE
        except Exception as import_error:
            logger.debug(f"Global device import failed: {import_error}")
            pass
        
        # ✅ STEP 2: Enhanced local device detection with comprehensive testing
        if torch.cuda.is_available():
            # Test CUDA device with enhanced safety validation
            try:
                # ✅ CUDA ENVIRONMENT SETUP: Set proper environment variables
                os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'
                os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
                os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
                
                # ✅ PYTORCH CONFIGURATION: Configure for optimal CUDA performance
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                
                # ✅ CUDA DEVICE VALIDATION: Test multiple CUDA operations
                device_count = torch.cuda.device_count()
                if device_count == 0:
                    raise RuntimeError("No CUDA devices available")
                
                logger.info(f"[CUDA] Found {device_count} CUDA device(s)")
                
                # Test tensor operations on each available device
                for device_id in range(device_count):
                    try:
                        device_name = f"cuda:{device_id}"
                        
                        # Test basic tensor creation and operations (smaller tensors)
                        test_tensor = torch.tensor([1.0], device=device_name)
                        result = test_tensor * 2
                        del test_tensor, result
                        
                        # Test memory allocation (smaller size)
                        memory_tensor = torch.randn(100, 100, device=device_name)
                        del memory_tensor
                        
                        # Test CUDA memory management
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()
                        
                        logger.info(f"[CUDA] Device {device_id} ({torch.cuda.get_device_name(device_id)}) working correctly")
                        
                        # Return the first working device
                        return device_name
                        
                    except Exception as device_error:
                        error_msg = str(device_error)
                        if "INTERNAL ASSERT FAILED" in error_msg:
                            logger.warning(f"[CUDA] Device {device_id} failed with driver error: {error_msg}")
                        else:
                            logger.warning(f"[CUDA] Device {device_id} failed: {error_msg}")
                        continue
                
                # If no devices worked, fall back to CPU
                raise RuntimeError("All CUDA devices failed validation")
                
            except Exception as cuda_error:
                logger.warning(f"[CUDA] CUDA test failed: {cuda_error}, falling back to CPU")
                # Clean up any CUDA state
                try:
                    torch.cuda.empty_cache()
                except:
                    pass
                return "cpu"
        else:
            logger.info("[OK] CUDA not available, using CPU")
            return "cpu"
            
    except Exception as e:
        logger.warning(f"[ERROR] Device detection failed: {e}, using CPU fallback")
        # Emergency cleanup
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
        return "cpu"

class FaceExtractor:
    """Multi-tier detector: YOLOv8 → MTCNN → OpenCV Haar cascade with enhanced error handling."""
    def __init__(self, yolo_model_path: Optional[str] = YOLO_FACE_MODEL_PATH):
        self.yolo_model = None
        self.detector = None
        self.face_cascade = None
        self._detection_counts = {'yolo': 0, 'mtcnn': 0, 'haar': 0}
        self._last_log_time = 0
        self._log_interval = 5.0  # Log detection stats every 5 seconds
        self._yolo_failure_count = 0
        self._max_yolo_failures = 3  # Disable YOLO after 3 consecutive failures

        # YOLOv8 (face) - Try to download if not exists, with fallback to general model
        if YOLO_AVAILABLE:
            try:
                # ✅ CRITICAL FIX: Clear CUDA cache before loading YOLOv8
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    # Check available GPU memory
                    allocated = torch.cuda.memory_allocated() / (1024**3)
                    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    free_memory = total_memory - allocated
                    
                    # If less than 500MB free, force CPU
                    if free_memory < 0.5:
                        logger.warning(f"⚠️ GPU memory low ({free_memory:.2f}GB free), using CPU for YOLOv8")
                        device = "cpu"
                    else:
                        device = get_safe_device()
                        # Double-check device is still safe
                        if device != "cpu" and torch.cuda.is_available():
                            # Check again after getting device
                            allocated = torch.cuda.memory_allocated() / (1024**3)
                            free_memory = total_memory - allocated
                            if free_memory < 0.5:
                                logger.warning(f"⚠️ GPU memory dropped below threshold, forcing CPU")
                                device = "cpu"
                else:
                    device = "cpu"
                
                logger.info(f"[FIX] Using device: {device}")
                
                # Try face-specific model first, then fallback to general model
                if yolo_model_path and os.path.exists(yolo_model_path):
                    # Check file size to ensure it's not corrupted
                    file_size = os.path.getsize(yolo_model_path)
                    if file_size < 1000000:  # Less than 1MB, likely corrupted
                        logger.warning(f"YOLOv8 face model file too small ({file_size} bytes), likely corrupted")
                        raise Exception("Model file corrupted")
                    
                    # Initialize YOLO with explicit device and proper configuration
                    try:
                        self.yolo_model = YOLO(yolo_model_path)
                        # ✅ CRITICAL FIX: Try to load on target device, fallback to CPU on OOM
                        try:
                            if device != "cpu":
                                self.yolo_model.to(device)
                                logger.info(f"✅ YOLOv8 loaded on {device} (FP32)")
                            else:
                                self.yolo_model.to("cpu")
                                logger.info(f"✅ YOLOv8 loaded on CPU")
                        except RuntimeError as oom_error:
                            if "CUDA" in str(oom_error) or "memory" in str(oom_error).lower():
                                logger.warning(f"⚠️ CUDA OOM loading YOLOv8: {oom_error}")
                                logger.warning("⚠️ Falling back to CPU for YOLOv8")
                                device = "cpu"
                                torch.cuda.empty_cache()
                                self.yolo_model.to("cpu")
                                logger.info(f"✅ YOLOv8 loaded on CPU (fallback)")
                            else:
                                raise oom_error
                    except Exception as load_error:
                        logger.warning(f"⚠️ YOLOv8 face model loading failed: {load_error}")
                        raise load_error
                else:
                    # Fallback to general YOLOv8 model if face model not available
                    logger.warning(f"YOLOv8 face model not found at {yolo_model_path}, using general YOLOv8 model")
                    try:
                        self.yolo_model = YOLO('yolov8n.pt')  # Use general YOLOv8 model as fallback
                        
                        # ✅ CRITICAL FIX: Try target device first, fallback to CPU on OOM
                        try:
                            if device != "cpu":
                                self.yolo_model.to(device)
                                logger.info(f"✅ YOLOv8 general model loaded on {device} (FP32)")
                            else:
                                self.yolo_model.to("cpu")
                                logger.info(f"✅ YOLOv8 general model loaded on CPU")
                        except RuntimeError as oom_error:
                            if "CUDA" in str(oom_error) or "memory" in str(oom_error).lower():
                                logger.warning(f"⚠️ CUDA OOM loading YOLOv8: {oom_error}")
                                logger.warning("⚠️ Falling back to CPU for YOLOv8")
                                device = "cpu"
                                torch.cuda.empty_cache()
                                self.yolo_model.to("cpu")
                                logger.info(f"✅ YOLOv8 general model loaded on CPU (fallback)")
                            else:
                                raise oom_error
                    except Exception as general_error:
                        logger.warning(f"⚠️ General YOLOv8 model loading failed: {general_error}")
                        # Try CPU as last resort
                        try:
                            device = "cpu"
                            torch.cuda.empty_cache()
                            self.yolo_model = YOLO('yolov8n.pt')
                            self.yolo_model.to("cpu")
                            logger.info(f"✅ YOLOv8 loaded on CPU (last resort)")
                        except Exception as cpu_error:
                            logger.error(f"❌ YOLOv8 failed to load even on CPU: {cpu_error}")
                            raise cpu_error
                
                # Additional fallback if model loading failed
                if self.yolo_model is None:
                    # Try to auto-download
                    try:
                        device = "cpu"  # Use CPU as safest option
                        torch.cuda.empty_cache()
                        self.yolo_model = YOLO('yolov8n.pt')  # Use general model as fallback
                        self.yolo_model.to("cpu")
                        logger.info(f"✅ YOLOv8 general model loaded as fallback on CPU")
                    except Exception as download_error:
                        logger.warning(f"YOLOv8 auto-download failed: {download_error}")
                        raise download_error
            except Exception as e:
                logger.warning(f"YOLOv8 model failed to load: {e}")
                self.yolo_model = None
                # Clear cache on failure
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        # MTCNN with Python 3.13 compatibility
        if MTCNN_AVAILABLE and self.yolo_model is None:
            try:
                # Use the safe MTCNN wrapper
                self.detector = MTCNN_DETECTOR
                if self.detector and self.detector.available:
                    logger.info("MTCNN initialized as primary detector (Python 3.13 compatible)")
                else:
                    logger.warning("MTCNN wrapper not available")
                    self.detector = None
            except Exception as e:
                logger.warning(f"MTCNN init failed: {e}")
                self.detector = None
        
        # Ensure we have at least one detector
        if self.yolo_model is None and self.detector is None:
            logger.warning("[WARNING] No face detection models available, using OpenCV Haar cascade only")

        # OpenCV Haar
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                self.face_cascade = None
                logger.warning("OpenCV Haar cascade not loaded")
            else:
                logger.info("OpenCV Haar cascade loaded as backup")
        except Exception as e:
            logger.error(f"OpenCV cascade init failed: {e}")
            self.face_cascade = None

        if not any([self.yolo_model, self.detector, self.face_cascade]):
            raise RuntimeError("No face detection method available")

        # Validate device configuration
        self._validate_device_configuration()

    def _validate_device_configuration(self):
        """Validate and log device configuration for debugging"""
        logger.info("[FIX] FaceExtractor device configuration:")
        
        if self.yolo_model:
            try:
                # Get YOLO model device info
                if hasattr(self.yolo_model, 'device'):
                    logger.info(f"  YOLOv8 device: {self.yolo_model.device}")
                else:
                    logger.info("  YOLOv8 device: Not explicitly set")
                
                # Test YOLO model with a small input
                test_input = torch.randn(1, 3, 640, 640)
                try:
                    with torch.no_grad():
                        _ = self.yolo_model(test_input, verbose=False)
                    logger.info("  YOLOv8 test: [OK] Working")
                except Exception as test_error:
                    logger.warning(f"  YOLOv8 test: [ERROR] Failed - {test_error}")
                    
            except Exception as e:
                logger.warning(f"  YOLOv8 device validation failed: {e}")
        
        if self.detector:
            logger.info("  MTCNN: [OK] Available")
        
        if self.face_cascade:
            logger.info("  OpenCV Haar: [OK] Available")
        
        logger.info(f"  Total detectors: {sum([1 for x in [self.yolo_model, self.detector, self.face_cascade] if x is not None])}")

    def _force_yolo_cpu_mode(self):
        """Force YOLOv8 to use CPU mode to avoid device errors"""
        if self.yolo_model:
            try:
                logger.info("[LOADING] Forcing YOLOv8 to CPU mode to avoid device errors")
                self.yolo_model.to("cpu")
                
                # Test CPU inference
                test_input = torch.randn(1, 3, 640, 640)
                with torch.no_grad():
                    _ = self.yolo_model(test_input, verbose=False, device="cpu")
                
                logger.info("[OK] YOLOv8 CPU mode activated successfully")
                self._yolo_failure_count = 0  # Reset failure count
                return True
            except Exception as e:
                logger.warning(f"YOLOv8 CPU mode activation failed: {e}")
                return False
        return False

    def _should_log_detection(self) -> bool:
        """Throttle detection logging to reduce spam"""
        current_time = time.time()
        if current_time - self._last_log_time > self._log_interval:
            self._last_log_time = current_time
            return True
        return False
    
    def _is_face_quality_good(self, face_img: np.ndarray) -> bool:
        """Check if face image has acceptable quality for deepfake detection"""
        try:
            if face_img is None or face_img.size == 0:
                logger.debug("Face quality check: FAILED - Empty or None face image")
                return False
            
            # Check minimum dimensions (extremely lenient for better detection)
            height, width = face_img.shape[0], face_img.shape[1]
            if height < 30 or width < 30:
                logger.debug(f"Face quality check: FAILED - Size too small ({width}x{height}) - minimum 30x30")
                return False
            
            # Check for sufficient contrast (not too dark or too bright) - extremely lenient
            gray = cv2.cvtColor(face_img, cv2.COLOR_RGB2GRAY) if len(face_img.shape) == 3 else face_img
            mean_brightness = np.mean(gray)
            if mean_brightness < 10 or mean_brightness > 250:  # Extremely lenient brightness range
                logger.debug(f"Face quality check: FAILED - Brightness out of range ({mean_brightness:.1f}) - range 10-250")
                return False
            
            # Check for sufficient contrast (standard deviation) - extremely lenient
            contrast = np.std(gray)
            if contrast < 3:  # Very low contrast requirement
                logger.debug(f"Face quality check: FAILED - Low contrast ({contrast:.1f}) - minimum 3")
                return False
            
            # Check for blur (Laplacian variance) - extremely lenient
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 5:  # Very low blur requirement
                logger.debug(f"Face quality check: FAILED - Too blurry ({laplacian_var:.1f}) - minimum 5")
                return False
            
            logger.debug(f"Face quality check: PASSED - Size: {width}x{height}, Brightness: {mean_brightness:.1f}, Contrast: {contrast:.1f}, Blur: {laplacian_var:.1f}")
            return True
            
        except Exception as e:
            logger.warning(f"Face quality check failed: {e}")
            # Return True on error to avoid rejecting faces due to quality check failures
            return True

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, np.ndarray]]:
        faces = []
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            logger.error("Empty or invalid frame for detection")
            return faces

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 1) YOLOv8 (prioritized) - with enhanced error handling
        if self.yolo_model is not None and self._yolo_failure_count < self._max_yolo_failures:
            try:
                # Force CPU inference if we've had device issues
                device = "cpu" if self._yolo_failure_count > 0 else None
                
                # Use device-specific inference with proper error handling
                try:
                    if device:
                        results = self.yolo_model(rgb, verbose=False, device=device)
                    else:
                        # Get current device from model
                        current_device = getattr(self.yolo_model, 'device', 'cpu')
                        results = self.yolo_model(rgb, verbose=False, device=current_device)
                    
                    if results and len(results) > 0:
                        boxes = results[0].boxes
                        if boxes is not None and len(boxes) > 0:
                            # Handle both face-specific and general YOLO models
                            xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, 'cpu') else boxes.xyxy.numpy()
                            conf = boxes.conf.cpu().numpy() if hasattr(boxes.conf, 'cpu') else boxes.conf.numpy()
                            
                            # For general YOLO, filter for person class (0) if available
                            if hasattr(boxes, 'cls'):
                                cls = boxes.cls.cpu().numpy() if hasattr(boxes.cls, 'cpu') else boxes.cls.numpy()
                                # For face-specific model, all detections are faces
                                # For general model, we'll take all high-confidence detections as potential faces
                                face_indices = range(len(xyxy))
                            else:
                                face_indices = range(len(xyxy))
                            
                            for i in face_indices:
                                if conf[i] > 0.4:  # ✅ FIXED: Lower threshold to detect more faces
                                    x1, y1, x2, y2 = map(int, xyxy[i])
                                    w, h = x2 - x1, y2 - y1
                                    
                                    # ✅ FIXED: More strict face size requirements for quality
                                    if (x1 >= 0 and y1 >= 0 and 
                                        x2 <= rgb.shape[1] and y2 <= rgb.shape[0] and
                                        w > 80 and h > 80):  # Increased minimum face size for better quality
                                        
                                        face_img = rgb[y1:y2, x1:x2]
                                        
                                        # ✅ FIXED: Accept all detected faces (quality check disabled)
                                        faces.append((x1, y1, w, h, face_img))
                                        
                                        if self._should_log_detection():
                                            self._detection_counts['yolo'] += 1
                                            logger.info(f"YOLOv8 detected face {self._detection_counts['yolo']}: {w}x{h} @ ({x1},{y1})")
                            
                            # Reset failure count on success
                            self._yolo_failure_count = 0
                            
                except Exception as inference_error:
                    error_str = str(inference_error)
                    # Check if it's a CUDA OOM error or memory issue
                    is_cuda_oom = ("CUDA" in error_str and ("out of memory" in error_str.lower() or "OOM" in error_str)) or "memory" in error_str.lower()
                    
                    if is_cuda_oom:
                        logger.warning(f"YOLOv8 GPU OOM: {inference_error}")
                        logger.info("[LOADING] CUDA inference failed, forcing CPU mode")
                        # Clear GPU cache before switching
                        try:
                            import torch
                            if torch.cuda.is_available():
                                torch.cuda.empty_cache()
                        except:
                            pass
                        
                        if self._force_yolo_cpu_mode():
                            # Retry with CPU
                            try:
                                results = self.yolo_model(rgb, verbose=False, device="cpu")
                                if results and len(results) > 0:
                                    boxes = results[0].boxes
                                    if boxes is not None and len(boxes) > 0:
                                        # Process boxes (same logic as above)
                                        xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, 'cpu') else boxes.xyxy.numpy()
                                        conf = boxes.conf.cpu().numpy() if hasattr(boxes.conf, 'cpu') else boxes.conf.numpy()
                                        for i in range(len(xyxy)):
                                            if conf[i] > 0.4:
                                                x1, y1, x2, y2 = map(int, xyxy[i])
                                                w, h = x2 - x1, y2 - y1
                                                if (x1 >= 0 and y1 >= 0 and 
                                                    x2 <= rgb.shape[1] and y2 <= rgb.shape[0] and
                                                    w > 80 and h > 80):
                                                    face_img = rgb[y1:y2, x1:x2]
                                                    faces.append((x1, y1, w, h, face_img))
                                self._yolo_failure_count = 0  # Reset on success
                            except Exception as cpu_error:
                                logger.warning(f"CPU inference also failed: {cpu_error}")
                                self._yolo_failure_count += 1
                        else:
                            self._yolo_failure_count += 1
                    elif "CUDA" in error_str or "NMS" in error_str:
                        logger.warning(f"YOLOv8 inference failed: {inference_error}")
                        logger.info("[LOADING] CUDA inference failed, forcing CPU mode")
                        if self._force_yolo_cpu_mode():
                            self._yolo_failure_count = 0  # Reset on successful CPU mode
                        else:
                            self._yolo_failure_count += 1
                    else:
                        logger.warning(f"YOLOv8 inference failed: {inference_error}")
                        self._yolo_failure_count += 1
                        
            except Exception as e:
                logger.warning(f"YOLOv8 detection failed: {e}")
                self._yolo_failure_count += 1

        # 2) MTCNN (fallback) - Python 3.13 compatible
        if not faces and self.detector is not None and hasattr(self.detector, 'available') and self.detector.available:
            try:
                results = self.detector.detect_faces(rgb)
                if results:
                    for result in results:
                        if result['confidence'] > 0.90:  # High confidence for MTCNN
                            box = result['box']
                            x, y, w, h = max(0, box[0]), max(0, box[1]), box[2], box[3]
                            
                            # Validate coordinates
                            if (x + w <= rgb.shape[1] and y + h <= rgb.shape[0] and
                                w > 20 and h > 20):  # Minimum face size
                                
                                face_img = rgb[y:y+h, x:x+w]
                                faces.append((x, y, w, h, face_img))
                                
                                if self._should_log_detection():
                                    self._detection_counts['mtcnn'] += 1
                                    logger.info(f"MTCNN detected face {self._detection_counts['mtcnn']}: {w}x{h} @ ({x},{y})")
            except Exception as e:
                logger.warning(f"MTCNN detection failed: {e}")
                # MTCNN wrapper handles compatibility issues internally
                pass

        # 3) OpenCV Haar cascade (final fallback)
        if not faces and self.face_cascade is not None:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detected = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.02,  # ✅ FIXED: More sensitive scaling
                    minNeighbors=2,    # ✅ FIXED: Lower neighbor requirement
                    minSize=(80, 80),  # ✅ FIXED: Larger minimum size for quality
                    maxSize=(400, 400) # ✅ FIXED: Larger maximum size
                )
                
                for (x, y, w, h) in detected:
                    # Validate coordinates
                    if (x >= 0 and y >= 0 and 
                        x + w <= rgb.shape[1] and y + h <= rgb.shape[0]):
                        
                        face_img = rgb[y:y+h, x:x+w]
                        
                        # ✅ FIXED: Accept all detected faces (quality check disabled)
                        faces.append((x, y, w, h, face_img))
                        
                        if self._should_log_detection():
                            self._detection_counts['haar'] += 1
                            logger.info(f"OpenCV Haar detected face {self._detection_counts['haar']}: {w}x{h} @ ({x},{y})")
            except Exception as e:
                logger.error(f"OpenCV Haar detection failed: {e}")

        # Add face detection summary logging
        yolo_count = self._detection_counts.get('yolo', 0)
        mtcnn_count = self._detection_counts.get('mtcnn', 0)
        haar_count = self._detection_counts.get('haar', 0)
        total_detected = yolo_count + mtcnn_count + haar_count
        
        logger.info(f"Face detection summary - Total detected: {len(faces)}, "
                   f"YOLOv8: {yolo_count}, MTCNN: {mtcnn_count}, Haar: {haar_count}")

        return faces

def safe_normalize_tensor(tensor, target_range=(0.0, 1.0)):
    """Safely normalize tensor to target range without warnings"""
    try:
        # Convert to float32 if needed
        if tensor.dtype != torch.float32:
            tensor = tensor.float()
        
        # Get current range
        current_min = tensor.min().item()
        current_max = tensor.max().item()
        
        # If already in target range, return as is
        if current_min >= target_range[0] and current_max <= target_range[1]:
            return tensor
        
        # Normalize to [0, 1] if values are in [0, 255] range
        if current_max > 1.0 and current_max <= 255.0:
            tensor = tensor / 255.0
        elif current_max > 255.0:
            # If values are way out of range, clamp to [0, 1]
            tensor = torch.clamp(tensor, 0.0, 1.0)
        elif current_max <= 1.0 and current_min >= 0.0:
            # Already in [0, 1] range
            pass
        else:
            # General normalization
            tensor = (tensor - current_min) / (current_max - current_min)
        
        # Final clamp to ensure values are in target range
        tensor = torch.clamp(tensor, target_range[0], target_range[1])
        
        return tensor
    except Exception as e:
        logger.warning(f"Tensor normalization failed: {e}, using fallback")
        return torch.clamp(tensor, 0.0, 1.0)

def ultra_safe_tensor_normalization(tensor):
    """Ultra-safe tensor normalization that completely prevents warnings"""
    try:
        # Ensure tensor is float32
        if tensor.dtype != torch.float32:
            tensor = tensor.float()
        
        # Get current range
        current_min = tensor.min().item()
        current_max = tensor.max().item()
        
        # Handle different input ranges
        if current_max <= 1.0 and current_min >= 0.0:
            # Already normalized
            return tensor
        elif current_max <= 255.0 and current_min >= 0.0:
            # Standard [0, 255] range - normalize to [0, 1]
            tensor = tensor / 255.0
        else:
            # Out of range values - clamp and normalize
            tensor = torch.clamp(tensor, 0.0, 255.0)
            tensor = tensor / 255.0
        
        # Final safety check with additional validation
        tensor = torch.clamp(tensor, 0.0, 1.0)
        
        # Double-check to prevent any warnings
        if tensor.max() > 1.0 or tensor.min() < 0.0:
            tensor = torch.clamp(tensor, 0.0, 1.0)
        
        return tensor
    except Exception as e:
        # Ultimate fallback - create a safe tensor
        logger.warning(f"Ultra-safe normalization failed: {e}, using safe fallback")
        return torch.clamp(tensor, 0.0, 1.0)

def preprocess_face_crop(face_crop, target_size: Tuple[int, int] = MODEL_INPUT_SIZE):
    """Fixed preprocessing with proper input validation and error handling"""
    try:
        # [OK] Check if the face image exists
        if face_crop is None:
            raise ValueError("[ERROR] preprocess_face_crop: Got None instead of image data")

        # [OK] If input is a PyTorch tensor, convert to NumPy
        if not isinstance(face_crop, np.ndarray):
            try:
                if hasattr(face_crop, 'cpu'):
                    face_crop = face_crop.cpu().numpy()
                else:
                    face_crop = np.array(face_crop)
            except Exception:
                raise TypeError("[ERROR] preprocess_face_crop: Input must be a NumPy array or convertible")

        # [OK] Ensure it's a proper image (H, W, C)
        if face_crop.ndim != 3 or face_crop.shape[2] not in [1, 3]:
            raise ValueError(f"[ERROR] preprocess_face_crop: Unexpected face shape {face_crop.shape}")

        # [OK] Ensure data is uint8 before OpenCV ops
        if face_crop.dtype != np.uint8:
            face_crop = np.clip(face_crop, 0, 255).astype(np.uint8)

        # [OK] Convert RGB → BGR if needed (OpenCV expects BGR)
        if face_crop.shape[2] == 3:
            # Check if it's already BGR by looking at channel order
            # If red channel has higher values than blue, it's likely RGB
            if np.mean(face_crop[:, :, 0]) > np.mean(face_crop[:, :, 2]):
                face_crop = cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR)

        # 🔍 Debug logging
        logger.info(f"🔍 Face dtype={face_crop.dtype}, shape={face_crop.shape}, type={type(face_crop)}")
        
        # [OK] Now safely resize with better interpolation for quality
        face_resized = cv2.resize(face_crop, target_size, interpolation=cv2.INTER_CUBIC)
        
        # [FIX] Proper normalization: ensure values are in [0, 1] range
        # Convert to float32 first to avoid overflow
        arr = face_resized.astype(np.float32)
        
        # Check current range and normalize accordingly
        current_max = np.max(arr)
        current_min = np.min(arr)
        
        # Force normalization to [0, 1] range
        if current_max > 1.0:
            if current_max <= 255.0:
                # Standard [0, 255] to [0, 1] normalization
                arr = arr / 255.0
            else:
                # If max > 255, clamp to [0, 1] range
                arr = np.clip(arr, 0.0, 1.0)
        
        # Ensure minimum value is 0
        if current_min < 0.0:
            arr = np.clip(arr, 0.0, 1.0)
        
        # Final verification - force to [0, 1] if still not correct
        arr = np.clip(arr, 0.0, 1.0)
        
        # Transpose to CHW format
        arr = np.transpose(arr, (2, 0, 1))  # HWC to CHW
        
        if torch is not None:
            t = torch.from_numpy(arr).float()
            # Use ultra-safe normalization to completely prevent warnings
            t = ultra_safe_tensor_normalization(t)
            
            # Apply ImageNet normalization with proper device and dtype
            mean = torch.tensor([0.485, 0.456, 0.406], device=t.device, dtype=t.dtype).view(3,1,1)
            std = torch.tensor([0.229, 0.224, 0.225], device=t.device, dtype=t.dtype).view(3,1,1)
            
            # Ensure tensors have compatible shapes for broadcasting
            if t.dim() == 3:  # (C, H, W)
                normalized = (t - mean) / std
            elif t.dim() == 4:  # (B, C, H, W)
                mean = mean.unsqueeze(0)  # (1, 3, 1, 1)
                std = std.unsqueeze(0)    # (1, 3, 1, 1)
                normalized = (t - mean) / std
            else:
                logger.error(f"Unexpected tensor dimensions: {t.shape}")
                raise ValueError(f"Unexpected tensor dimensions: {t.shape}")
            return normalized
        else:
            mean = np.array([0.485, 0.456, 0.406]).reshape((3,1,1))
            std = np.array([0.229, 0.224, 0.225]).reshape((3,1,1))
            normalized = (arr - mean) / std
            return normalized
    except Exception as e:
        logger.error(f"[ERROR] preprocess_face_crop failed: {e}")
        raise ValueError(f"Failed to preprocess face crop: {e}")

def extract_faces_from_video_sync(video_path: str, frames_to_process: int = 15, frame_interval: int = 30, video_id: str = None, base_progress: int = 0) -> Tuple[List, Dict]:
    start_time = time.time()
    last_progress_update = time.time()
    
    if not os.path.exists(video_path): 
        raise FileNotFoundError(video_path)
    
    logger.info(f"Starting face extraction from: {os.path.basename(video_path)}")
    
    face_extractor = FaceExtractor(YOLO_FACE_MODEL_PATH)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened(): 
        raise IOError(f"Could not open video: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    extracted = []
    frame_count = 0
    processed_count = 0
    frames_with_faces = 0
    
    # Progress update helper function
    def update_progress_if_needed():
        nonlocal last_progress_update
        if video_id and (time.time() - last_progress_update > 3.0 or processed_count == frames_to_process):
            progress_range = 20  # Face extraction takes 20% of total progress
            current_progress = base_progress + int((processed_count / frames_to_process) * progress_range)
            stage_details = f"Extracting faces from video frames... ({processed_count}/{frames_to_process})"
            
            # Import here to avoid circular imports
            try:
                from ..main import update_detection_progress
                update_detection_progress(video_id, current_progress, stage_details, "face_extraction")
            except ImportError:
                pass  # Skip progress update if main module not available
            
            last_progress_update = time.time()
    
    while processed_count < frames_to_process and frame_count < total_frames:
        ret, frame = cap.read()
        if not ret: 
            break
            
        # ✅ FIXED: Process more frames for better face detection
        if frame_count % (frame_interval // 2) == 0:  # Process every 15 frames instead of 30
            faces = face_extractor.detect_faces(frame)
            if faces: 
                frames_with_faces += 1
                
            # ✅ FIXED: Process multiple faces per frame
            for (x, y, w, h, rgb_crop) in faces:
                if processed_count >= frames_to_process: 
                    break
                try:
                    pre = preprocess_face_crop(rgb_crop)
                    
                    # FIXED: Use FaceDataValidator to ensure proper numpy array format
                    if FACE_VALIDATOR_AVAILABLE:
                        validated_face = FaceDataValidator.validate_and_convert(pre, f"video_face_{processed_count}")
                        if validated_face is not None:
                            extracted.append(validated_face)
                            processed_count += 1
                        else:
                            logger.warning(f"Face validation failed for face {processed_count}")
                    else:
                        # Fallback: ensure it's a numpy array
                        if isinstance(pre, np.ndarray):
                            extracted.append(pre)
                            processed_count += 1
                        else:
                            logger.warning(f"Face is not numpy array: {type(pre)}")
                    
                    # Update progress every 3 seconds or when complete
                    update_progress_if_needed()
                    
                except Exception as e:
                    logger.debug(f"Failed to preprocess face: {e}")
        frame_count += 1
    
    cap.release()
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    timing_info = {
        'processing_time': round(processing_time, 2),
        'video_duration': round(duration, 2),
        'processing_speed': round(duration / processing_time, 2) if processing_time > 0 else 0,
        'frames_per_second_processed': round(frame_count / processing_time, 2) if processing_time > 0 else 0
    }
    
    logger.info(f"Face extraction completed in {processing_time:.2f}s - "
               f"Found {processed_count} faces in {frames_with_faces} frames")
    
    return extracted, timing_info

def extract_scene_frames_sync(video_path: str, max_frames: int = 8) -> Tuple[List[np.ndarray], Dict]:
    start_time = time.time()
    
    if not os.path.exists(video_path): 
        return [], {'processing_time': 0, 'frames_extracted': 0}
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): 
        return [], {'processing_time': 0, 'frames_extracted': 0}
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total_frames // max_frames)
    frames = []
    count = 0
    extracted = 0
    
    while extracted < max_frames and count < total_frames:
        ret, frame = cap.read()
        if not ret: 
            break
        if count % interval == 0:
            frame_resized = cv2.resize(frame, (512, 512))
            frames.append(frame_resized)
            extracted += 1
        count += 1
    
    cap.release()
    
    processing_time = time.time() - start_time
    timing_info = {
        'processing_time': round(processing_time, 2),
        'frames_extracted': extracted,
        'total_frames': total_frames
    }
    
    return frames, timing_info

def analyze_frame_transitions_sync(video_path: str, max_frames_to_analyze: int = 20) -> Dict:
    start_time = time.time()
    
    if not os.path.exists(video_path): 
        return {'processing_time': 0}
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): 
        return {'processing_time': 0}
    
    transitions = []
    prev_frame = None
    frame_count = 0
    
    while frame_count < max_frames_to_analyze:
        ret, frame = cap.read()
        if not ret: 
            break
            
        if prev_frame is not None:
            try:
                diff = cv2.absdiff(prev_frame, frame)
                transition_magnitude = float(np.mean(diff))
                gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners = cv2.goodFeaturesToTrack(gray_prev, maxCorners=50, qualityLevel=0.01, minDistance=7)
                flow_magnitude = 0.0
                
                if corners is not None and len(corners) > 0:
                    lk_params = dict(winSize=(15, 15), maxLevel=2, 
                                   criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
                    next_pts, status, error = cv2.calcOpticalFlowPyrLK(gray_prev, gray_curr, corners, None, **lk_params)
                    if next_pts is not None and len(next_pts) > 0:
                        vectors = next_pts - corners
                        flow_magnitude = float(np.mean(np.linalg.norm(vectors, axis=2)))
                
                transitions.append({
                    'frame_index': frame_count,
                    'transition_magnitude': transition_magnitude,
                    'flow_magnitude': flow_magnitude,
                })
            except Exception as e:
                logger.debug(f"Temporal analysis error on frame {frame_count}: {e}")
                
        prev_frame = frame.copy()
        frame_count += 1
    
    cap.release()
    
    processing_time = time.time() - start_time
    
    if transitions:
        mags = [t['transition_magnitude'] for t in transitions]
        flows = [t['flow_magnitude'] for t in transitions]
        return {
            'transitions': transitions,
            'avg_transition_magnitude': float(np.mean(mags)),
            'transition_variance': float(np.var(mags)),
            'avg_flow_magnitude': float(np.mean(flows)),
            'flow_variance': float(np.var(flows)),
            'frames_analyzed': len(transitions),
            'processing_time': round(processing_time, 2),
        }
    
    return {'processing_time': round(processing_time, 2)}

def compute_frequency_features_sync(video_path: str, max_frames: int = 5) -> Dict:
    start_time = time.time()
    
    if not os.path.exists(video_path): 
        return {'processing_time': 0}
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): 
        return {'processing_time': 0}
    
    features = []
    frame_count = 0
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret: 
            break
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fft = np.fft.fft2(gray)
            fft_shifted = np.fft.fftshift(fft)
            mag = np.abs(fft_shifted)
            h, w = mag.shape
            h_start, h_end = h // 4, 3 * h // 4
            w_start, w_end = w // 4, 3 * w // 4
            high = float(np.sum(mag[h_start:h_end, w_start:w_end]))
            total = float(np.sum(mag))
            ratio = high / total if total > 0 else 0.0
            features.append({
                'frame_index': frame_count, 
                'high_freq_energy': high, 
                'total_energy': total, 
                'high_freq_ratio': ratio
            })
        except Exception as e:
            logger.debug(f"Frequency analysis error on frame {frame_count}: {e}")
        frame_count += 1
    
    cap.release()
    
    processing_time = time.time() - start_time
    
    if features:
        ratios = [f['high_freq_ratio'] for f in features]
        return {
            'features': features, 
            'avg_high_freq_ratio': float(np.mean(ratios)), 
            'high_freq_variance': float(np.var(ratios)), 
            'frames_analyzed': len(features),
            'processing_time': round(processing_time, 2)
        }
    
    return {'processing_time': round(processing_time, 2)}

def analyze_scene_for_ai_generation_sync(full_frames: List[np.ndarray], temporal_data: Dict) -> Dict:
    start_time = time.time()
    
    if not full_frames:
        return {
            'is_ai_generated': False, 
            'confidence': 0.0, 
            'type': 'no_frames',
            'processing_time': round(time.time() - start_time, 2)
        }
    
    ai_indicators = 0
    total_indicators = 0
    edge_densities = []
    color_variances = []
    texture_analysis = []
    frequency_analysis = []
    
    for idx, frame in enumerate(full_frames[:5]):
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            continue
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        
        # Enhanced edge detection with multiple scales
        edges_fine = cv2.Canny(gray, 50, 150)
        edges_coarse = cv2.Canny(gray, 100, 200)
        edge_density = float(np.count_nonzero(edges_fine) / (edges_fine.shape[0] * edges_fine.shape[1]))
        edge_densities.append(edge_density)
        
        # Multi-scale texture analysis
        texture_features = analyze_texture_features(gray)
        texture_analysis.append(texture_features)
        
        # Frequency domain analysis
        freq_features = analyze_frequency_features(gray)
        frequency_analysis.append(freq_features)
        
        if len(frame.shape) == 3 and frame.shape[2] >= 3:
            var = float(np.mean(np.var(frame, axis=(0, 1))))
        else:
            var = 0.0
        color_variances.append(var)
        
        # Enhanced AI detection indicators
        if edge_density > 0.15:
            ai_indicators += 1
        if var < 50:
            ai_indicators += 1
        if texture_features['uniformity'] > 0.8:  # Too uniform might indicate AI
            ai_indicators += 1
        if freq_features['high_freq_ratio'] < 0.1:  # Low high-frequency content
            ai_indicators += 1
        total_indicators += 4
    
    # Temporal consistency analysis
    if temporal_data and 'transition_variance' in temporal_data:
        if isinstance(temporal_data['transition_variance'], (int, float)) and temporal_data['transition_variance'] < 50:
            ai_indicators += 1
            total_indicators += 1
    
    # Advanced temporal analysis
    if temporal_data and 'flow_variance' in temporal_data:
        flow_var = temporal_data.get('flow_variance', 0)
        if flow_var < 10:  # Very low motion variance might indicate AI
            ai_indicators += 1
            total_indicators += 1
    
    confidence = (ai_indicators / total_indicators * 100.0) if total_indicators > 0 else 0.0
    is_ai = confidence > 60.0
    avg_edge = float(np.mean(edge_densities)) if edge_densities else 0.0
    avg_texture_uniformity = float(np.mean([t['uniformity'] for t in texture_analysis])) if texture_analysis else 0.0
    avg_freq_ratio = float(np.mean([f['high_freq_ratio'] for f in frequency_analysis])) if frequency_analysis else 0.0
    
    # Enhanced content type classification
    if avg_edge > 0.2:
        ctype = 'ui_interface'
    elif avg_edge > 0.05 and avg_texture_uniformity < 0.7:
        ctype = 'natural_scene'
    elif avg_freq_ratio < 0.1:
        ctype = 'synthetic_content'
    else:
        ctype = 'mixed_content'
    
    processing_time = time.time() - start_time
    
    return {
        'is_ai_generated': is_ai,
        'confidence': confidence,
        'type': ctype,
        'ai_indicators': ai_indicators,
        'total_indicators': total_indicators,
        'avg_edge_density': avg_edge,
        'avg_color_variance': float(np.mean(color_variances)) if color_variances else 0.0,
        'avg_texture_uniformity': avg_texture_uniformity,
        'avg_frequency_ratio': avg_freq_ratio,
        'texture_analysis': texture_analysis,
        'frequency_analysis': frequency_analysis,
        'frames_analyzed': min(5, len(full_frames)),
        'processing_time': round(processing_time, 2),
    }

def analyze_texture_features(gray_image: np.ndarray) -> Dict[str, float]:
    """Analyze texture features for AI detection"""
    try:
        if SKIMAGE_AVAILABLE:
            # Calculate Local Binary Pattern (LBP) uniformity
            lbp = local_binary_pattern(gray_image, 8, 1, method='uniform')
            uniformity = float(np.sum(lbp == 0) / lbp.size)
        else:
            # Fallback: calculate uniformity using standard deviation
            uniformity = 1.0 - float(np.std(gray_image) / 255.0)
        
        # Calculate Gabor filter responses
        gabor_responses = []
        for angle in [0, 45, 90, 135]:
            kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 10, 0.5, 0, ktype=cv2.CV_32F)
            response = cv2.filter2D(gray_image, cv2.CV_8UC3, kernel)
            gabor_responses.append(float(np.mean(response)))
        
        gabor_variance = float(np.var(gabor_responses))
        
        return {
            'uniformity': uniformity,
            'gabor_variance': gabor_variance,
            'texture_complexity': 1.0 - uniformity
        }
    except Exception as e:
        logger.warning(f"Texture analysis failed: {e}")
        return {'uniformity': 0.5, 'gabor_variance': 0.0, 'texture_complexity': 0.5}

def analyze_frequency_features(gray_image: np.ndarray) -> Dict[str, float]:
    """Analyze frequency domain features for AI detection"""
    try:
        # FFT analysis
        fft = np.fft.fft2(gray_image)
        fft_shifted = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shifted)
        
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        
        # Calculate high-frequency energy ratio
        high_freq_mask = np.zeros_like(magnitude)
        high_freq_mask[center_h-h//4:center_h+h//4, center_w-w//4:center_w+w//4] = 1
        high_freq_energy = float(np.sum(magnitude * high_freq_mask))
        total_energy = float(np.sum(magnitude))
        high_freq_ratio = high_freq_energy / total_energy if total_energy > 0 else 0.0
        
        # Calculate spectral centroid
        y_coords, x_coords = np.ogrid[:h, :w]
        distances = np.sqrt((y_coords - center_h)**2 + (x_coords - center_w)**2)
        spectral_centroid = float(np.sum(magnitude * distances) / total_energy) if total_energy > 0 else 0.0
        
        return {
            'high_freq_ratio': high_freq_ratio,
            'spectral_centroid': spectral_centroid,
            'total_energy': total_energy
        }
    except Exception as e:
        logger.warning(f"Frequency analysis failed: {e}")
        return {'high_freq_ratio': 0.1, 'spectral_centroid': 0.0, 'total_energy': 0.0}

def _extract_comprehensive_features_sync(video_path: str) -> Dict:
    overall_start_time = time.time()
    
    try:
        logger.info(f"Starting comprehensive analysis of {os.path.basename(video_path)}")
        
        # Extract faces with timing
        faces, face_timing = extract_faces_from_video_sync(video_path)
        
        # Extract scene frames with timing
        full_frames, scene_timing = extract_scene_frames_sync(video_path)
        
        # Analyze temporal data
        temporal_data = analyze_frame_transitions_sync(video_path)
        
        # Compute frequency features
        frequency_features = compute_frequency_features_sync(video_path)
        
        # Analyze scene for AI generation
        scene_analysis = analyze_scene_for_ai_generation_sync(full_frames, temporal_data)
        
        total_processing_time = time.time() - overall_start_time
        
        logger.info(f"Comprehensive analysis completed in {total_processing_time:.2f}s - "
                   f"Found {len(faces)} faces across {len(full_frames)} scene frames")
        
        return {
            'face_sequences': faces,
            'full_frames': full_frames,
            'temporal_data': temporal_data,
            'frequency_features': frequency_features,
            'scene_analysis': scene_analysis,
            'metadata': {
                'faces_found': len(faces),
                'frames_analyzed': len(full_frames),
                'video_path': video_path,
                'extraction_success': True,
                'total_processing_time': round(total_processing_time, 2),
                'face_extraction_time': face_timing.get('processing_time', 0),
                'scene_extraction_time': scene_timing.get('processing_time', 0),
                'temporal_analysis_time': temporal_data.get('processing_time', 0),
                'frequency_analysis_time': frequency_features.get('processing_time', 0),
                'scene_analysis_time': scene_analysis.get('processing_time', 0),
                'processing_breakdown': {
                    'face_extraction': face_timing,
                    'scene_extraction': scene_timing,
                    'temporal_analysis': temporal_data.get('processing_time', 0),
                    'frequency_analysis': frequency_features.get('processing_time', 0),
                    'scene_analysis': scene_analysis.get('processing_time', 0)
                }
            }
        }
    except Exception as e:
        total_processing_time = time.time() - overall_start_time
        logger.exception(f"Comprehensive extraction failed after {total_processing_time:.2f}s: {e}")
        return {
            'face_sequences': [],
            'full_frames': [],
            'temporal_data': {},
            'frequency_features': {},
            'scene_analysis': {},
            'error': str(e),
            'metadata': {
                'faces_found': 0, 
                'frames_analyzed': 0, 
                'video_path': video_path, 
                'extraction_success': False,
                'total_processing_time': round(total_processing_time, 2),
                'error_occurred_at': round(total_processing_time, 2)
            },
        }

# ---- Async wrappers (for FastAPI or async callers) ----

async def extract_comprehensive_features(video_path: str) -> Dict:
    try:
        return await to_thread(_extract_comprehensive_features_sync, video_path)
    except Exception as e:
        logger.error(f"Comprehensive features extraction failed: {e}")
        return {'face_sequences': [], 'scene_frames': [], 'temporal_data': {}, 'frequency_features': {}, 'scene_analysis': {}, 'processing_time': 0}

async def extract_faces_from_video(video_path: str, frames_to_process: int = 15, frame_interval: int = 30, video_id: str = None, base_progress: int = 0) -> Tuple[List, Dict]:
    try:
        return await to_thread(extract_faces_from_video_sync, video_path, frames_to_process, frame_interval, video_id, base_progress)
    except Exception as e:
        logger.error(f"Face extraction failed: {e}")
        return [], {'processing_time': 0, 'video_duration': 0, 'processing_speed': 0, 'frames_per_second_processed': 0}

async def extract_scene_frames(video_path: str, max_frames: int = 8) -> Tuple[List[np.ndarray], Dict]:
    try:
        return await to_thread(extract_scene_frames_sync, video_path, max_frames)
    except Exception as e:
        logger.error(f"Scene frame extraction failed: {e}")
        return [], {'processing_time': 0, 'frames_extracted': 0, 'total_frames': 0}

async def analyze_frame_transitions(video_path: str) -> Dict:
    try:
        return await to_thread(analyze_frame_transitions_sync, video_path)
    except Exception as e:
        logger.error(f"Frame transitions analysis failed: {e}")
        return {'processing_time': 0, 'frames_analyzed': 0, 'transition_consistency': 0.5}

async def compute_frequency_features(video_path: str) -> Dict:
    try:
        return await to_thread(compute_frequency_features_sync, video_path)
    except Exception as e:
        logger.error(f"Frequency features analysis failed: {e}")
        return {'processing_time': 0, 'high_freq_ratio': 0.1, 'spectral_centroid': 0.0, 'total_energy': 0.0}

async def analyze_scene_for_ai_generation(full_frames: List[np.ndarray], temporal_data: Dict) -> Dict:
    try:
        return await to_thread(analyze_scene_for_ai_generation_sync, full_frames, temporal_data)
    except Exception as e:
        logger.error(f"Scene analysis failed: {e}")
        return {'processing_time': 0, 'ai_probability': 0.4, 'confidence': 50.0, 'artifacts': ['analysis_failed']}

# ---- Direct CLI test ----

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str, help="Video path to test")
    args = parser.parse_args()
    if args.video:
        print("Running comprehensive sync extraction...")
        result = _extract_comprehensive_features_sync(args.video)
        metadata = result.get("metadata", {})
        print(f"Result metadata: {metadata}")
        if 'processing_breakdown' in metadata:
            print("Processing breakdown:")
            for key, value in metadata['processing_breakdown'].items():
                if isinstance(value, dict):
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}s")
    else:
        print("No video path provided. Use --video <path>")


class VideoProcessor:
    """
    Production Video Processor for Deepfake Detection
    Integrates with existing video processing functionality
    """
    
    def __init__(self):
        self.face_extractor = FaceExtractor()
        self.logger = logging.getLogger(__name__)
        self.logger.info("[OK] Real VideoProcessor initialized successfully")
    
    async def process_video(self, video_path: str, max_faces: int = 15) -> Dict[str, Any]:
        """
        Process video and extract comprehensive features
        
        Args:
            video_path: Path to video file
            max_faces: Maximum number of faces to extract
            
        Returns:
            Dictionary with processing results
        """
        try:
            self.logger.info(f"[DETECTION] Processing video: {os.path.basename(video_path)}")
            
            # Extract comprehensive features
            result = await extract_comprehensive_features(video_path)
            
            # Add processing metadata
            result['processor'] = 'VideoProcessor'
            result['processing_type'] = 'real_video_analysis'
            result['success'] = True
            
            self.logger.info(f"[OK] Video processing completed: {len(result.get('face_sequences', []))} faces extracted")
            return result
            
        except Exception as e:
            self.logger.error(f"[ERROR] Video processing failed: {e}")
            return {
                'processor': 'VideoProcessor',
                'processing_type': 'real_video_analysis',
                'success': False,
                'error': str(e),
                'face_sequences': [],
                'full_frames': [],
                'temporal_data': {},
                'frequency_features': {},
                'scene_analysis': {}
            }
    
    async def extract_faces(self, video_path: str, max_faces: int = 15) -> List[torch.Tensor]:
        """
        Extract faces from video using real face detection
        
        Args:
            video_path: Path to video file
            max_faces: Maximum number of faces to extract
            
        Returns:
            List of preprocessed face tensors
        """
        try:
            faces, timing_info = await extract_faces_from_video(video_path, max_faces)
            self.logger.info(f"[OK] Extracted {len(faces)} faces from video")
            return faces
        except Exception as e:
            self.logger.error(f"[ERROR] Face extraction failed: {e}")
            return []
    
    async def analyze_temporal_features(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze temporal features of video
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with temporal analysis results
        """
        try:
            temporal_data = await analyze_frame_transitions(video_path)
            self.logger.info(f"[OK] Temporal analysis completed")
            return temporal_data
        except Exception as e:
            self.logger.error(f"[ERROR] Temporal analysis failed: {e}")
            return {}
    
    async def analyze_frequency_features(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze frequency features of video
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with frequency analysis results
        """
        try:
            frequency_data = await compute_frequency_features(video_path)
            self.logger.info(f"[OK] Frequency analysis completed")
            return frequency_data
        except Exception as e:
            self.logger.error(f"[ERROR] Frequency analysis failed: {e}")
            return {}
    
    def get_processing_capabilities(self) -> Dict[str, Any]:
        """
        Get information about processing capabilities
        
        Returns:
            Dictionary with capability information
        """
        return {
            'face_detection': 'YOLOv8 + MTCNN + OpenCV Haar',
            'temporal_analysis': 'Optical flow + frame transitions',
            'frequency_analysis': 'FFT + spectral analysis',
            'scene_analysis': 'Edge detection + color variance',
            'real_processing': True,
            'mock_processing': False
        }















# app/services/video_processor.py - ALIGNED WITH ADVANCED DEEPFAKE_DETECTOR
# import cv2
# import os
# import torch
# from torchvision import transforms
# from typing import List, Tuple
# import logging
# import numpy as np

# logger = logging.getLogger(__name__)

# # Try multiple face detection methods for robustness
# try:
#     from facenet_pytorch import MTCNN
#     MTCNN_AVAILABLE = True
# except ImportError:
#     MTCNN_AVAILABLE = False
#     logger.warning("MTCNN not available. Install with: pip install facenet-pytorch")

# try:
#     import dlib
#     DLIB_AVAILABLE = True
# except ImportError:
#     DLIB_AVAILABLE = False

# class AlignedFaceExtractor:
#     """ALIGNED face extractor compatible with advanced deepfake detector"""
    
#     def __init__(self):
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.detector = None
#         self.face_cascade = None
#         self._init_detectors()
        
#         # ALIGNED preprocessing - matches advanced detector expectations
#         self.preprocess = transforms.Compose([
#             transforms.ToPILImage(),
#             transforms.Resize((224, 224)),
#             transforms.ToTensor(),
#             transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#         ])
    
#     def _init_detectors(self):
#         """Initialize face detectors with fallback priority"""
#         # Priority 1: MTCNN (most accurate)
#         if MTCNN_AVAILABLE:
#             try:
#                 self.detector = MTCNN(
#                     device=self.device, 
#                     min_face_size=40, 
#                     thresholds=[0.6, 0.7, 0.7],
#                     select_largest=False,
#                     post_process=False
#                 )
#                 # Reduced logging to avoid duplicates
#                 return
#             except Exception as e:
#                 logger.warning(f"MTCNN initialization failed: {e}")
        
#         # Priority 2: OpenCV Haar Cascades (fallback)
#         try:
#             self.face_cascade = cv2.CascadeClassifier(
#                 cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#             )
#             if self.face_cascade.empty():
#                 raise Exception("Failed to load Haar cascade")
#             # Reduced logging to avoid duplicates
#         except Exception as e:
#             logger.error(f"[ERROR] All face detectors failed: {e}")

# def extract_faces_from_video(video_path: str, max_faces: int = 20, frame_interval: int = 5) -> List[torch.Tensor]:
#     """
#     ALIGNED face extraction function - returns tensors compatible with advanced detector
    
#     Args:
#         video_path: Path to video file
#         max_faces: Maximum number of faces to extract
#         frame_interval: Process every Nth frame
        
#     Returns:
#         List of preprocessed face tensors ready for advanced detection
#     """
#     if not os.path.exists(video_path):
#         raise FileNotFoundError(f"Video file not found: {video_path}")
    
#     logger.info(f"🎬 Processing video: {video_path}")
    
#     # Use global extractor instance
#     extractor = AlignedFaceExtractor()
    
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         raise IOError(f"Could not open video: {video_path}")
    
#     extracted_faces = []
#     frame_count = 0
#     successful_extractions = 0
    
#     try:
#         while len(extracted_faces) < max_faces:
#             ret, frame = cap.read()
#             if not ret:
#                 break
            
#             if frame_count % frame_interval == 0:
#                 try:
#                     faces = _detect_faces_in_frame(frame, extractor)
                    
#                     for face_img in faces:
#                         if len(extracted_faces) >= max_faces:
#                             break
                        
#                         try:
#                             # ALIGNED preprocessing - matches advanced detector expectations
#                             face_tensor = extractor.preprocess(face_img)
#                             extracted_faces.append(face_tensor)
#                             successful_extractions += 1
                            
#                         except Exception as e:
#                             logger.warning(f"Face preprocessing failed: {e}")
#                             continue
                
#                 except Exception as e:
#                     logger.warning(f"Frame processing failed at frame {frame_count}: {e}")
#                     continue
            
#             frame_count += 1
    
#     except Exception as e:
#         logger.error(f"Video processing error: {e}")
    
#     finally:
#         cap.release()
    
#     logger.info(f"[OK] Extracted {len(extracted_faces)} faces from {frame_count} frames")
#     logger.info(f"[DATA] Success rate: {successful_extractions}/{frame_count * len(extracted_faces) // max_faces if frame_count > 0 else 0}")
    
#     return extracted_faces

# def _detect_faces_in_frame(frame, extractor) -> List[np.ndarray]:
#     """
#     ALIGNED face detection using multiple methods
#     Returns raw face images ready for preprocessing
#     """
#     faces = []
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
#     # Method 1: MTCNN (preferred)
#     if extractor.detector is not None:
#         try:
#             boxes, probs = extractor.detector.detect(rgb_frame)
            
#             if boxes is not None and len(boxes) > 0:
#                 # Filter by confidence
#                 for i, (box, prob) in enumerate(zip(boxes, probs)):
#                     if prob is not None and prob > 0.85:  # High confidence only
#                         x1, y1, x2, y2 = [max(0, int(coord)) for coord in box]
                        
#                         # Ensure valid coordinates
#                         x2 = min(rgb_frame.shape[1], x2)
#                         y2 = min(rgb_frame.shape[0], y2)
                        
#                         if x2 > x1 and y2 > y1:
#                             face_img = rgb_frame[y1:y2, x1:x2]
                            
#                             # Quality check
#                             if face_img.size > 0 and min(face_img.shape[:2]) > 40:
#                                 faces.append(face_img)
                
#                 if faces:  # If MTCNN found faces, return them
#                     return faces
                    
#         except Exception as e:
#             logger.warning(f"MTCNN detection failed: {e}")
    
#     # Method 2: OpenCV Haar Cascade (fallback)
#     if extractor.face_cascade is not None:
#         try:
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             detected_faces = extractor.face_cascade.detectMultiScale(
#                 gray, 
#                 scaleFactor=1.1, 
#                 minNeighbors=5, 
#                 minSize=(50, 50),
#                 maxSize=(300, 300)
#             )
            
#             for (x, y, w, h) in detected_faces:
#                 # Extract with some padding
#                 padding = int(min(w, h) * 0.1)
#                 x1 = max(0, x - padding)
#                 y1 = max(0, y - padding)
#                 x2 = min(rgb_frame.shape[1], x + w + padding)
#                 y2 = min(rgb_frame.shape[0], y + h + padding)
                
#                 face_img = rgb_frame[y1:y2, x1:x2]
                
#                 if face_img.size > 0 and min(face_img.shape[:2]) > 40:
#                     faces.append(face_img)
                    
#         except Exception as e:
#             logger.warning(f"OpenCV detection failed: {e}")
    
#     return faces

# # ALIGNED compatibility functions for existing code
# def extract_faces_from_image(image_path: str) -> List[torch.Tensor]:
#     """Extract faces from a single image"""
#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"Image file not found: {image_path}")
    
#     extractor = AlignedFaceExtractor()
#     image = cv2.imread(image_path)
#     if image is None:
#         raise IOError(f"Could not read image: {image_path}")
    
#     faces = _detect_faces_in_frame(image, extractor)
#     processed_faces = []
    
#     for face_img in faces:
#         try:
#             face_tensor = extractor.preprocess(face_img)
#             processed_faces.append(face_tensor)
#         except Exception as e:
#             logger.warning(f"Face preprocessing failed: {e}")
#             continue
    
#     logger.info(f"[OK] Extracted {len(processed_faces)} faces from image")
#     return processed_faces

# # Global instance for compatibility
# face_extractor = AlignedFaceExtractor()

# # Legacy function names for backward compatibility
# def detect_faces_in_frame(frame):
#     """Legacy function for backward compatibility"""
#     return _detect_faces_in_frame(frame, face_extractor)

# # Additional utility functions
# def validate_video_file(video_path: str) -> bool:
#     """Validate if video file can be processed"""
#     try:
#         cap = cv2.VideoCapture(video_path)
#         if not cap.isOpened():
#             return False
        
#         # Check if we can read at least one frame
#         ret, frame = cap.read()
#         cap.release()
#         return ret and frame is not None
        
#     except Exception:
#         return False

# def get_video_info(video_path: str) -> dict:
#     """Get video information for processing optimization"""
#     try:
#         cap = cv2.VideoCapture(video_path)
#         if not cap.isOpened():
#             return {}
        
#         fps = cap.get(cv2.CAP_PROP_FPS)
#         frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         duration = frame_count / fps if fps > 0 else 0
        
#         cap.release()
        
#         return {
#             'fps': fps,
#             'frame_count': frame_count,
#             'width': width,
#             'height': height,
#             'duration': duration,
#             'size_mb': os.path.getsize(video_path) / (1024 * 1024)
#         }
#     except Exception:
#         return {}


