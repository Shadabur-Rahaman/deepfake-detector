import os
import sys
import logging
import io
import contextlib

def configure_logging():
    """Configure Python logging with reduced verbosity from noisy libraries"""
    # Configure Python logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    
    # Reduce verbosity from noisy libraries
    logging.getLogger("absl").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

def suppress_cpp_warnings():
    """Set environment variables to reduce TensorFlow/C++ noise and return stderr suppression context"""
    # Environment variables to reduce TensorFlow/C++ noise
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # silence TF C++ INFO/WARNING
    os.environ.setdefault("ABSL_CPP_MIN_LOG_LEVEL", "3")
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")  # Use only first GPU
    os.environ.setdefault("OMP_NUM_THREADS", "1")  # Reduce OpenMP noise
    
    # Additional CUDA-specific environment variables to suppress warnings
    os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")  # Disable CUDA launch blocking
    os.environ.setdefault("TORCH_CUDNN_V8_API_ENABLED", "1")  # Enable cuDNN v8 API
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:128")  # Optimize CUDA memory allocation
    
    # Suppress specific CUDA driver and factory warnings
    os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
    os.environ.setdefault("TF_GPU_THREAD_MODE", "gpu_private")
    
    # Import warnings module and set up comprehensive warning filters
    import warnings
    warnings.filterwarnings("ignore", message=".*Skipping registering GPU devices.*")
    warnings.filterwarnings("ignore", message=".*could not load the CUDA driver.*")
    warnings.filterwarnings("ignore", message=".*Unable to register cuDNN factory.*")
    warnings.filterwarnings("ignore", message=".*Unable to register cuBLAS factory.*")
    warnings.filterwarnings("ignore", message=".*Duplicate PluggableDeviceFactory.*")
    warnings.filterwarnings("ignore", message=".*computation placer already registered.*")
    warnings.filterwarnings("ignore", message=".*factory already been registered.*")
    warnings.filterwarnings("ignore", message=".*duplicate registration.*")
    warnings.filterwarnings("ignore", message=".*Unable to register.*factory.*")
    warnings.filterwarnings("ignore", message=".*cuDNN.*")
    warnings.filterwarnings("ignore", message=".*cuBLAS.*")
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    # Utility context manager to temporarily capture/stash stderr during noisy imports
    @contextlib.contextmanager
    def _suppress_stderr_ctx():
        old_stderr = sys.stderr
        try:
            sys.stderr = io.StringIO()
            yield
        finally:
            sys.stderr = old_stderr
    
    return _suppress_stderr_ctx

def mount_static_once(app):
    """Mount static directories only once to prevent duplicate logs"""
    if getattr(app.state, "static_mounted", False):
        return
    
    from fastapi.staticfiles import StaticFiles
    import os
    
    # Perform mount(s) for video directories
    app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")
    app.mount("/downloaded_videos", StaticFiles(directory="downloaded_videos"), name="downloaded_videos")
    
    # Also mount general static if it exists
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    app.state.static_mounted = True
    logging.getLogger("app.main").info("[OK] Static file directories mounted successfully")
