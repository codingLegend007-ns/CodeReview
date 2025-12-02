"""FastAPI application serving the local UI frontend."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
UI_DIR = PROJECT_ROOT / "ui"
HOME_PAGE = UI_DIR / "home.html"

app = FastAPI(
    title="AI Code Review Frontend",
    description="Serves the local HTML interface for running AI-powered PR reviews.",
    version="0.1.0",
)

"""
// New doc for comitment
"""
@app.get("/", include_in_schema=False)
async def read_home() -> FileResponse:
    """Return the single-page frontend application."""
    if not HOME_PAGE.exists():
        raise HTTPException(status_code=500, detail="UI home.html file not found")
    return FileResponse(HOME_PAGE)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
