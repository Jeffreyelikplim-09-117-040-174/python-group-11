from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product, PriceHistory, CompetitorPrice
# from app.models.analytics import DemandMetrics  # Commented out since DemandMetrics is disabled
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, PriceHistoryResponse
from app.api.auth import get_current_user
from app.ml.dynamic_pricing_model import DynamicPricingEngine
from app.scrapers.competitor_scraper import CompetitorPriceScraper

router = APIRouter()
pricing_engine = DynamicPricingEngine()
scraper = CompetitorPriceScraper()

@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_product = Product(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    db.commit()
    return {"message": "Product deleted successfully"}

@router.post("/{product_id}/update-price")
def update_product_price(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update product price using AI dynamic pricing (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get competitor prices
    competitor_prices = scraper.get_competitor_prices(str(product.name), str(product.category))
    
    # Calculate average competitor price
    if competitor_prices:
        avg_competitor_price = sum(cp['price'] for cp in competitor_prices) / len(competitor_prices)
    else:
        avg_competitor_price = product.base_price
    
    # Get demand metrics (commented out since DemandMetrics is disabled)
    # demand_metrics = db.query(DemandMetrics).filter(
    #     DemandMetrics.product_id == product_id
    # ).order_by(DemandMetrics.date.desc()).first()
    
    # Prepare data for pricing model
    product_data = {
        'base_price': product.base_price,
        'competitor_avg_price': avg_competitor_price,
        'demand_score': pricing_engine.calculate_demand_score(
            0,  # views - default value since DemandMetrics is disabled
            0,  # add_to_cart - default value since DemandMetrics is disabled
            0   # purchases - default value since DemandMetrics is disabled
        ),
        'stock_level': product.stock_quantity,
        'seasonality_factor': pricing_engine.calculate_seasonality_factor(datetime.now().month),
        'user_engagement': 0.0,
        'conversion_rate': 0.0,
        'time_since_last_price_change': 1.0  # Simplified
    }
    
    # Predict optimal price
    optimal_price = pricing_engine.predict_optimal_price(product_data)
    
    # Update product price
    old_price = product.current_price
    product.current_price = optimal_price
    
    # Record price history
    price_history = PriceHistory(
        product_id=product_id,
        price=optimal_price,
        reason="ai_dynamic_pricing"
    )
    
    # Save competitor prices
    for cp in competitor_prices:
        competitor_price = CompetitorPrice(
            product_id=product_id,
            competitor_name=cp['competitor'],
            price=cp['price'],
            url=cp.get('url')
        )
        db.add(competitor_price)
    
    db.add(price_history)
    db.commit()
    
    return {
        "message": "Price updated successfully",
        "old_price": old_price,
        "new_price": optimal_price,
        "competitor_prices": competitor_prices
    }

@router.get("/{product_id}/price-history", response_model=List[PriceHistoryResponse])
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    """Get price history for a product"""
    price_history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).order_by(PriceHistory.created_at.desc()).all()
    return price_history 