from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from .. import db
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


# -----------------
# Request / Response models
# -----------------


class ExtractRequest(BaseModel):
    text: str = Field(..., description="Source text to extract action items from")
    save_note: bool = Field(False, description="Whether to save the original note to the DB")


class ExtractItemResponse(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: Optional[int]
    items: List[ExtractItemResponse]


class ListActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


# -----------------
# Business logic helpers (kept small and testable)
# -----------------


def _process_extract(text: str, save_note: bool) -> ExtractResponse:
    """Run extraction and persist results. Returns a typed response object.

    This separates the business logic from the FastAPI route handler for easier
    testing and clearer error handling.
    """
    text = text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="text is required")

    note_id: Optional[int] = None
    try:
        if save_note:
            note_id = db.insert_note(text)
    except Exception as exc:  # defensive: translate DB errors to HTTP 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    # Extract action items using the extractor service
    try:
        items = extract_action_items(text)
    except Exception as exc:
        # If extraction fails unexpectedly, wrap as a 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    try:
        ids = db.insert_action_items(items, note_id=note_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return ExtractResponse(
        note_id=note_id,
        items=[ExtractItemResponse(id=i, text=t) for i, t in zip(ids, items)],
    )


def _process_extract_llm(text: str, save_note: bool) -> ExtractResponse:
    """Run LLM-backed extraction and persist results. Mirrors _process_extract but
    uses the LLM extractor instead of the heuristic one.
    """
    text = text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="text is required")

    note_id: Optional[int] = None
    try:
        if save_note:
            note_id = db.insert_note(text)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    try:
        items = extract_action_items_llm(text)
    except Exception as exc:
        # If the LLM call fails, return a 502 Bad Gateway since it's an external dependency
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    try:
        ids = db.insert_action_items(items, note_id=note_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return ExtractResponse(note_id=note_id, items=[ExtractItemResponse(id=i, text=t) for i, t in zip(ids, items)])


# -----------------
# Routes
# -----------------


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    return _process_extract(payload.text, payload.save_note)


@router.post("/extract/llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    """LLM-backed extraction endpoint.

    Mirrors the behavior of the heuristic /extract endpoint but uses the LLM
    extractor under the hood.
    """
    return _process_extract_llm(payload.text, payload.save_note)


@router.get("", response_model=List[ListActionItemResponse])
def list_all(note_id: Optional[int] = None) -> List[ListActionItemResponse]:
    try:
        rows = db.list_action_items(note_id=note_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return [
        ListActionItemResponse(
            id=r["id"],
            note_id=r.get("note_id"),
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


class MarkDoneRequest(BaseModel):
    done: bool = True


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> dict:
    try:
        db.mark_action_item_done(action_item_id, bool(payload.done))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    return {"id": action_item_id, "done": bool(payload.done)}


