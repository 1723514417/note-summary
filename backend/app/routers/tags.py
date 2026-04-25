from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tag, Note, note_tags
from app.schemas import TagResponse, NoteListItem
from app.services.auth_service import get_current_user
from app.models import User
from pydantic import BaseModel

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
    current_user: User = Depends(get_current_user),
):
    result = db.execute(
        select(Note)
        .join(note_tags, Note.id == note_tags.c.note_id)
        .where(note_tags.c.tag_id == tag_id, Note.user_id == current_user.id, Note.is_deleted == False)
        .order_by(Note.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


class TagRename(BaseModel):
    name: str


@router.put("/{tag_id}", response_model=TagResponse)
def api_rename_tag(
    tag_id: int,
    data: TagRename,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签未找到")

    new_name = data.name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="标签名不能为空")

    existing = db.execute(select(Tag).where(Tag.name == new_name, Tag.id != tag_id)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="标签名已存在")

    tag.name = new_name
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}")
def api_delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签未找到")

    db.execute(delete(note_tags).where(note_tags.c.tag_id == tag_id))
    db.delete(tag)
    db.commit()
    return {"message": "标签已删除"}
