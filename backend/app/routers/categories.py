from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import (
    get_categories,
    get_category,
    create_category,
    update_category,
    delete_category,
    build_category_tree,
)
from app.services.auth_service import get_current_user
from app.models import User

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
def api_list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = get_categories(db, current_user.id)
    tree = build_category_tree(categories)
    return tree


@router.post("", response_model=CategoryResponse)
def api_create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = create_category(db, data, current_user.id)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def api_update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = update_category(db, category_id, data, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="分类未找到")
    return category


@router.delete("/{category_id}")
def api_delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = delete_category(db, category_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="分类未找到")
    return {"message": "删除成功"}
