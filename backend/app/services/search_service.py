from typing import List
from sqlalchemy import text, select
from sqlalchemy.orm import Session
from app.models import Note
from app.services.ai_service import generate_embedding
from app.services.vector_service import search_similar
from app.database import is_postgres


def fulltext_search(
    db: Session, query: str, user_id: int, limit: int = 20, offset: int = 0
) -> tuple[List[Note], int]:
    print(f"[DEBUG] fulltext_search 开始, query={query}, user_id={user_id}")
    try:
        if is_postgres():
            return _fulltext_search_pg(db, query, user_id, limit, offset)
        else:
            return _fulltext_search_sqlite(db, query, user_id, limit, offset)
    except Exception as e:
        print(f"[DEBUG] fulltext_search 失败: {e}")
        import traceback
        traceback.print_exc()
        return [], 0


def _fulltext_search_sqlite(
    db: Session, query: str, user_id: int, limit: int, offset: int
) -> tuple[List[Note], int]:
    count_result = db.execute(
        text("SELECT COUNT(*) FROM notes_fts WHERE notes_fts MATCH :query"),
        {"query": query},
    )
    total = count_result.scalar()

    result = db.execute(
        text(
            "SELECT n.* FROM notes n "
            "JOIN notes_fts f ON f.rowid = n.id "
            "WHERE notes_fts MATCH :query AND n.user_id = :user_id AND n.is_deleted = FALSE "
            "ORDER BY rank "
            "LIMIT :limit OFFSET :offset"
        ),
        {"query": query, "user_id": user_id, "limit": limit, "offset": offset},
    )
    rows = result.fetchall()
    note_ids = [row[0] for row in rows]

    notes = []
    if note_ids:
        note_result = db.execute(select(Note).where(Note.id.in_(note_ids)))
        notes = list(note_result.scalars().all())
        id_order = {nid: idx for idx, nid in enumerate(note_ids)}
        notes.sort(key=lambda n: id_order.get(n.id, 999))

    print(f"[DEBUG] fulltext_search (sqlite) 完成, 返回 {len(notes)} 条")
    return notes, total


def _fulltext_search_pg(
    db: Session, query: str, user_id: int, limit: int = 20, offset: int = 0
) -> tuple[List[Note], int]:
    pattern = f"%{query}%"

    count_result = db.execute(
        text("""
            SELECT COUNT(*) FROM notes
            WHERE user_id = :user_id AND is_deleted = FALSE
            AND (title ILIKE :pattern
                 OR raw_content ILIKE :pattern
                 OR summary ILIKE :pattern
                 OR keywords ILIKE :pattern)
        """),
        {"pattern": pattern, "user_id": user_id},
    )
    total = count_result.scalar()

    result = db.execute(
        text("""
            SELECT * FROM notes
            WHERE user_id = :user_id AND is_deleted = FALSE
            AND (title ILIKE :pattern
                 OR raw_content ILIKE :pattern
                 OR summary ILIKE :pattern
                 OR keywords ILIKE :pattern)
            ORDER BY
                CASE WHEN title ILIKE :pattern THEN 0
                     WHEN keywords ILIKE :pattern THEN 1
                     WHEN summary ILIKE :pattern THEN 2
                     ELSE 3 END,
                created_at DESC
            LIMIT :limit OFFSET :offset
        """),
        {"pattern": pattern, "user_id": user_id, "limit": limit, "offset": offset},
    )
    rows = result.fetchall()
    note_ids = [row[0] for row in rows]

    notes = []
    if note_ids:
        note_result = db.execute(select(Note).where(Note.id.in_(note_ids)))
        notes = list(note_result.scalars().all())
        id_order = {nid: idx for idx, nid in enumerate(note_ids)}
        notes.sort(key=lambda n: id_order.get(n.id, 999))

    print(f"[DEBUG] fulltext_search (postgres ILIKE) 完成, 返回 {len(notes)} 条")
    return notes, total


def semantic_search(
    db: Session, query: str, user_id: int, limit: int = 10
) -> List[Note]:
    print(f"[DEBUG] semantic_search 开始, query={query}, user_id={user_id}")
    try:
        embedding = generate_embedding(query)
        print(f"[DEBUG] semantic_search - embedding 生成完成, 维度: {len(embedding)}")

        similar_items = search_similar(embedding, limit=limit)
        print(f"[DEBUG] semantic_search - 向量搜索完成, 结果数: {len(similar_items)}")

        if not similar_items:
            return []

        note_ids = [item["id"] for item in similar_items]
        result = db.execute(select(Note).where(Note.id.in_(note_ids), Note.user_id == user_id, Note.is_deleted == False))
        notes = list(result.scalars().all())

        id_order = {item["id"]: idx for idx, item in enumerate(similar_items)}
        notes.sort(key=lambda n: id_order.get(n.id, 999))

        print(f"[DEBUG] semantic_search 完成, 返回 {len(notes)} 条")
        return notes
    except Exception as e:
        print(f"[DEBUG] semantic_search 失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def hybrid_search(
    db: Session, query: str, user_id: int, limit: int = 20
) -> tuple[List[Note], int]:
    print(f"[DEBUG] hybrid_search 开始, query={query}, user_id={user_id}")

    try:
        fts_notes, fts_total = fulltext_search(db, query, user_id, limit=limit)
    except Exception as e:
        print(f"[DEBUG] hybrid_search - fulltext 失败: {e}")
        fts_notes, fts_total = [], 0

    if fts_notes:
        print(f"[DEBUG] hybrid_search - 全文搜索有结果，直接返回 {len(fts_notes)} 条")
        return fts_notes[:limit], len(fts_notes)

    try:
        semantic_notes = semantic_search(db, query, user_id, limit=limit)
    except Exception as e:
        print(f"[DEBUG] hybrid_search - semantic 失败: {e}")
        semantic_notes = []

    print(f"[DEBUG] hybrid_search 完成, 返回 {len(semantic_notes)} 条")
    return semantic_notes[:limit], len(semantic_notes)
