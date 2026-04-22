from typing import List, Optional
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session, selectinload
from app.models import Note, Category, Tag, note_tags
from app.schemas import NoteCreate, NoteUpdate
from app.services.ai_service import organize_content, generate_embedding
from app.services.vector_service import add_to_vector, delete_from_vector


def create_note_with_ai(db: Session, note_data: NoteCreate) -> Note:
    print(f"[DEBUG] 开始 AI 整理, 内容长度: {len(note_data.raw_content)}")
    ai_result = organize_content(note_data.raw_content)
    print(f"[DEBUG] AI 整理完成, 标题: {ai_result.get('title')}")

    try:
        category = _ensure_category(db, ai_result.get("suggested_category", "未分类"))
        print(f"[DEBUG] 分类完成: {category.name if category else None}, id={category.id if category else None}")
    except Exception as e:
        print(f"[DEBUG] 分类失败: {e}")
        raise

    note = Note(
        title=ai_result["title"],
        raw_content=note_data.raw_content,
        organized_content=ai_result["organized_content"],
        summary=ai_result["summary"],
        category_id=category.id if category else note_data.category_id,
        keywords=ai_result.get("keywords", ""),
        source_type=ai_result.get("source_type", note_data.source_type or "knowledge"),
    )
    db.add(note)
    db.flush()
    print(f"[DEBUG] Note flushed, id={note.id}")

    tags = _ensure_tags(db, ai_result.get("suggested_tags", []))
    for tag in tags:
        note.tags.append(tag)

    db.commit()
    db.refresh(note)
    print(f"[DEBUG] Note committed, id={note.id}")

    try:
        text_for_embedding = f"{note.title} {note.raw_content} {note.summary or ''}"
        print(f"[DEBUG] 开始生成 embedding...")
        embedding = generate_embedding(text_for_embedding)
        print(f"[DEBUG] Embedding 生成完成, 维度: {len(embedding)}")

        try:
            print(f"[DEBUG] 开始向量存储...")
            add_to_vector(note.id, text_for_embedding, embedding)
            print(f"[DEBUG] 向量存储完成")
        except Exception as ve:
            print(f"[DEBUG] 向量存储失败: {ve}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"[DEBUG] Embedding 失败: {e}")
        import traceback
        traceback.print_exc()

    return note


def get_note(db: Session, note_id: int) -> Optional[Note]:
    result = db.execute(
        select(Note).options(selectinload(Note.tags)).where(Note.id == note_id)
    )
    return result.scalar_one_or_none()


def get_notes(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    source_type: Optional[str] = None,
    keyword: Optional[str] = None,
) -> tuple[List[Note], int]:
    print(f"[DEBUG] get_notes 开始, skip={skip}, limit={limit}, category_id={category_id}, source_type={source_type}, keyword={keyword}")
    
    try:
        query = select(Note)
        count_query = select(func.count(Note.id))
        print(f"[DEBUG] get_notes - 构建查询完成")

        if category_id:
            query = query.where(Note.category_id == category_id)
            count_query = count_query.where(Note.category_id == category_id)
            print(f"[DEBUG] get_notes - 分类过滤完成")
        if source_type:
            query = query.where(Note.source_type == source_type)
            count_query = count_query.where(Note.source_type == source_type)
            print(f"[DEBUG] get_notes - 来源类型过滤完成")
        if keyword:
            query = query.where(Note.title.contains(keyword) | Note.keywords.contains(keyword))
            count_query = count_query.where(
                Note.title.contains(keyword) | Note.keywords.contains(keyword)
            )
            print(f"[DEBUG] get_notes - 关键词过滤完成")

        print(f"[DEBUG] get_notes - 开始执行 count 查询")
        total_result = db.execute(count_query)
        total = total_result.scalar()
        print(f"[DEBUG] get_notes - count 查询完成, total={total}")

        print(f"[DEBUG] get_notes - 开始执行列表查询")
        result = db.execute(
            query.order_by(Note.created_at.desc()).offset(skip).limit(limit)
        )
        notes = list(result.scalars().all())
        print(f"[DEBUG] get_notes - 列表查询完成, 数量={len(notes)}")
        
        return notes, total
    except Exception as e:
        print(f"[DEBUG] get_notes 失败: {e}")
        import traceback
        traceback.print_exc()
        return [], 0


def update_note(db: Session, note_id: int, note_data: NoteUpdate) -> Optional[Note]:
    note = get_note(db, note_id)
    if not note:
        return None

    update_data = note_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: int) -> bool:
    note = get_note(db, note_id)
    if not note:
        return False
    
    # 直接删除 note，note_tags 会通过外键级联删除
    db.delete(note)
    db.commit()

    # 后台执行向量删除，不阻塞主流程
    import threading
    
    def _background_delete_vector():
        try:
            delete_from_vector(note_id)
        except Exception:
            pass
    
    threading.Thread(target=_background_delete_vector, daemon=True).start()
    return True


def _ensure_category(db: Session, name: str) -> Optional[Category]:
    if not name:
        return None
    result = db.execute(select(Category).where(Category.name == name))
    category = result.scalar_one_or_none()
    if not category:
        category = Category(name=name)
        db.add(category)
        db.flush()
    return category


def _ensure_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    tags = []
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        result = db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalar_one_or_none()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags
