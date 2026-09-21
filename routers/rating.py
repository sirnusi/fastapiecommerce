from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models, schemas

from routers.auth import get_current_user

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=schemas.RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating: schemas.RatingCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized to create ratings")

    product = db.query(models.Product).filter(models.Product.id == rating.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db_rating = models.Rating(
        **rating.model_dump(),
        user_id=current_user.id
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@router.get("/product/{product_id}", response_model=List[schemas.RatingResponse])
def get_product_ratings(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    ratings = db.query(models.Rating).filter(
        models.Rating.product_id == product_id,
        models.Rating.is_active == True
    ).offset(skip).limit(limit).all()
    
    return ratings

@router.delete("/delete/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_query = db.query(models.Rating).filter(models.Rating.id == rating_id)
    rating = db_query.first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
        
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this rating")

    db_query.update({"is_active": False}, synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)