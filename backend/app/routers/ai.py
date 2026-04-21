from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OrganizeRequest, OrganizeResponse, ResearchRequest, ResearchResponse, NoteListItem, NoteUpdate
from app.services.ai_service import organize_content, research_topic, expand_note
from app.services.note_service import get_note, update_note

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/organize", response_model=OrganizeResponse)
def api_organize(request: OrganizeRequest):
    result = organize_content(request.raw_content)
    return OrganizeResponse(**result)


@router.post("/research", response_model=ResearchResponse)
def api_research(request: ResearchRequest, db: Session = Depends(get_db)):
    existing_content = ""
    related_notes = []

    if request.note_id:
        note = get_note(db, request.note_id)
        if not note:
            raise HTTPException(status_code=404, detail="笔记未找到")
        existing_content = f"标题: {note.title}\n内容: {note.organized_content or note.raw_content}"
        related_notes.append(NoteListItem.model_validate(note))
        topic = note.title
    elif request.topic:
        topic = request.topic
    else:
        raise HTTPException(status_code=400, detail="请提供 note_id 或 topic")

    if request.note_id:
        research_content = expand_note(
            title=topic,
            content=existing_content,
        )
    else:
        research_content = research_topic(
            topic=topic,
            existing_content=existing_content,
        )

    if request.note_id:
        update_note(db, request.note_id, NoteUpdate(
            research_content=research_content,
        ))

    return ResearchResponse(
        research_content=research_content,
        related_notes=related_notes,
    )
