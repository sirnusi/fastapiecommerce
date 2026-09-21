import enum
from database import Base
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Text, Float, Enum, DateTime
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(EmailType, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    # Relationships
    address = Column(String)
    orders = relationship("Order", back_populates="user")
    ratings = relationship("Rating", back_populates="user")



class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String)

    # Relationships
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    
    # Core details
    name = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Pricing and Inventory
    price = Column(Numeric(10, 2), nullable=False)
    
    stock_quantity = Column(Integer, default=0, nullable=False)
    created = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    is_active = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Categories", back_populates="products")

    # Relationship to Ratings
    ratings = relationship("Rating", back_populates="product")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    product_id = Column(Integer, ForeignKey('products.id'))

    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="ratings")
    product = relationship("Product", back_populates="ratings")


# -- CATALOG --

# -- PURCHASING ---
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Intermediate Fields: Financials & Tracking
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    shipping_fee = Column(Numeric(10, 2), default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Intermediate Fields: Price Snapshotting
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Numeric(10, 2), nullable=False) 

    # Relationships
    order = relationship("Order", back_populates="items")

