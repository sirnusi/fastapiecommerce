from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal

class OrderStatusSchema(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# --- CATEGORY SCHEMAS ---
class CategoryBase(BaseModel):
    name: str
    slug: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- PRODUCT SCHEMAS ---
class ProductBase(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    stock_quantity: Optional[int] = 0
    is_active: Optional[bool] = True
    category_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "FastAPI Guide",
                    "slug": "fastapi-guide",
                    "description": "A comprehensive guide to FastAPI.",
                    "price": 30.00,
                    "stock_quantity": 5,
                    "is_active": True,
                    "category_id": 1
                }
            ]
        }
    }

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created: datetime
    model_config = ConfigDict(from_attributes=True)

# --- RATING SCHEMAS ---
class RatingBase(BaseModel):
    rating: float
    description: str
    product_id: int

class RatingCreate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: int
    user_id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

# --- ORDER ITEM SCHEMAS ---
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    price_at_purchase: Decimal
    model_config = ConfigDict(from_attributes=True)

# --- ORDER SCHEMAS ---
class OrderCreate(BaseModel):
    # The client only sends the items they want to buy. 
    # Your backend will calculate the total_amount to prevent spoofing.
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatusSchema
    shipping_fee: Decimal
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: OrderStatusSchema

# --- USER SCHEMAS ---


