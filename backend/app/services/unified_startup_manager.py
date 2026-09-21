#!/usr/bin/env python3
"""
Unified Startup Manager - 2025 Style Clean Startup Sequence
Fixes all redundant initializations, duplicate imports, and model loading issues
"""

import os
import sys
import logging
import threading
import warnings
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# GLOBAL STATE MANAGEMENT
# =============================================================================

class StartupState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SystemCapabilities:
    enhanced_detection: bool = False
    modern_ai_detection: bool = False
    title_classification: bool = False
    realtime_detection: bool = False
    youtube_support: bool = False
    hybrid_detector: bool = False
    specialized_detectors: bool = False
    caching: bool = False
    self_learning: bool = False
    analytics: bool = False

class UnifiedStartupManager:
    """
    Unified startup manager that ensures clean, efficient initialization
    with no duplicates, proper lazy loading, and elegant 2025-style logging
    """
    
    def __init__(self):
        self._state = StartupState.UNINITIALIZED
        self._lock = threading.Lock()
        self._initialized_services: Set[str] = set()
        self._capabilities = SystemCapabilities()
        
        # Device configuration (set once)
        self._device_info: Optional[Dict[str, Any]] = None
        self._safe_device: Optional[str] = None
        
        # Import cache (avoid duplicate imports)
        self._import_cache: Dict[str, Any] = {}
        
        # Model registry (avoid duplicate registrations)
        self._registered_models: Set[str] = set()
        
        # Logger setup
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup unified logging system"""
        # Configure root logger to be clean and elegant
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Suppress verbose library logs
        logging.getLogger('timm').setLevel(logging.WARNING)
        logging.getLogger('ultralytics').setLevel(logging.WARNING)
        logging.getLogger('torch').setLevel(logging.WARNING)
        logging.getLogger('transformers').setLevel(logging.WARNING)
    
    def initialize(self) -> Dict[str, Any]:
        """Main initialization method - called once at startup"""
        with self._lock:
            if self._state != StartupState.UNINITIALIZED:
                return self._get_status()
            
            self._state = StartupState.INITIALIZING
            
            try:
                # Phase 1: Environment and warnings
                self._initialize_environment()
                
                # Phase 2: Device configuration (once)
                self._configure_device()
                
                # Phase 3: Core imports (cached, no duplicates)
                self._initialize_imports()
                
                # Phase 4: Service initialization (deduplicated)
                self._initialize_services()
                
                # Phase 5: Model registration (singleton pattern)
                self._register_models()
                
                # Phase 6: Capability assessment
                self._assess_capabilities()
                
                self._state = StartupState.COMPLETED
                return self._get_status()
                
            except Exception as e:
                self._state = StartupState.FAILED
                logging.error(f"❌ Startup failed: {e}")
                raise
    
    def _initialize_environment(self):
        """Initialize environment variables and warning suppression"""
        if "environment" in self._initialized_services:
            return
        
        # Set optimal environment variables
        os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")
        os.environ.setdefault("TORCH_USE_CUDA_DSA", "1")
        os.environ.setdefault("ULTRALYTICS_VERBOSE", "False")
        os.environ.setdefault("YOLO_VERBOSE", "False")
        os.environ.setdefault("PYTORCH_WARN_LEVEL", "0")
        os.environ.setdefault("TORCH_WARN_LEVEL", "0")
        os.environ.setdefault("PYTHONWARNINGS", "ignore")
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
        
        # Comprehensive warning suppression
        warnings.filterwarnings("ignore")
        warnings.simplefilter("ignore")
        
        # Python 3.13 compatibility fixes
        self._apply_python313_fixes()
        
        self._initialized_services.add("environment")
        logging.info("🔧 Environment configured")
    
    def _apply_python313_fixes(self):
        """Apply Python 3.13 compatibility fixes"""
        try:
            # LooseVersion compatibility fix
            from packaging.version import Version
            import types
            
            class LooseVersion:
                def __init__(self, vstring=None):
                    self.vstring = vstring
                    if vstring:
                        self.parse(vstring)
                
                def parse(self, vstring):
                    import re
                    self.vstring = vstring
                    components = re.split(r'[.-]', vstring)
                    self.version = []
                    for component in components:
                        try:
                            self.version.append(int(component))
                        except ValueError:
                            self.version.append(component)
                
                def __str__(self):
                    return self.vstring
                
                def __repr__(self):
                    return f"LooseVersion('{self.vstring}')"
                
                def __cmp__(self, other):
                    if isinstance(other, str):
                        other = LooseVersion(other)
                    return (self.version > other.version) - (self.version < other.version)
                
                def __eq__(self, other):
                    return self.__cmp__(other) == 0
                
                def __lt__(self, other):
                    return self.__cmp__(other) < 0
                
                def __le__(self, other):
                    return self.__cmp__(other) <= 0
                
                def __gt__(self, other):
                    return self.__cmp__(other) > 0
                
                def __ge__(self, other):
                    return self.__cmp__(other) >= 0
            
            # Create mock distutils.version module
            mock_distutils_version = types.ModuleType('distutils.version')
            mock_distutils_version.LooseVersion = LooseVersion
            
            # Add to sys.modules
            if 'distutils.version' not in sys.modules:
                sys.modules['distutils.version'] = mock_distutils_version
            
            logging.info("🐍 Python 3.13 compatibility fixes applied")
            
        except ImportError:
            logging.warning("⚠️ packaging not available, LooseVersion fix skipped")
        except Exception as e:
            logging.warning(f"⚠️ Python 3.13 fixes failed: {e}")
    
    def _configure_device(self):
        """Configure device once - no repeated checks"""
        if "device" in self._initialized_services:
            return
        
        # Use unified CUDA manager for consistent device configuration
        try:
            from .unified_cuda_manager import unified_cuda_manager
            self._device_info = unified_cuda_manager.configure_device()
            self._safe_device = unified_cuda_manager.get_safe_device()
            logging.info(f"🔧 Device configured: {self._safe_device}")
        except ImportError:
            # Fallback to basic device configuration
            force_cpu = os.getenv("FORCE_CPU_MODE", "0") == "1"
            
            if force_cpu:
                self._safe_device = "cpu"
                self._device_info = {
                    'safe_device': 'cpu',
                    'cuda_available': False,
                    'cuda_devices': [],
                    'fallback_reasons': ['Force CPU mode enabled'],
                    'device_count': 0
                }
                logging.info("🔧 Force CPU mode enabled")
            else:
                # Check CUDA availability
                try:
                    import torch
                    if torch.cuda.is_available():
                        self._safe_device = "cuda:0"
                        self._device_info = {
                            'safe_device': 'cuda:0',
                            'cuda_available': True,
                            'cuda_devices': [torch.cuda.get_device_name(0)],
                            'fallback_reasons': [],
                            'device_count': torch.cuda.device_count()
                        }
                        logging.info(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
                    else:
                        self._safe_device = "cpu"
                        self._device_info = {
                            'safe_device': 'cpu',
                            'cuda_available': False,
                            'cuda_devices': [],
                            'fallback_reasons': ['CUDA not available'],
                            'device_count': 0
                        }
                        logging.info("💻 Using CPU (CUDA not available)")
                except ImportError:
                    self._safe_device = "cpu"
                    self._device_info = {
                        'safe_device': 'cpu',
                        'cuda_available': False,
                        'cuda_devices': [],
                        'fallback_reasons': ['PyTorch not available'],
                        'device_count': 0
                    }
                    logging.info("💻 Using CPU (PyTorch not available)")
        
        self._initialized_services.add("device")
    
    def _initialize_imports(self):
        """Initialize core imports once - no duplicates"""
        if "imports" in self._initialized_services:
            return
        
        # Import core libraries (cached)
        self._import_cache['torch'] = self._safe_import_torch()
        self._import_cache['torchvision'] = self._safe_import_torchvision()
        self._import_cache['opencv'] = self._safe_import_opencv()
        self._import_cache['numpy'] = self._safe_import_numpy()
        
        self._initialized_services.add("imports")
        logging.info("📦 Core imports cached")
    
    def _safe_import_torch(self):
        """Safely import PyTorch"""
        try:
            import torch
            return torch
        except ImportError as e:
            logging.error(f"❌ PyTorch import failed: {e}")
            return None
    
    def _safe_import_torchvision(self):
        """Safely import torchvision"""
        try:
            from torchvision import models, transforms
            return {"models": models, "transforms": transforms}
        except ImportError as e:
            logging.error(f"❌ torchvision import failed: {e}")
            return None
    
    def _safe_import_opencv(self):
        """Safely import OpenCV"""
        try:
            import cv2
            return cv2
        except ImportError as e:
            logging.error(f"❌ OpenCV import failed: {e}")
            return None
    
    def _safe_import_numpy(self):
        """Safely import NumPy"""
        try:
            import numpy as np
            return np
        except ImportError as e:
            logging.error(f"❌ NumPy import failed: {e}")
            return None
    
    def _initialize_services(self):
        """Initialize services once - no duplicates"""
        if "services" in self._initialized_services:
            return
        
        # Initialize enhanced services
        self._initialize_enhanced_services()
        
        # Initialize detection services
        self._initialize_detection_services()
        
        self._initialized_services.add("services")
        logging.info("⚙️ Services initialized")
    
    def _initialize_enhanced_services(self):
        """Initialize enhanced services"""
        try:
            # MTCNN handler
            from .enhanced_mtcnn_handler import MTCNN_AVAILABLE
            if MTCNN_AVAILABLE:
                logging.info("👤 MTCNN available")
            
            # YOLO handler
            from .enhanced_yolo_handler import YOLO_AVAILABLE
            if YOLO_AVAILABLE:
                logging.info("🎯 YOLO available")
                
        except ImportError as e:
            logging.warning(f"⚠️ Enhanced services not available: {e}")
    
    def _initialize_detection_services(self):
        """Initialize detection services"""
        try:
            # Deepfake detector
            from .deepfake_detector import DeepfakeDetector
            self._deepfake_detector = DeepfakeDetector()
            self._capabilities.enhanced_detection = True
            
            # Enhanced detector
            from .enhanced_detector import EnhancedDetector
            self._enhanced_detector = EnhancedDetector()
            self._capabilities.modern_ai_detection = True
            
            # Real-time detector
            from .realtime_detector import RealTimeDeepfakeDetector
            self._realtime_detector = RealTimeDeepfakeDetector()
            self._capabilities.realtime_detection = True
            
            logging.info("🔍 Detection services ready")
            
        except ImportError as e:
            logging.warning(f"⚠️ Detection services not available: {e}")
    
    def _register_models(self):
        """Register models once - no duplicates"""
        if "models" in self._initialized_services:
            return
        
        try:
            from .unified_model_loader import unified_model_loader
            
            # Register critical models with unified loader
            unified_model_loader.register_critical_models()
            
            logging.info("🧠 Model registry configured")
            
        except ImportError as e:
            logging.warning(f"⚠️ Unified model registry not available: {e}")
            # Fallback to lazy model loader
            try:
                from .lazy_model_loader import lazy_loader
                
                # Register critical models (avoid duplicates)
                critical_models = [
                    ('yolo_face', 1),
                    ('efficientnet_b0', 2),
                    ('efficientnet_b7', 3),
                    ('resnet50', 4),
                    ('densenet121', 5),
                    ('inception_v3', 6),
                    ('vgg16', 7)
                ]
                
                for model_name, priority in critical_models:
                    if model_name not in self._registered_models:
                        # Create placeholder loader
                        loader_func = lambda name=model_name: self._create_model_loader(name)
                        lazy_loader.register_model_loader(model_name, loader_func, priority)
                        self._registered_models.add(model_name)
                
                logging.info("🧠 Model registry configured (fallback)")
                
            except ImportError as e2:
                logging.warning(f"⚠️ Model registry not available: {e2}")
        
        self._initialized_services.add("models")
    
    def _create_model_loader(self, model_name: str):
        """Create a model loader function"""
        def loader():
            # This will be called when the model is actually needed
            logging.info(f"🔄 Loading {model_name} on first use")
            return None  # Placeholder
        return loader
    
    def _assess_capabilities(self):
        """Assess system capabilities"""
        # YouTube support
        try:
            from .youtube_downloader import YouTubeDownloader
            self._capabilities.youtube_support = True
        except ImportError:
            pass
        
        # Caching
        try:
            from .caching_service import CachingService
            self._capabilities.caching = True
        except ImportError:
            pass
        
        # Analytics
        try:
            from .analytics_service import AnalyticsService
            self._capabilities.analytics = True
        except ImportError:
            pass
        
        logging.info("📊 Capabilities assessed")
    
    def _get_status(self) -> Dict[str, Any]:
        """Get current startup status"""
        return {
            'state': self._state.value,
            'device': self._device_info,
            'capabilities': self._capabilities.__dict__,
            'services': list(self._initialized_services),
            'models_registered': len(self._registered_models)
        }
    
    def get_device(self) -> str:
        """Get the safe device"""
        return self._safe_device or "cpu"
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        return self._device_info or {}
    
    def get_capabilities(self) -> SystemCapabilities:
        """Get system capabilities"""
        return self._capabilities
    
    def print_startup_summary(self):
        """Print elegant 2025-style startup summary"""
        if self._state != StartupState.COMPLETED:
            return
        
        print("\n" + "="*60)
        print("🚀 DEEPFAKE DETECTION SYSTEM - READY")
        print("="*60)
        
        # Device info
        device_info = self.get_device_info()
        device_emoji = "🚀" if device_info.get('cuda_available') else "💻"
        print(f"{device_emoji} Device: {device_info.get('safe_device', 'unknown')}")
        
        # Capabilities
        capabilities = self.get_capabilities()
        print("\n📋 SYSTEM CAPABILITIES:")
        for attr, value in capabilities.__dict__.items():
            emoji = "✅" if value else "❌"
            name = attr.replace('_', ' ').title()
            print(f"   {emoji} {name}")
        
        print("\n🎯 STATUS: Ready for deepfake detection")
        print("="*60 + "\n")

# Global startup manager instance
_startup_manager: Optional[UnifiedStartupManager] = None
_startup_lock = threading.Lock()

def get_startup_manager() -> UnifiedStartupManager:
    """Get the global startup manager (singleton)"""
    global _startup_manager
    
    with _startup_lock:
        if _startup_manager is None:
            _startup_manager = UnifiedStartupManager()
        return _startup_manager

def initialize_system() -> Dict[str, Any]:
    """Initialize the entire system - call this once at startup"""
    manager = get_startup_manager()
    return manager.initialize()

def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    manager = get_startup_manager()
    return manager._get_status()

def print_startup_summary():
    """Print startup summary"""
    manager = get_startup_manager()
    manager.print_startup_summary()
