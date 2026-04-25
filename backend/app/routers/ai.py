import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OrganizeRequest, OrganizeResponse, ResearchRequest, ResearchResponse, NoteListItem, NoteUpdate
from app.services.ai_service import organize_content, research_topic, expand_note
from app.services.note_service import get_note, update_note
from app.services.auth_service import get_current_user
from app.models import User

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/organize", response_model=OrganizeResponse)
def api_organize(request: OrganizeRequest, current_user: User = Depends(get_current_user)):
    result = organize_content(request.raw_content)
    return OrganizeResponse(**result)


@router.post("/research")
def api_research(
    request: ResearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_content = ""
    related_notes = []

    if request.note_id:
        note = get_note(db, request.note_id, current_user.id)
        if not note:
            raise HTTPException(status_code=404, detail="笔记未找到")
        existing_content = f"标题: {note.title}\n内容: {note.organized_content or note.raw_content}"
        related_notes.append(NoteListItem.model_validate(note))
        topic = note.title
    elif request.topic:
        topic = request.topic
    else:
        raise HTTPException(status_code=400, detail="请提供 note_id 或 topic")

    def generate():
        yield _sse_event({"stage": "preparing", "message": "正在准备调研内容..."})

        yield _sse_event({"stage": "researching", "message": "AI 正在深度调研，请稍候..."})

        try:
            if request.note_id:
                research_content = expand_note(title=topic, content=existing_content)
            else:
                research_content = research_topic(topic=topic, existing_content=existing_content)

            yield _sse_event({"stage": "saving", "message": "调研完成，正在保存..."})

            if request.note_id:
                update_note(db, request.note_id, NoteUpdate(research_content=research_content), current_user.id)

            yield _sse_event({
                "stage": "complete",
                "message": "调研完成",
                "research_content": research_content,
                "related_notes": [n.model_dump(mode="json") for n in related_notes],
            })
        except Exception as e:
            yield _sse_event({"stage": "error", "message": str(e)})

    return StreamingResponse(generate(), media_type="text/event-stream")
