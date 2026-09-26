# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Single-container "website + APIs" production image for iFake deepfake
# detector. Builds the Vite frontend in a Node stage, copies dist into the
# final Python image, and serves the whole stack through gunicorn + uvicorn
# workers on port 8000. Same-origin by default, so the browser app never
# needs CORS.
#
# If you prefer a split deploy (nginx frontend + separate backend API), the
# companion frontend/Dockerfile still works unchanged.
# ---------------------------------------------------------------------------

# --- Stage 1: Build the frontend SPA with Node --------------------------------
FROM node:20-alpine AS frontend-build
WORKDIR /web

# Install deps first for better layer caching
COPY frontend/package.json frontend/package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      npm ci; \
    else \
      npm install; \
    fi

COPY frontend/ .
# Empty VITE_* env = same-origin (one-container default). Override at build
# time if you want the compiled frontend to point at a separate API host:
#   docker build --build-arg VITE_API_URL=https://api.ifake.ai ...
ARG VITE_API_URL=""
ARG VITE_WS_URL=""
ARG VITE_BASE_PATH="/"
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WS_URL=${VITE_WS_URL}
ENV VITE_BASE_PATH=${VITE_BASE_PATH}
RUN npm run build

# --- Stage 2: Production backend + pre-built frontend ------------------------
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY ml_artifacts ./ml_artifacts
COPY advanced_models ./advanced_models
COPY config.env.example ./config.env
COPY gunicorn.conf.py ./gunicorn.conf.py
COPY run.py ./run.py

# Ship the compiled frontend SPA so FastAPI can serve it at "/" same-origin.
COPY --from=frontend-build /web/dist /app/frontend/dist

ENV FORCE_CPU_MODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV MAX_CONCURRENT_JOBS=2
ENV DEVELOPMENT_MODE=false

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/v1/health')" || exit 1

# gunicorn manages multiple uvicorn workers on Linux (this image's platform).
# Override with "uvicorn backend.app.main:app --host 0.0.0.0 --port 8000" if
# you ever need single-worker debugging.
CMD ["python", "-m", "gunicorn", "backend.app.main:app", "-c", "/app/gunicorn.conf.py"]
