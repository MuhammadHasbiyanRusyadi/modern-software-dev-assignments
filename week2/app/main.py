from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import action_items, notes


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Application lifespan: initialize resources here."""
    # initialize DB (keeps previous behavior but during startup)
    init_db()
    yield


def create_app() -> FastAPI:
    """Application factory for easier testing and lifecycle control."""
    app = FastAPI(title="Action Item Extractor", lifespan=_lifespan)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        return html_path.read_text(encoding="utf-8")

    app.include_router(notes.router)
    app.include_router(action_items.router)

    static_dir = Path(__file__).resolve().parents[1] / "frontend"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    return app


# Module-level application for normal execution
app = create_app()