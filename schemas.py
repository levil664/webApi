from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ProductCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(ProductCategoryBase):
    name: Optional[str] = Field(None, title="New product category name")


class ProductCategory(ProductCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
