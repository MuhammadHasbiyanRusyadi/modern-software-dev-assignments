# Week 2 — Action Item Extractor

This folder contains a small FastAPI application that extracts action items from free-form text, persists notes and action items to a local SQLite database, and exposes both a heuristic extractor and an LLM-backed extractor (using the Ollama Python client).

## What it contains

- FastAPI backend (application factory in `app/main.py`). The app serves a minimal frontend from `frontend/index.html` at `/` and static files under `/static`.
- SQLite persistence implemented in `app/db.py`. Database file lives in `app/data/app.db` and tables are created automatically on startup by `init_db()`.
- Heuristic extractor in `app/services/extract.py` as `extract_action_items(text: str) -> list[str]`.
- LLM-backed extractor in the same file as `extract_action_items_llm(text: str) -> list[str]` which calls `ollama.chat` and expects structured JSON output; it falls back to the heuristic extractor on errors.
- Routers in `app/routers`:
  - `notes.py` — create/list/get notes
  - `action_items.py` — extract action items (heuristic and LLM), list action items, mark items done
- Tests under `tests/` (pytest): `tests/test_extract.py` covers the extractors and mocks the Ollama `chat` function.

## Quick start (development)

1. Install dependencies (project uses Poetry / pyproject.toml). If you use Poetry:

```powershell
poetry install
poetry run uvicorn week2.app.main:app --reload
```

Or using plain Python if dependencies are already installed:

```powershell
python -m uvicorn week2.app.main:app --reload
```

2. Open the frontend at: http://127.0.0.1:8000/

Notes:
- On startup the app will ensure `app/data/app.db` exists and will create the `notes` and `action_items` tables.
- The app-level DB initialization happens during the FastAPI lifespan (startup) via `init_db()`.

## Endpoints

The following table lists the primary API endpoints implemented by the app.

| Path | Method | Request | Response | Notes |
|------|--------|---------|----------|-------|
| `/` | GET | — | HTML | Serves `frontend/index.html` (simple UI)
| `/static/*` | GET | — | static files | Frontend assets mounted at `/static`
| `/notes` | POST | JSON `{ "content": "..." }` | `{ "id": int, "content": str, "created_at": str }` | Create a note
| `/notes` | GET | — | `[{ "id":..., "content":..., "created_at":... }, ...]` | List saved notes
| `/notes/{note_id}` | GET | — | `{ "id":..., "content":..., "created_at":... }` | Get a single note or 404 if not found
| `/action-items/extract` | POST | JSON `{ "text": "...", "save_note": false }` | `{ "note_id": int|null, "items": [{"id":int, "text":str}, ...] }` | Heuristic extraction (bullet markers, keywords, checkboxes, fallback heuristics)
| `/action-items/extract/llm` | POST | JSON `{ "text": "...", "save_note": false }` | `{ "note_id": int|null, "items": [{"id":int, "text":str}, ...] }` | LLM-backed extraction using Ollama; returns same response shape as heuristic endpoint
| `/action-items` | GET | Query `note_id` optional | `[{ "id":..., "note_id":..., "text":..., "done":bool, "created_at":... }, ...]` | List action items; optionally filter by note
| `/action-items/{action_item_id}/done` | POST | JSON `{ "done": true|false }` | `{ "id": int, "done": bool }` | Mark an action item done/undone

All endpoints use JSON request/response bodies (except `/` which serves HTML). The project uses Pydantic models in the routers to validate request/response shapes.

## Extraction details

- Heuristic extractor (`extract_action_items`):
  - Detects bullet lines (leading `-`, `*`, `•`, or numbered like `1.`) and lines prefixed with keywords such as `todo:`, `action:`, `next:`.
  - Recognizes checkbox markers like `[ ]` or `[todo]` and trims them.
  - If no explicit lines are found, falls back to splitting the text into sentences and selects sentences that look imperative (starts with verbs like `add`, `create`, `implement`, `fix`, etc.).
  - Deduplicates extracted items case-insensitively while preserving order.

- LLM-backed extractor (`extract_action_items_llm`):
  - Calls `ollama.chat(...)` with a JSON schema in the `format` argument requesting a JSON object with an `action_items` array of strings.
  - Uses the `OLLAMA_MODEL` environment variable if set (defaults to `llama3.1:8b` in code) and sets a low temperature.
  - Attempts to parse the model's response as JSON (resilient to code fences). If parsing fails, or if the model call raises, it falls back to the heuristic extractor.
  - Deduplicates results case-insensitively and returns a list of strings.

## Persistence (SQLite)

- Database file: `week2/app/data/app.db` (created automatically).
- Tables created by `init_db()`:
  - `notes(id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')))`
  - `action_items(id INTEGER PRIMARY KEY AUTOINCREMENT, note_id INTEGER, text TEXT NOT NULL, done INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`
- DB helper functions are in `app/db.py` (convenience functions for inserting/listing notes and action items, marking done, etc.).

## Tests

- Pytest-based tests are in `week2/tests/test_extract.py`.
- Tests cover:
  - Heuristic extraction behavior (bullets, checkboxes).
  - LLM extraction behavior using `monkeypatch` to mock the `ollama.chat` client (valid JSON response, empty input, duplicate handling, invalid JSON fallback).

Run tests with:

```powershell
poetry run pytest -q
# or
pytest -q
```

## Notes / Requirements

- The LLM-backed extraction requires the `ollama` Python package and access to an Ollama model server or runtime. If you don't have Ollama available, the LLM endpoint may fall back to the heuristic extractor (depending on errors and how the server responds) or the `extract_action_items_llm` function will fall back to the heuristic locally when it cannot call the model successfully.
- The frontend (`frontend/index.html`) provides a minimal UI with buttons for "Extract", "Extract LLM" and "List Notes" that call the corresponding endpoints.

## Where to look in the code

- Application entry / app factory: `week2/app/main.py`
- Routers: `week2/app/routers/notes.py`, `week2/app/routers/action_items.py`
- Extraction logic: `week2/app/services/extract.py`
- SQLite helpers and schema init: `week2/app/db.py`
- Frontend: `week2/frontend/index.html`
- Tests: `week2/tests/test_extract.py`

If you'd like, I can also run the test suite now and report results, or add example curl requests for some endpoints. Let me know which you'd prefer.