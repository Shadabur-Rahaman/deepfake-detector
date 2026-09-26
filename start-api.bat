@echo off
cd /d "%~dp0"
echo Stopping anything already using port 8000...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
timeout /t 2 /nobreak >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
echo Starting API on http://127.0.0.1:8000
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
