from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from .. import db


router = APIRouter(prefix="/notes", tags=["notes"])


class CreateNoteRequest(BaseModel):
    content: str = Field(..., description="Note text")


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


def _create_note(content: str) -> NoteResponse:
    content = (content or "").strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="content is required")
    try:
        note_id = db.insert_note(content)
        note = db.get_note(note_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    if note is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to retrieve created note")
    return NoteResponse(id=note["id"], content=note["content"], created_at=note["created_at"])


def _get_note(note_id: int) -> NoteResponse:
    try:
        row = db.get_note(note_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="note not found")
    return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])


@router.post("", response_model=NoteResponse)
def create_note(payload: CreateNoteRequest) -> NoteResponse:
    return _create_note(payload.content)


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    return _get_note(note_id)


@router.get("", response_model=List[NoteResponse])
def list_notes() -> List[NoteResponse]:
    try:
        rows = db.list_notes()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return [NoteResponse(id=r["id"], content=r["content"], created_at=r["created_at"]) for r in rows]


