from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product, PriceHistory
from app.models.order import Order, OrderItem
from app.api.auth import get_current_user
from app.ml.train_model import ModelTrainer

router = APIRouter()

@router.get("/metrics")
async def get_analytics_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get key analytics metrics"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Total Revenue
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_(['completed', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # Total Orders
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    
    # Active Users (users with orders in last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    active_users = db.query(func.count(func.distinct(Order.user_id))).filter(
        Order.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Price Changes (from price history)
    price_changes = db.query(func.count(PriceHistory.id)).scalar() or 0
    
    return {
        "total_revenue": float(total_revenue),
        "total_orders": total_orders,
        "active_users": active_users,
        "price_changes": price_changes
    }

@router.get("/chart-data")
async def get_chart_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chart data for analytics dashboard"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Revenue data for last 7 days
    revenue_data = []
    revenue_labels = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        daily_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date,
            Order.status.in_(['completed', 'shipped', 'delivered'])
        ).scalar() or 0
        
        revenue_data.insert(0, float(daily_revenue))
        revenue_labels.insert(0, date.strftime('%b %d'))
    
    # Price changes data
    increases = db.query(func.count(PriceHistory.id)).filter(
        PriceHistory.reason == 'ai_dynamic_pricing'
    ).scalar() or 0
    
    decreases = db.query(func.count(PriceHistory.id)).filter(
        PriceHistory.reason == 'competition'
    ).scalar() or 0
    
    stable = db.query(func.count(Product.id)).filter(
        Product.is_active == True
    ).scalar() - (increases + decreases)
    
    return {
        "revenue": {
            "labels": revenue_labels,
            "data": revenue_data
        },
        "price_changes": {
            "increases": increases,
            "decreases": decreases,
            "stable": max(0, stable)
        }
    }

@router.get("/revenue")
async def get_revenue_data(
    period: str = "7d",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get revenue data for different periods"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 7)
    
    revenue_data = []
    revenue_labels = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        daily_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= start_date,
            Order.created_at < end_date,
            Order.status.in_(['completed', 'shipped', 'delivered'])
        ).scalar() or 0
        
        revenue_data.insert(0, float(daily_revenue))
        revenue_labels.insert(0, date.strftime('%b %d'))
    
    return {
        "labels": revenue_labels,
        "data": revenue_data
    }

@router.get("/products")
async def get_product_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get product performance analytics"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    products = db.query(Product).filter(Product.is_active == True).all()
    
    product_analytics = []
    for product in products:
        # Get sales count and revenue for this product
        sales_data = db.query(
            func.count(OrderItem.id).label('sales_count'),
            func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue')
        ).join(Order).filter(
            OrderItem.product_id == product.id,
            Order.status.in_(['completed', 'shipped', 'delivered'])
        ).first()
        
        sales_count = getattr(sales_data, 'sales_count', 0) if sales_data else 0
        revenue = float(getattr(sales_data, 'revenue', 0) or 0) if sales_data else 0.0
        
        # Calculate price change percentage
        price_change = 0
        base_price = getattr(product, 'base_price', 0) or 0
        if base_price > 0:
            current_price = getattr(product, 'current_price', 0) or 0
            price_change = ((current_price - base_price) / base_price) * 100
        
        product_analytics.append({
            "id": getattr(product, 'id', 0),
            "name": getattr(product, 'name', ''),
            "category": getattr(product, 'category', ''),
            "base_price": float(base_price),
            "current_price": float(getattr(product, 'current_price', 0) or 0),
            "price_change": round(price_change, 2),
            "sales_count": sales_count,
            "revenue": revenue,
            "stock_quantity": getattr(product, 'stock_quantity', 0) or 0
        })
    
    return product_analytics

@router.get("/orders")
async def get_order_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order analytics"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Orders by status
    orders_by_status = db.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()
    
    # Recent orders
    recent_orders = db.query(Order).order_by(
        desc(Order.created_at)
    ).limit(10).all()
    
    return {
        "by_status": [
            {"status": status, "count": count} 
            for status, count in orders_by_status
        ],
        "recent": [
            {
                "id": getattr(order, 'id', 0),
                "total_amount": float(getattr(order, 'total_amount', 0) or 0),
                "status": getattr(order.status, 'value', 'unknown') if getattr(order, 'status', None) else 'unknown',
                "created_at": getattr(order, 'created_at', datetime.now()).isoformat(),
                "customer_name": getattr(order, 'customer_name', 'Unknown') or "Unknown"
            }
            for order in recent_orders
        ]
    }

@router.post("/retrain-model")
async def retrain_model(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger ML model retraining"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    try:
        trainer = ModelTrainer()
        # This will run the training pipeline and return model, metrics
        model, metrics = trainer.train()
        return {
            "message": "Model retraining completed successfully!",
            "metrics": metrics
        }
    except Exception as e:
        return {
            "message": f"Model retraining failed: {str(e)}"
        } 