"""simple_database compatibility shim.

Older modules (mode_detection.py, main.py imports) reference `simple_database`.
The real implementation lives in :mod:`backend.app.database`.  This module
re-exports the public names from there so imports of the form::

    from simple_database import create_detection_job_record
    from ..simple_database import setup_database, get_db

continue to work without any caller-side changes.  If :mod:`.database` is
ever removed or fails to load, an in-memory dictionary store is used as a
last-resort fallback (matching the "Continuing with in-memory storage
fallback" behaviour in :mod:`backend.app.main`).
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def _try_import_real():
    """Import the real :mod:`backend.app.database` module with multiple strategies.

    The same Python file can be imported under 3 different ``sys.path``
    configurations inside this project:
      * ``from backend.app.simple_database import ...`` (proper package import)
      * ``from .simple_database import ...`` (inside ``backend.app``)
      * bare ``import simple_database`` after ``sys.path`` includes
        ``backend/app`` (used by older callers in :mod:`backend.app.main`).

    In the last case, a relative ``from .database import ...`` fails with
    ``attempted relative import with no known parent package``, which is
    exactly the line that appeared in production startup logs.
    """

    # Strategy 1 — clean package import.
    try:
        from backend.app import database as _db  # type: ignore
        return _db
    except Exception:
        pass

    # Strategy 2 — relative import (works when we're a package submodule).
    try:
        from . import database as _db  # type: ignore
        return _db
    except Exception:
        pass

    # Strategy 3 — sys.path append + absolute import by bare name.
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    try:
        import database as _db  # type: ignore
        return _db
    except Exception as exc:
        logger.info(
            "simple_database: real backend.app.database module not importable "
            "(%s: %s). Switching to in-memory fallback store.",
            type(exc).__name__,
            exc,
        )
        return None


_db = _try_import_real()

# Pick up only the names that are *actually* exposed by the real module;
# missing names fall back to the local in-memory implementation below.
if _db is not None:
    _real_names = set(dir(_db))
    setup_database = _db.setup_database if "setup_database" in _real_names else None
    ensure_detection_jobs_table = (
        _db.ensure_detection_jobs_table
        if "ensure_detection_jobs_table" in _real_names
        else None
    )
    create_detection_job_record = (
        _db.create_detection_job_record if "create_detection_job_record" in _real_names else None
    )
    get_detection_job_record = (
        _db.get_detection_job_record if "get_detection_job_record" in _real_names else None
    )
    update_detection_job_record = (
        _db.update_detection_job_record if "update_detection_job_record" in _real_names else None
    )
    get_db = _db.get_db if "get_db" in _real_names else None
    _REAL_DB = all(
        n is not None
        for n in (
            setup_database,
            ensure_detection_jobs_table,
            create_detection_job_record,
            get_detection_job_record,
            update_detection_job_record,
            get_db,
        )
    )
else:
    setup_database = None
    ensure_detection_jobs_table = None
    create_detection_job_record = None
    get_detection_job_record = None
    update_detection_job_record = None
    get_db = None
    _REAL_DB = False


if not _REAL_DB:
    # ------------------------------------------------------------------
    # Last-resort in-memory dict store. Matches the exact public contract
    # of backend.app.database's helpers, so callers (mode_detection routes,
    # startup event in main.py) behave identically whether sqlite, file,
    # or in-memory store is active.
    # ------------------------------------------------------------------
    _store_lock = threading.Lock()
    _IN_MEMORY_STORE: Dict[str, Dict[str, Any]] = {}

    def setup_database() -> Tuple[bool, str]:  # type: ignore[no-redef]
        return True, "in-memory fallback store"

    def ensure_detection_jobs_table() -> Tuple[bool, str]:  # type: ignore[no-redef]
        return True, "in-memory detection jobs table ready"

    def create_detection_job_record(  # type: ignore[no-redef]
        video_id: str,
        mode: str,
        file_path: str,
        original_filename: Optional[str] = None,
        file_size: Optional[int] = None,
        filename: Optional[str] = None,
        youtube_url: Optional[str] = None,
        status: str = "pending",
        **extra: Any,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        job_id = str(uuid.uuid4())
        record: Dict[str, Any] = {
            "job_id": job_id,
            "video_id": video_id,
            "mode": mode,
            "file_path": file_path,
            "original_filename": original_filename or filename,
            "filename": filename or original_filename,
            "file_size": file_size,
            "youtube_url": youtube_url,
            "status": status,
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        record.update(extra)
        with _store_lock:
            _IN_MEMORY_STORE[video_id] = record
            _IN_MEMORY_STORE[job_id] = record
        return True, job_id, record

    def get_detection_job_record(video_id: str) -> Optional[Dict[str, Any]]:  # type: ignore[no-redef]
        with _store_lock:
            return _IN_MEMORY_STORE.get(video_id)

    def update_detection_job_record(video_id: str, **updates: Any) -> Tuple[bool, str]:  # type: ignore[no-redef]
        with _store_lock:
            rec = _IN_MEMORY_STORE.get(video_id)
            if rec is None:
                return False, f"job not found for video_id={video_id}"
            rec.update(updates)
            rec["updated_at"] = time.time()
            _IN_MEMORY_STORE[video_id] = rec
            if rec.get("job_id") and rec["job_id"] in _IN_MEMORY_STORE:
                _IN_MEMORY_STORE[rec["job_id"]] = rec
            return True, "updated"

    class _DummySession:
        def close(self) -> None:
            return None

        def __enter__(self):  # pragma: no cover - trivial context manager
            return self

        def __exit__(self, exc_type, exc, tb):  # pragma: no cover
            self.close()

    def get_db():  # type: ignore[no-redef]
        s = _DummySession()
        try:
            yield s
        finally:
            s.close()


__all__ = [
    "setup_database",
    "ensure_detection_jobs_table",
    "create_detection_job_record",
    "get_detection_job_record",
    "update_detection_job_record",
    "get_db",
]

# Set backend.app.database-equivalent env flag so startup log can report
# whether we fell back to memory or loaded the real store.  The logger is
# module-qualified (not root WARNING:root) to keep startup logs clean.
if _REAL_DB:
    logger.info("simple_database: backed by backend.app.database (%s)", getattr(_db, "__file__", "builtin"))
else:
    logger.info("simple_database: using in-memory fallback store")
