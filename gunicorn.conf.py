import os
import multiprocessing

_max_workers = int(os.getenv("GUNICORN_MAX_WORKERS", "4"))
_cpu = max(1, multiprocessing.cpu_count())
workers = int(os.getenv("GUNICORN_WORKERS", str(min(_cpu, _max_workers))))
worker_class = "uvicorn.workers.UvicornWorker"
threads = 2

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "8000")
bind = os.getenv("GUNICORN_BIND", f"{host}:{port}")

timeout = int(os.getenv("GUNICORN_TIMEOUT", "180"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "60"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "10"))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "500"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))

preload_app = os.getenv("GUNICORN_PRELOAD", "false").lower() in ("1", "true", "yes")
reload = False

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "INFO").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss'

proxy_allow_ips = "*"
forwarded_allow_ips = "*"
