from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    base_price: float
    current_price: float
    stock_quantity: int = 0
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[float] = None
    current_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CompetitorPriceResponse(BaseModel):
    id: int
    product_id: int
    competitor_name: str
    price: float
    url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 