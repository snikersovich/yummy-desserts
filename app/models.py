from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    role = Column(String(50), default="customer")  # admin, customer
    created_at = Column(DateTime, default=datetime.now)

    # Связи
    orders = relationship("Order", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    icon = Column(String(10))

    # Связи
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    in_stock = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    preparation_days = Column(Integer, default=1)

    # Связи
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False)  # ORD-...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # может быть NULL для гостей
    guest_name = Column(String(255))
    guest_phone = Column(String(50))
    guest_email = Column(String(255))
    order_date = Column(DateTime, default=datetime.now)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="new")  # new, confirmed, in_progress, delivered, cancelled
    delivery_address = Column(Text, nullable=False)
    delivery_date = Column(String(50))
    delivery_time = Column(String(50))
    payment_method = Column(String(50), default="cash_on_delivery")
    comment = Column(Text)

    # Связи
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(255))
    product_price = Column(Float)
    quantity = Column(Integer, default=1)

    # Связи
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")