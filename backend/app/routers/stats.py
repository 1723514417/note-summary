from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Note, Category, Tag
from app.services.auth_service import get_current_user
from app.models import User
import datetime
import pytz

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
def api_stats_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uid = current_user.id

    note_count = db.execute(
        select(func.count(Note.id)).where(Note.user_id == uid, Note.is_deleted == False)
    ).scalar() or 0

    category_count = db.execute(
        select(func.count(Category.id)).where(Category.user_id == uid)
    ).scalar() or 0

    tag_count = db.execute(
        select(func.count(Tag.id))
    ).scalar() or 0

    starred_count = db.execute(
        select(func.count(Note.id)).where(Note.user_id == uid, Note.is_deleted == False, Note.is_starred == True)
    ).scalar() or 0

    trashed_count = db.execute(
        select(func.count(Note.id)).where(Note.user_id == uid, Note.is_deleted == True)
    ).scalar() or 0

    source_dist_result = db.execute(
        select(Note.source_type, func.count(Note.id))
        .where(Note.user_id == uid, Note.is_deleted == False)
        .group_by(Note.source_type)
    )
    source_distribution = [
        {"type": row[0] or "未分类", "count": row[1]}
        for row in source_dist_result
    ]

    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.datetime.now(tz).date()
    daily_counts = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_start = tz.localize(datetime.datetime.combine(day, datetime.time.min))
        day_end = tz.localize(datetime.datetime.combine(day, datetime.time.max))
        count = db.execute(
            select(func.count(Note.id)).where(
                Note.user_id == uid,
                Note.is_deleted == False,
                Note.created_at >= day_start,
                Note.created_at <= day_end,
            )
        ).scalar() or 0
        daily_counts.append({"date": day.isoformat(), "count": count})

    return {
        "note_count": note_count,
        "category_count": category_count,
        "tag_count": tag_count,
        "starred_count": starred_count,
        "trashed_count": trashed_count,
        "source_distribution": source_distribution,
        "daily_counts": daily_counts,
    }
