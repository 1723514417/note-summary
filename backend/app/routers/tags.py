from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tag, Note, note_tags
from app.schemas import TagResponse, NoteListItem

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
def api_list_tags(db: Session = Depends(get_db)):
    result = db.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars().all())


@router.get("/{tag_id}/notes", response_model=list[NoteListItem])
def api_get_tag_notes(
    tag_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(Note)
        .join(note_tags, Note.id == note_tags.c.note_id)
        .where(note_tags.c.tag_id == tag_id)
        .order_by(Note.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())
