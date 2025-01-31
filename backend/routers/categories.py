from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from models.database_models import Category
from schemas.category import CategoryCreate, CategoryResponse
from utils.auth import verify_token

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token),
):
    db_category = Category(name=category.name, user_id=current_user["user_id"])
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    return db.query(Category).filter(Category.user_id == current_user["user_id"]).all()

@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token),
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == current_user["user_id"])
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"} 