from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import NoteCreate, NoteUpdate, NoteResponse, NoteListItem, SearchResult
from app.services.note_service import create_note_with_ai, get_note, get_notes, update_note, delete_note

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def api_create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    note = create_note_with_ai(db, note_data)
    return note


@router.get("", response_model=SearchResult)
def api_list_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    category_id: Optional[int] = None,
    source_type: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    notes, total = get_notes(db, skip, limit, category_id, source_type, keyword)
    return SearchResult(notes=notes, total=total)


@router.get("/{note_id}", response_model=NoteResponse)
def api_get_note(note_id: int, db: Session = Depends(get_db)):
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def api_update_note(
    note_id: int, note_data: NoteUpdate, db: Session = Depends(get_db)
):
    note = update_note(db, note_id, note_data)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return note


@router.delete("/{note_id}")
def api_delete_note(note_id: int, db: Session = Depends(get_db)):
    success = delete_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return {"message": "删除成功"}
