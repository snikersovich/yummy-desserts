from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# User schemas
class UserBase(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    in_stock: bool = True
    category_id: int
    preparation_days: int = 1


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True


# Category schemas
class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = None

    class Config:
        from_attributes = True