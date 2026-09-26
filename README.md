# Deepfake Detector

FastAPI + React app that scores images and videos for likely AI manipulation using an ensemble of local computer-vision models. Optional OpenAI / Gemini / Claude keys can add extra analysis.

Live UI (static GitHub Pages demo): **https://shadabur-rahaman.github.io/deepfake-detector/**  
Detection API runs locally or in Docker — Pages only hosts the frontend.

## What you need

- Python 3.11+
- Node.js 18+ (only if you want to build the website; pure APIs don't need it)
- 8 GB RAM minimum (16 GB is more comfortable)
- GPU is optional; CPU mode works

## Quick start (recommended: one command)

This launches the ENTIRE app — website + APIs + Swagger docs + WebSockets — on a single port, no two terminals required.

```bash
git clone https://github.com/Shadabur-Rahaman/deepfake-detector.git
cd deepfake-detector
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy config.env.example config.env   # Windows
# cp config.env.example config.env  # macOS/Linux
#
# Edit config.env:
#   - Set SECRET_KEY (python -c "import secrets; print(secrets.token_urlsafe(32))")
#   - Leave CORS_ORIGINS empty in one-container mode (same origin is the default)
python run.py
```

Then open:
- Website: http://localhost:8000/
- Swagger (try the APIs interactively): http://localhost:8000/docs
- ReDoc): http://localhost:8000/redoc
- API health): http://localhost:8000/api/health  and  http://localhost:8000/v1/health

How it works:
- If `frontend/dist/index.html` exists, FastAPI serves it at `"/"` (same-origin, no CORS)
- If `frontend/dist/index.html` is missing, `python run.py` will run `npm install` automatically
  install && npm run build` for you (npm is on PATH). APIs always work either way.

## Quick start (I only want the APIs)

Skip the website build entirely:

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
# -> http://127.0.0.1:8000/docs
```

## Calling the APIs directly

Public API is at /v1 and /api work interchangeably

```bash
# 1) Upload a video / image (returns video_id / job_id)
curl -X POST "http://127.0.0.1:8000/v1/detect" -F "file=@video.mp4" -F "detection_mode=hybrid"

# 2) Poll until status is completed
curl "http://127.0.0.1:8000/v1/jobs/VIDEO_ID"
```

Modes: `traditional`, `modern-ai`, `hybrid`. Optional `X-API-Key` header if `PUBLIC_API_KEY` is set in `config.env`.

### Auth (JWT or API key)

```bash
curl -X POST http://127.0.0.1:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"secret123","full_name":"You"}'

curl -X POST http://127.0.0.1:8000/v1/auth/api-keys \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"prod"}'

curl -X POST http://127.0.0.1:8000/v1/detect \
  -H "X-API-Key: ifk_..." \
  -F "file=@video.mp4"
```

## Docker

Recommended single-container (website + APIs together):

```bash
copy config.env.example config.env
docker compose up --build
# open http://localhost:8000/
```

Want a split deploy (separate nginx for frontend + separate backend)? Uncomment the second block in `docker-compose.yml` and comment out the single-container `app` block.

Production:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

## Frontend-only dev mode (separate Vite dev server, for when you're editing the frontend code)

If you're iterating on frontend code, keep `python run.py` on 8000, then run a Vite separately on port 5173 with Vite's built-in `/api` → :8000 proxy so you get hot reload.

```bash
cd frontend
npm install
npm run dev # http://127.0.0.1:5173
```

Vite proxies `/api`, `/v1`, `/ws`, etc through to port 8000 automatically (see vite.config.ts).

## Project layout

```
backend/app.py       FastAPI app (canonical entry: backend.app.main:app)
frontend/        React + Vite + Tailwind UI
ml_artifacts/   Model weights (Git LFS)
deploy/         Nginx config for the optional frontend-only container
run.py         One-command launcher (env + build + serve)
gunicorn.conf.py  Production multi-worker config (used by Linux/macOS + Docker)
```

## Configuration

Copy `config.env.example` to `config.env`. Leave API keys empty to run on local models only. Do not commit `config.env`.

If you previously committed real keys in this repository, **rotate them at the provider (OpenAI, Google AI Studio, Anthropic) — those keys must be treated as leaked.

### Production checklist before first deploy:

1. Set `SECRET_KEY` to a long random string
2. Set `DEVELOPMENT_MODE=false`
3. Set `CORS_ORIGINS` empty for same-origin; only add origins here if you serve the frontend from a separate domain
4. Set `FORCE_CPU_MODE=0` only if you have a working NVIDIA GPU + CUDA
5. Back DB path in `DATABASE_URL if you want Postgres instead of SQLite) — defaults to `sqlite:///./deepfake_detection.db`

## Git LFS

Large `*.pth` / `*.pt` files are tracked with Git LFS. After clone:

```bash
git lfs install
git lfs pull
```

## License

MIT — see [LICENSE](LICENSE).
