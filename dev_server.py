"""
Development server launcher with hot reload for the backend FastAPI app.

- Watches only the `backend/` directory for Python file changes
- Excludes large and non-code paths to avoid unnecessary reloads
- Keeps a single worker to ensure CUDA/PyTorch is initialized once per reload

Usage:
  python dev_server.py

Optional environment variables:
  HOST (default: 127.0.0.1)
  PORT (default: 8000)
  LOG_LEVEL (default: info)
"""

import os
from pathlib import Path

import uvicorn


def main() -> None:
    repo_root = Path(__file__).parent
    backend_dir = str(repo_root / "backend")

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")

    # Exclude heavy/non-code paths and large files from triggering reloads
    reload_excludes = [
        "**/__pycache__/**",
        "**/*.pt",
        "**/*.pth",
        "**/*.onnx",
        "**/*.ckpt",
        "uploaded_videos/**",
        "downloaded_videos/**",
        "advanced_models/**",
        "models/**",
        "*.log",
        "logs/**",
        "**/.venv/**",
        "**/venv/**",
        "**/.git/**",
    ]

    # Run uvicorn with reload enabled and limited to backend dir
    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=True,
        reload_dirs=[backend_dir],
        reload_excludes=reload_excludes,
        # Keep a single process so CUDA/PyTorch is initialized once per reload
        workers=1,
    )


if __name__ == "__main__":
    main()


