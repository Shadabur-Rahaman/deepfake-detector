"""SPA static-asset and catch-all helpers for FastAPI + built Vite/React frontend.

Exposes two helpers:

- mount_spa(app, dist_dir) -> None
    Mounts StaticFiles at "/" with html=True so the built frontend is served
    same-origin from the FastAPI process. Skips silently if dist_dir does not
    exist (pure-API deployments still work).

- add_spa_catchall(app, dist_dir) -> None
    Appends a literal-last GET /* route that serves dist_dir/index.html for
    deep-link browser refreshes (/detection, /account, /try, etc). The
    catch-all:

      * Only runs for GET requests.
      * Only runs for paths that don't look like a file (no extension) OR
        Accept: text/html header is present.
      * Explicitly excludes API prefixes, mounted static paths, WebSocket
        paths, /docs, /redoc, and /openapi.json so those continue to return
        FastAPI's native JSON 404 / WebSocket upgrade.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

_RESERVED_PREFIXES = (
    "/api/",
    "/v1/",
    "/ws",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/openapi.yaml",
    "/uploaded_videos/",
    "/downloaded_videos/",
    "/ml_artifacts/",
    "/videos/",
    "/assets/",  # Vite already serves own assets via StaticFiles
)


def mount_spa(app: FastAPI, dist_dir: str | os.PathLike[str]) -> bool:
    dist = Path(dist_dir)
    index_html = dist / "index.html"
    if not dist.is_dir() or not index_html.is_file():
        logger.warning(
            "SPA frontend not mounted: %s/index.html not found. "
            "Run `cd frontend && npm run build` or set VITE_API_URL and "
            "serve frontend separately.",
            str(dist),
        )
        return False
    # StaticFiles(html=True) serves "/" -> index.html and unknown leaf paths
    # that don't match a static asset -> index.html. We still add the explicit
    # catch-all below for nested paths like /detection/sub because StaticFiles
    # with html=True only handles single missing files.
    app.mount("/", StaticFiles(directory=str(dist), html=True), name="spa_static")
    logger.info("[OK] SPA frontend mounted at / (dist=%s)", str(dist))
    return True


def _looks_like_static_asset(path: str) -> bool:
    # Paths with a dot in their last segment are treated as asset requests
    # (image.png, style.css, app.abc123.js). Only fall back to index.html for
    # browser-looking routes.
    last = path.rstrip("/").rsplit("/", 1)[-1]
    if not last:
        return False
    return "." in last


def add_spa_catchall(app: FastAPI, dist_dir: str | os.PathLike[str]) -> Optional[Path]:
    dist = Path(dist_dir)
    index_html = dist / "index.html"
    if not index_html.is_file():
        return None

    # Use mount_path prefix so /assets resolve correctly for non-root Vite
    # deployments (VITE_BASE_PATH). Default = "/".
    index_body = index_html.read_text(encoding="utf-8")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def _spa_catchall(request: Request, full_path: str):  # type: ignore[no-redef]
        req_path = "/" + full_path
        for prefix in _RESERVED_PREFIXES:
            if req_path.startswith(prefix):
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="Not Found")

        accept = request.headers.get("accept", "")
        wants_html = "text/html" in accept or "*/*" in accept
        if not wants_html and _looks_like_static_asset(req_path):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")

        return HTMLResponse(content=index_body, media_type="text/html")

    return index_html
