from typing import List, Optional
from sqlalchemy import select, func, delete, or_, case
from sqlalchemy.orm import Session, selectinload
from app.models import Note, Category, Tag, NoteLink, note_tags
from app.schemas import NoteCreate, NoteUpdate
from app.services.ai_service import organize_content, generate_embedding
from app.services.vector_service import add_to_vector, delete_from_vector
import datetime
import pytz
import re


def create_note_with_ai(db: Session, note_data: NoteCreate, user_id: int) -> Note:
    print(f"[DEBUG] 开始 AI 整理, 内容长度: {len(note_data.raw_content)}")
    ai_result = organize_content(note_data.raw_content)
    print(f"[DEBUG] AI 整理完成, 返回类型={type(ai_result)}, 内容={str(ai_result)[:200]}")
    if not isinstance(ai_result, dict):
        raise ValueError(f"AI 整理返回类型异常: {type(ai_result)}, 期望 dict")

    try:
        category = _ensure_category(db, ai_result.get("suggested_category", "未分类"), user_id)
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
        user_id=user_id,
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
        rebuild_links(db, note)
        db.commit()
    except Exception as e:
        print(f"[DEBUG] rebuild_links failed: {e}")
        import traceback
        traceback.print_exc()

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


def get_note(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    result = db.execute(
        select(Note).options(selectinload(Note.tags)).where(
            Note.id == note_id, Note.user_id == user_id, Note.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


def get_notes(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    source_type: Optional[str] = None,
    keyword: Optional[str] = None,
    starred: Optional[bool] = None,
) -> tuple[List[Note], int]:
    print(f"[DEBUG] get_notes 开始, user_id={user_id}, skip={skip}, limit={limit}")

    try:
        query = select(Note).where(Note.user_id == user_id, Note.is_deleted == False)
        count_query = select(func.count(Note.id)).where(Note.user_id == user_id, Note.is_deleted == False)

        if category_id:
            query = query.where(Note.category_id == category_id)
            count_query = count_query.where(Note.category_id == category_id)
        if source_type:
            query = query.where(Note.source_type == source_type)
            count_query = count_query.where(Note.source_type == source_type)
        if keyword:
            query = query.where(Note.title.contains(keyword) | Note.keywords.contains(keyword))
            count_query = count_query.where(
                Note.title.contains(keyword) | Note.keywords.contains(keyword)
            )
        if starred is not None:
            query = query.where(Note.is_starred == starred)
            count_query = count_query.where(Note.is_starred == starred)

        total_result = db.execute(count_query)
        total = total_result.scalar()

        sort_expr = [
            Note.is_pinned.desc(),
            Note.is_starred.desc(),
            Note.created_at.desc(),
        ]
        result = db.execute(
            query.order_by(*sort_expr).offset(skip).limit(limit)
        )
        notes = list(result.scalars().all())
        print(f"[DEBUG] get_notes 完成, total={total}, 数量={len(notes)}")

        return notes, total
    except Exception as e:
        print(f"[DEBUG] get_notes 失败: {e}")
        import traceback
        traceback.print_exc()
        return [], 0


def update_note(db: Session, note_id: int, note_data: NoteUpdate, user_id: int) -> Optional[Note]:
    note = get_note(db, note_id, user_id)
    if not note:
        return None

    update_data = note_data.model_dump(exclude_unset=True)
    tag_names = update_data.pop("tags", None)

    for field, value in update_data.items():
        setattr(note, field, value)

    if tag_names is not None:
        note.tags.clear()
        tags = _ensure_tags(db, tag_names)
        for tag in tags:
            note.tags.append(tag)

    db.commit()
    db.refresh(note)

    try:
        rebuild_links(db, note)
        db.commit()
    except Exception as e:
        print(f"[DEBUG] rebuild_links failed: {e}")
        import traceback
        traceback.print_exc()

    return note


def delete_note(db: Session, note_id: int, user_id: int) -> bool:
    note = get_note(db, note_id, user_id)
    if not note:
        return False

    note.is_deleted = True
    note.deleted_at = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    db.commit()
    return True


def get_trashed_notes(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[Note], int]:
    query = select(Note).options(selectinload(Note.tags)).where(
        Note.user_id == user_id, Note.is_deleted == True
    )
    count_query = select(func.count(Note.id)).where(
        Note.user_id == user_id, Note.is_deleted == True
    )

    total_result = db.execute(count_query)
    total = total_result.scalar()

    result = db.execute(
        query.order_by(Note.deleted_at.desc()).offset(skip).limit(limit)
    )
    notes = list(result.scalars().all())
    return notes, total


def restore_note(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    result = db.execute(
        select(Note).options(selectinload(Note.tags)).where(
            Note.id == note_id, Note.user_id == user_id, Note.is_deleted == True
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        return None

    if note.category_id:
        cat_result = db.execute(select(Category).where(Category.id == note.category_id))
        if not cat_result.scalar_one_or_none():
            note.category_id = None

    note.is_deleted = False
    note.deleted_at = None
    db.commit()
    db.refresh(note)
    return note


def permanent_delete_note(db: Session, note_id: int, user_id: int) -> bool:
    result = db.execute(
        select(Note).where(
            Note.id == note_id, Note.user_id == user_id, Note.is_deleted == True
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        return False

    db.delete(note)
    db.commit()

    import threading

    def _background_delete_vector():
        try:
            delete_from_vector(note_id)
        except Exception:
            pass

    threading.Thread(target=_background_delete_vector, daemon=True).start()
    return True


def purge_expired_notes(db: Session, days: int = 30) -> int:
    cutoff = datetime.datetime.now(pytz.timezone('Asia/Shanghai')) - datetime.timedelta(days=days)
    result = db.execute(
        select(Note).where(Note.is_deleted == True, Note.deleted_at < cutoff)
    )
    notes = list(result.scalars().all())
    note_ids_to_clean = [n.id for n in notes]
    for note in notes:
        db.delete(note)
    db.commit()

    if note_ids_to_clean:
        import threading

        def _background_purge_vectors():
            for nid in note_ids_to_clean:
                try:
                    delete_from_vector(nid)
                except Exception:
                    pass

        threading.Thread(target=_background_purge_vectors, daemon=True).start()

    return len(note_ids_to_clean)


def get_trash_count(db: Session, user_id: int) -> int:
    result = db.execute(
        select(func.count(Note.id)).where(Note.user_id == user_id, Note.is_deleted == True)
    )
    return result.scalar()


def toggle_star(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    note = get_note(db, note_id, user_id)
    if not note:
        return None
    note.is_starred = not note.is_starred
    db.commit()
    db.refresh(note)
    return note


def toggle_pin(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    note = get_note(db, note_id, user_id)
    if not note:
        return None
    note.is_pinned = not note.is_pinned
    db.commit()
    db.refresh(note)
    return note


_LINK_PATTERN = re.compile(r'\[\[(.+?)\]\]')


def _extract_link_titles(text: str) -> List[str]:
    if not text:
        return []
    return list(set(m.group(1).strip() for m in _LINK_PATTERN.finditer(text)))


def rebuild_links(db: Session, note: Note):
    all_text = " ".join(filter(None, [note.organized_content, note.raw_content, note.summary]))
    titles = _extract_link_titles(all_text)
    print(f"[rebuild_links] note_id={note.id}, extracted_titles={titles}")
    if not titles:
        db.execute(delete(NoteLink).where(NoteLink.source_id == note.id))
        db.flush()
        return

    db.execute(delete(NoteLink).where(NoteLink.source_id == note.id))
    db.flush()

    for title in titles:
        result = db.execute(
            select(Note).where(Note.title == title, Note.is_deleted == False)
        )
        target = result.scalar_one_or_none()
        if target and target.id != note.id:
            print(f"[rebuild_links]   matched: '{title}' -> note_id={target.id}")
            link = NoteLink(source_id=note.id, target_id=target.id)
            db.add(link)
        else:
            print(f"[rebuild_links]   no match: '{title}' (target={target})")
    db.flush()


def get_backlinks(db: Session, note_id: int, user_id: int) -> List[dict]:
    result = db.execute(
        select(NoteLink).where(NoteLink.target_id == note_id)
    )
    links = list(result.scalars().all())
    backlinks = []
    for link in links:
        note_result = db.execute(
            select(Note).where(Note.id == link.source_id, Note.user_id == user_id, Note.is_deleted == False)
        )
        source_note = note_result.scalar_one_or_none()
        if source_note:
            backlinks.append({
                "id": source_note.id,
                "title": source_note.title,
                "summary": source_note.summary,
                "created_at": source_note.created_at.isoformat() if source_note.created_at else None,
            })
    return backlinks


def get_outgoing_links(db: Session, note_id: int) -> List[dict]:
    result = db.execute(
        select(NoteLink).where(NoteLink.source_id == note_id)
    )
    links = list(result.scalars().all())
    outgoing = []
    for link in links:
        note_result = db.execute(
            select(Note).where(Note.id == link.target_id, Note.is_deleted == False)
        )
        target_note = note_result.scalar_one_or_none()
        if target_note:
            outgoing.append({
                "id": target_note.id,
                "title": target_note.title,
            })
    return outgoing


def _ensure_category(db: Session, name: str, user_id: int) -> Optional[Category]:
    if not name:
        return None
    result = db.execute(select(Category).where(Category.name == name, Category.user_id == user_id))
    category = result.scalar_one_or_none()
    if not category:
        category = Category(name=name, user_id=user_id)
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
