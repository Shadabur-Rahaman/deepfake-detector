# Procfile — Heroku / Render (buildpack deploy) / Railway
# One-command zero-config production entrypoint.  All PaaS platforms that
# support a Procfile (Heroku, Dokku, Render buildpacks, Railway legacy, Clever Cloud)
# will pick the `web` process up and run gunicorn multi-worker on whatever
# $PORT the platform assigns.  FORCE_CPU_MODE=1 keeps PyTorch from trying to
# initialise CUDA on CPU-only cloud instances.
#
# If gunicorn is unavailable (e.g. minimal Python image) the fallback command
# in Procfile.fallback runs uvicorn with the same semantics.  Keep this file
# in sync with the Dockerfile CMD and run.py.
web: FORCE_CPU_MODE=1 PYTHONUNBUFFERED=1 python -m gunicorn backend.app.main:app -c gunicorn.conf.py --worker-tmp-dir /dev/shm
