from fastapi import APIRouter, Depends, HTTPException, status, Response

from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from database import SessionLocal
import models, schemas

from datetime import datetime
# Assuming your auth logic exports a dependency to get the authenticated user
from routers.auth import get_current_user 

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# READ (All for Current User)
@router.get("/", response_model=List[schemas.OrderResponse])
def get_user_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return orders

# READ (Single)
@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Ensure users can only view their own orders
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
        
    return order

# CREATE
@router.post("/create-order", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: schemas.OrderCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_amount = Decimal("0.00")
    order_items = []
    
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        
        # Calculate secure total and deduct inventory
        price = product.price
        total_amount += (price * item.quantity)
        product.stock_quantity -= item.quantity
        
        order_items.append(
            models.OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=price
            )
        )
        
    new_order = models.Order(
        user_id=current_user.id,
        status=models.OrderStatus.PENDING,
        shipping_fee=Decimal("5.00"), 
        total_amount=total_amount,
        items=order_items
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

# UPDATE (Status Only - usually restricted to Admin in production)
@router.patch("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate, # <-- FIX: Use the Update model, not the Enum
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update this order")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this order")

    # This will now work perfectly because OrderStatusUpdate has a .status attribute
    order.status = status_update.status.name
    db.commit()
    db.refresh(order)
    return order

# DELETE (Cancel Order and Restore Stock)
@router.delete("/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
        
    if order.status != models.OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot cancel an order that has already been processed")

    # Restore inventory
    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity

    order.status = models.OrderStatus.CANCELLED
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)