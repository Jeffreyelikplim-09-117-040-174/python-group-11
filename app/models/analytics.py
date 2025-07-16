from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

# Temporarily commenting out analytics models to fix SQLAlchemy issues
# These can be re-enabled later when the relationship issues are resolved

# class UserBehavior(BaseModel):
#     __tablename__ = "user_behaviors"
#     
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
#     action_type = Column(String, nullable=False)  # view, add_to_cart, purchase, etc.
#     session_duration = Column(Integer)  # in seconds
#     timestamp = Column(DateTime, nullable=False)
#     
#     # Relationships - simplified to avoid circular imports
#     user = relationship("User")
#     product = relationship("Product")

# class DemandMetrics(BaseModel):
#     __tablename__ = "demand_metrics"
#     
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
#     date = Column(DateTime, nullable=False)
#     views = Column(Integer, default=0)
#     add_to_cart_count = Column(Integer, default=0)
#     purchase_count = Column(Integer, default=0)
#     conversion_rate = Column(Float, default=0.0)
#     
#     # Relationships - simplified to avoid circular imports
#     product = relationship("Product")

class PricingStrategy(BaseModel):
    __tablename__ = "pricing_strategies"
    
    name = Column(String, nullable=False)
    description = Column(String)
    algorithm_type = Column(String, nullable=False)  # regression, reinforcement_learning
    parameters = Column(String)  # JSON string of model parameters
    is_active = Column(String, default="true") 