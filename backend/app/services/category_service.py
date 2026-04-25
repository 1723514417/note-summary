from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Category, Note
from app.schemas import CategoryCreate, CategoryUpdate


def get_categories(db: Session, user_id: int) -> List[Category]:
    result = db.execute(
        select(Category).where(Category.parent_id.is_(None), Category.user_id == user_id).order_by(Category.name)
    )
    return list(result.scalars().all())


def get_category(db: Session, category_id: int, user_id: int) -> Optional[Category]:
    result = db.execute(select(Category).where(Category.id == category_id, Category.user_id == user_id))
    return result.scalar_one_or_none()


def create_category(db: Session, data: CategoryCreate, user_id: int) -> Category:
    category = Category(
        name=data.name,
        parent_id=data.parent_id,
        description=data.description,
        user_id=user_id,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(
    db: Session, category_id: int, data: CategoryUpdate, user_id: int
) -> Optional[Category]:
    category = get_category(db, category_id, user_id)
    if not category:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int, user_id: int) -> bool:
    category = get_category(db, category_id, user_id)
    if not category:
        return False

    result = db.execute(select(Note).where(Note.category_id == category_id, Note.user_id == user_id, Note.is_deleted == False))
    for note in result.scalars().all():
        note.category_id = None
    db.flush()

    result = db.execute(select(Category).where(Category.parent_id == category_id))
    for child in result.scalars().all():
        child.parent_id = None
    db.flush()

    db.delete(category)
    db.commit()
    return True


def build_category_tree(categories: List[Category]) -> List[dict]:
    cat_map = {}
    for cat in categories:
        cat_map[cat.id] = {
            "id": cat.id,
            "name": cat.name,
            "parent_id": cat.parent_id,
            "description": cat.description,
            "created_at": cat.created_at.isoformat() if cat.created_at else None,
            "children": [],
        }

    tree = []
    all_cats = []
    for cat in categories:
        all_cats.append(cat_map[cat.id])

    for cat_data in all_cats:
        if cat_data["parent_id"] and cat_data["parent_id"] in cat_map:
            cat_map[cat_data["parent_id"]]["children"].append(cat_data)
        else:
            tree.append(cat_data)

    return tree
