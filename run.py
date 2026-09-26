#!/usr/bin/env python3
"""One-command launcher for iFake deepfake detector.

Usage:
    python run.py

Behaviour:
    1. Loads `config.env` from repo root into os.environ if present.
    2. Ensures frontend is built (frontend/dist/index.html exists). If
       missing and npm is available, runs `npm ci` + `npm run build` in
       frontend/. If npm cannot be found, prints a clear instruction.
    3. Launches the backend using gunicorn (Linux/macOS) or uvicorn
       (Windows / when gunicorn is not installed) on HOST:PORT.

Pure "I only want APIs" alternative:
    uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
CONFIG_ENV = REPO_ROOT / "config.env"
FRONTEND_DIR = REPO_ROOT / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "dist" / "index.html"
REQUIREMENTS = REPO_ROOT / "requirements.txt"


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        print(f"[run] INFO: no {path.name} found (using current env vars).")
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
    print(f"[run] Loaded env from {path}.")


def _frontend_ok() -> bool:
    return FRONTEND_INDEX.is_file()


def _build_frontend() -> bool:
    if _frontend_ok():
        return True
    if not (FRONTEND_DIR / "package.json").is_file():
        print("[run] WARNING: frontend/package.json missing, skipping frontend build.")
        return False
    npm = shutil.which("npm")
    if not npm:
        print(
            "[run] WARNING: npm not found on PATH. Frontend was NOT built.\n"
            "      Install Node.js 18+, then run:\n"
            "        cd frontend && npm install && npm run build\n"
            "      The website (/) will 404 until then, but /docs and /api still work."
        )
        return False
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.is_dir():
        print("[run] Installing frontend dependencies (npm ci / install)...")
        install_args = [npm, ("ci" if (FRONTEND_DIR / "package-lock.json").is_file() else "install")]
        try:
            subprocess.run(install_args, cwd=FRONTEND_DIR, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"[run] ERROR: frontend install failed ({exc}).")
            return False
    print("[run] Building frontend (npm run build)...")
    env = os.environ.copy()
    env.setdefault("VITE_API_URL", "")
    env.setdefault("VITE_WS_URL", "")
    try:
        subprocess.run([npm, "run", "build"], cwd=FRONTEND_DIR, env=env, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"[run] ERROR: frontend build failed ({exc}).")
        return False
    return _frontend_ok()


def _ensure_runtime_deps() -> None:
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except ImportError:
        print(
            "[run] FastAPI/uvicorn not importable. Did you install dependencies?\n"
            "      python -m venv venv\n"
            "      venv\\Scripts\\activate     (Windows)\n"
            "      source venv/bin/activate   (macOS/Linux)\n"
            "      pip install -r requirements.txt"
        )
        sys.exit(2)


def _serve() -> int:
    # Render, Railway, Fly.io, Heroku, and most PaaS platforms expose a
    # single PORT env var and expect the container to bind to 0.0.0.0.
    # Railway additionally supports a BIND env.  Locally, fall back to
    # 127.0.0.1:8000 only when *no* cloud env hints are present.
    _cloud_env = any(
        k in os.environ
        for k in (
            "PORT",
            "BIND",
            "RENDER",
            "RAILWAY_STATIC_URL",
            "RAILWAY_SERVICE_NAME",
            "FLY_APP_NAME",
            "HEROKU",
            "DYNO",
            "K_SERVICE",
            "WEBSITE_HOSTNAME",
            "GUNICORN_CMD_ARGS",
            "DEBIAN_FRONTEND",
        )
    )
    default_host = "0.0.0.0" if _cloud_env else "127.0.0.1"
    host = os.getenv("HOST", os.getenv("BIND", default_host)).strip() or default_host
    # Render/Railway set PORT as the single externally-routable port.
    port = (
        os.getenv("PORT", os.getenv("RAILWAY_PORT", "8000")).strip()
        or "8000"
    )
    try:
        port_int = int(port)
    except ValueError:
        print(f"[run] WARNING: invalid PORT={port!r}, falling back to 8000")
        port_int = 8000
        port = "8000"
    if port_int <= 0 or port_int > 65535:
        print(f"[run] WARNING: PORT={port_int} out of range, falling back to 8000")
        port_int = 8000
        port = "8000"

    # Display URL with localhost when bound to all interfaces (friendlier for
    # humans), while keeping the host env exactly what the platform asked for.
    display_host = "localhost" if host in ("0.0.0.0", "::", "[::]") else host
    api_docs = f"http://{display_host}:{port_int}/docs"
    website = f"http://{display_host}:{port_int}/"
    if _frontend_ok():
        print(f"[run] Website: {website}")
    else:
        print(f"[run] INFO: frontend not built -> {website} will 404 (APIs still work).")
    print(f"[run] API docs: {api_docs}")
    print(f"[run] Health  : http://{display_host}:{port_int}/api/health")

    gunicorn = shutil.which("gunicorn")
    if gunicorn and sys.platform != "win32":
        print("[run] Launching with gunicorn (production) ...")
        # Expose host/port via env so gunicorn.conf.py picks them up.
        os.environ["HOST"] = host
        os.environ["PORT"] = str(port_int)
        cmd = [
            sys.executable, "-m", "gunicorn",
            "backend.app.main:app",
            "-c", str(REPO_ROOT / "gunicorn.conf.py"),
        ]
    else:
        if sys.platform == "win32":
            print("[run] Launching with uvicorn (gunicorn is not supported on Windows).")
        else:
            print("[run] gunicorn not installed, falling back to uvicorn.")
            if REQUIREMENTS.is_file():
                print("      To enable multi-worker production mode: pip install gunicorn")
        # Railway/Render-style platform hints: set a production-ish
        # keep-alive that works behind reverse proxies.
        keep_alive = int(os.getenv("UVICORN_KEEP_ALIVE", "15"))
        cmd = [
            sys.executable, "-m", "uvicorn",
            "backend.app.main:app",
            "--host", host,
            "--port", str(port_int),
            "--timeout-keep-alive", str(keep_alive),
        ]

    os.chdir(REPO_ROOT)
    try:
        completed = subprocess.run(cmd, check=False)
        return completed.returncode
    except KeyboardInterrupt:
        print("\n[run] stopped by user.")
        return 0


def main() -> int:
    _load_dotenv(CONFIG_ENV)
    _ensure_runtime_deps()
    _build_frontend()
    return _serve()


if __name__ == "__main__":
    sys.exit(main())
