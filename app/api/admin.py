from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product, PriceHistory
from app.models.order import Order
# from app.models.analytics import DemandMetrics  # Disabled
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get basic stats
    total_products = db.query(Product).count()
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    
    # Calculate total revenue
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0.0
    
    return {
        "total_products": total_products,
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue)
    }

@router.get("/recent-price-changes")
async def get_recent_price_changes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent price changes (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get recent price changes with product names
        recent_changes = db.query(
            PriceHistory, Product.name.label('product_name')
        ).join(Product).order_by(
            PriceHistory.created_at.desc()
        ).limit(10).all()
        
        return [
            {
                "product_name": change.product_name,
                "old_price": change.price,
                "new_price": change.price,  # This would need to be calculated from history
                "created_at": change.created_at,
                "reason": change.reason
            }
            for change in recent_changes
        ]
    except Exception as e:
        # If there's an error (e.g., no price history), return empty list
        print(f"Error getting price changes: {e}")
        return []

@router.get("/users")
async def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]

@router.put("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle user active status (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_status = getattr(user, 'is_active', True)
    setattr(user, 'is_active', not current_status)
    db.commit()
    
    return {"message": f"User {getattr(user, 'username', 'Unknown')} status updated to {'active' if getattr(user, 'is_active', True) else 'inactive'}"} 