from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models, schemas

from routers.auth import get_current_user 

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Restrict to admins in practice
):
    existing_category = db.query(models.Categories).filter(models.Categories.slug == category.slug).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category slug already exists")

    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized to create categories")
        
    db_category = models.Categories(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category



@router.get("", response_model=List[schemas.CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Categories).offset(skip).limit(limit).all()



@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category



@router.put("/update/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int, 
    category_update: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_query = db.query(models.Categories).filter(models.Categories.id == category_id)
    if not db_query.first():
        raise HTTPException(status_code=404, detail="Category not found")

    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update categories")

    db_query.update(category_update.model_dump(), synchronize_session=False)
    db.commit()
    return db_query.first()



@router.delete("/delete/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_query = db.query(models.Categories).filter(models.Categories.id == category_id)
    if not db_query.first():
        raise HTTPException(status_code=404, detail="Category not found")

    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete categories")

    db_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)