from sqlalchemy.orm import Session
from typing import Annotated, Optional, List
from models import *
import schemas
from database import SessionLocal
from fastapi import Depends, APIRouter, HTTPException, HTTPException, Path, status

from routers.auth import get_current_user


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=List[schemas.ProductResponse], status_code=status.HTTP_200_OK)
async def get_products(db: db_dependency):
    products = db.query(Product).filter(Product.is_active == True)
    return products



@router.get("/{products_id}", status_code=status.HTTP_200_OK)
async def get_one_products(db: db_dependency, products_id: int):
    query = db.query(Product).filter(Product.id == products_id).first()

    if query is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    return query


@router.post("/create-product", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(user: user_dependency, db: db_dependency, product: schemas.ProductCreate):
    category = db.query(Categories).filter(Categories.id == product.category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if user is None:
        raise HTTPException(status_code=401, detail="Not authorized.")

    product_model = Product(**product.model_dump())

    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    
    return product_model

@router.patch("/patch-product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_expense(user: user_dependency, db: db_dependency, product: schemas.ProductCreate, product_id: int = Path(gt=-1)):
   
    if user is None:
        raise HTTPException(status_code=401, detail="Not authorized!")
    query = db.query(Product).filter(Product.id == product_id).first()
    
    
    if query is None:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(query, key, value)


    db.commit()
    db.refresh(query)
    
    return query


@router.delete("/delete-product/{product_id}", status_code=status.HTTP_200_OK)
async def delete_expense(user: user_dependency, db: db_dependency, product_id: int = Path(gt=-1)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authorized!")
    query = db.query(Product).filter(Product.id == product_id).first()
    
    if query is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.query(Product).filter(Product.id == product_id).update({"is_active": False}, synchronize_session=False)
    db.commit()
    return {'message': 'Your product has been deleted.'}