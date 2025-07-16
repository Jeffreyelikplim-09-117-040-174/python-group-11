from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")
    competitor_prices = relationship("CompetitorPrice", back_populates="product")
    # user_behaviors and demand_metrics will be set after all classes

class PriceHistory(BaseModel):
    __tablename__ = "price_history"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    reason = Column(String)  # demand, competition, user_behavior, etc.
    
    # Relationships
    product = relationship("Product", back_populates="price_history")

class CompetitorPrice(BaseModel):
    __tablename__ = "competitor_prices"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    competitor_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    url = Column(String)
    
    # Relationships
    product = relationship("Product", back_populates="competitor_prices")

# Set relationships that reference models defined elsewhere
# Product.user_behaviors = relationship("UserBehavior", back_populates="product")
# Product.demand_metrics = relationship("DemandMetrics", back_populates="product") 