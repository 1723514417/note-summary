from typing import List
from sqlalchemy import text, select
from sqlalchemy.orm import Session
from app.models import Note
from app.services.ai_service import generate_embedding
from app.services.vector_service import search_similar


def fulltext_search(
    db: Session, query: str, limit: int = 20, offset: int = 0
) -> tuple[List[Note], int]:
    print(f"[DEBUG] fulltext_search 开始, query={query}")
    try:
        count_result = db.execute(
            text("SELECT COUNT(*) FROM notes_fts WHERE notes_fts MATCH :query"),
            {"query": query},
        )
        total = count_result.scalar()
        print(f"[DEBUG] fulltext_search - count 完成, total={total}")

        result = db.execute(
            text(
                "SELECT n.* FROM notes n "
                "JOIN notes_fts f ON f.rowid = n.id "
                "WHERE notes_fts MATCH :query "
                "ORDER BY rank "
                "LIMIT :limit OFFSET :offset"
            ),
            {"query": query, "limit": limit, "offset": offset},
        )
        rows = result.fetchall()
        note_ids = [row[0] for row in rows]
        print(f"[DEBUG] fulltext_search - 匹配到 {len(note_ids)} 个结果")

        notes = []
        if note_ids:
            note_result = db.execute(select(Note).where(Note.id.in_(note_ids)))
            notes = list(note_result.scalars().all())
            id_order = {nid: idx for idx, nid in enumerate(note_ids)}
            notes.sort(key=lambda n: id_order.get(n.id, 999))

        print(f"[DEBUG] fulltext_search 完成, 返回 {len(notes)} 条")
        return notes, total
    except Exception as e:
        print(f"[DEBUG] fulltext_search 失败: {e}")
        import traceback
        traceback.print_exc()
        return [], 0


def semantic_search(
    db: Session, query: str, limit: int = 10
) -> List[Note]:
    print(f"[DEBUG] semantic_search 开始, query={query}")
    try:
        embedding = generate_embedding(query)
        print(f"[DEBUG] semantic_search - embedding 生成完成, 维度: {len(embedding)}")
        
        similar_items = search_similar(embedding, limit=limit)
        print(f"[DEBUG] semantic_search - 向量搜索完成, 结果数: {len(similar_items)}")

        if not similar_items:
            return []

        note_ids = [item["id"] for item in similar_items]
        result = db.execute(select(Note).where(Note.id.in_(note_ids)))
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
    db: Session, query: str, limit: int = 20
) -> tuple[List[Note], int]:
    print(f"[DEBUG] hybrid_search 开始, query={query}")
    
    # 先执行全文搜索
    try:
        fts_notes, fts_total = fulltext_search(db, query, limit=limit)
    except Exception as e:
        print(f"[DEBUG] hybrid_search - fulltext 失败: {e}")
        fts_notes, fts_total = [], 0
    
    # 如果全文搜索有结果，直接返回，不进行向量搜索（避免 ChromaDB 卡住）
    if fts_notes:
        print(f"[DEBUG] hybrid_search - 全文搜索有结果，直接返回 {len(fts_notes)} 条")
        return fts_notes[:limit], len(fts_notes)
    
    # 如果全文搜索无结果，再尝试向量搜索
    try:
        semantic_notes = semantic_search(db, query, limit=limit)
    except Exception as e:
        print(f"[DEBUG] hybrid_search - semantic 失败: {e}")
        semantic_notes = []

    print(f"[DEBUG] hybrid_search 完成, 返回 {len(semantic_notes)} 条")
    return semantic_notes[:limit], len(semantic_notes)
