from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    NoteCreate, NoteUpdate, NoteResponse, NoteListItem,
    SearchResult, TrashedNoteResult, NoteLinksResponse,
)
from app.services.note_service import (
    create_note_with_ai, get_note, get_notes, update_note, delete_note,
    get_trashed_notes, restore_note, permanent_delete_note, get_trash_count,
    toggle_star, toggle_pin, get_backlinks, get_outgoing_links,
)
from app.services.auth_service import get_current_user
from app.models import User

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def api_create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = create_note_with_ai(db, note_data, current_user.id)
    return note


@router.get("", response_model=SearchResult)
def api_list_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    source_type: Optional[str] = None,
    keyword: Optional[str] = None,
    starred: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes, total = get_notes(db, current_user.id, skip, limit, category_id, source_type, keyword, starred)
    return SearchResult(notes=notes, total=total)


@router.get("/trash/list", response_model=TrashedNoteResult)
def api_list_trash(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes, total = get_trashed_notes(db, current_user.id, skip, limit)
    return TrashedNoteResult(notes=notes, total=total)


@router.get("/trash/count")
def api_trash_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = get_trash_count(db, current_user.id)
    return {"count": count}


@router.get("/{note_id}", response_model=NoteResponse)
def api_get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return note


@router.get("/{note_id}/links", response_model=NoteLinksResponse)
def api_get_note_links(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    backlinks = get_backlinks(db, note_id, current_user.id)
    outgoing = get_outgoing_links(db, note_id)
    return NoteLinksResponse(backlinks=backlinks, outgoing=outgoing)


@router.put("/{note_id}", response_model=NoteResponse)
def api_update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = update_note(db, note_id, note_data, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return note


@router.delete("/{note_id}")
def api_delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = delete_note(db, note_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return {"message": "删除成功"}


@router.post("/{note_id}/star", response_model=NoteResponse)
def api_toggle_star(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = toggle_star(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return note


@router.post("/{note_id}/pin", response_model=NoteResponse)
def api_toggle_pin(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = toggle_pin(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return note


@router.post("/{note_id}/restore", response_model=NoteResponse)
def api_restore_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = restore_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return note


@router.delete("/{note_id}/permanent")
def api_permanent_delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = permanent_delete_note(db, note_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="笔记未找到")
    return {"message": "已永久删除"}
