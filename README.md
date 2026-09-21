# Deepfake Detector

FastAPI + React app that scores images and videos for likely AI manipulation using an ensemble of local computer-vision models. Optional OpenAI / Gemini / Claude keys can add extra analysis.

Live UI (static GitHub Pages demo): **https://shadabur-rahaman.github.io/deepfake-detector/**  
Detection API runs locally or in Docker — Pages only hosts the frontend.

## What you need

- Python 3.11+
- Node.js 18+
- 8 GB RAM minimum (16 GB is more comfortable)
- GPU is optional; CPU mode works

## Quick start (local)

```bash
git clone https://github.com/Shadabur-Rahaman/deepfake-detector.git
cd deepfake-detector
```

### Backend

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy config.env.example config.env   # Windows
# cp config.env.example config.env  # macOS/Linux
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
copy .env.example .env   # Windows
# cp .env.example .env
npm install
npm run dev
```

App: http://127.0.0.1:5173

## Docker

```bash
copy config.env.example config.env
docker compose up --build
```

- UI: http://localhost:8080
- API: http://localhost:8000

## Project layout

```
backend/app/     FastAPI app (canonical entry: backend.app.main:app)
frontend/        React + Vite + Tailwind UI
ml_artifacts/    Model weights (Git LFS)
deploy/          Nginx config for the frontend container
```

## Configuration

Copy `config.env.example` to `config.env`. Leave API keys empty to run on local models only. Do not commit `config.env`.

If you previously committed real keys in this repository, **rotate them** at the provider (OpenAI, Google AI Studio, Anthropic). Those keys must be treated as leaked.

## Git LFS

Large `*.pth` / `*.pt` files are tracked with Git LFS. After clone:

```bash
git lfs install
git lfs pull
```

## License

MIT — see [LICENSE](LICENSE).
