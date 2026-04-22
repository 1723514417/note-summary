from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SearchResult
from app.services.search_service import fulltext_search, semantic_search, hybrid_search
from app.services.auth_service import get_current_user
from app.models import User

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
def api_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    mode: str = Query("hybrid", pattern="^(fts|semantic|hybrid)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if mode == "fts":
        notes, total = fulltext_search(db, q, current_user.id, limit, offset)
    elif mode == "semantic":
        notes = semantic_search(db, q, current_user.id, limit)
        total = len(notes)
    else:
        notes, total = hybrid_search(db, q, current_user.id, limit)

    return SearchResult(notes=notes, total=total)
