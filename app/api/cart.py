from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.order import CartItem
from app.models.product import Product
from app.api.auth import get_current_user

router = APIRouter()

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    price: float  # Alias for product_price
    quantity: int
    total_price: float
    price_at_time: float
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[CartItemResponse])
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's cart items"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    response_items = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            current_price = getattr(product, 'current_price', 0.0)
            item_total = current_price * getattr(item, 'quantity', 0)
            response_items.append(CartItemResponse(
                id=getattr(item, 'id', 0),
                product_id=getattr(item, 'product_id', 0),
                product_name=getattr(product, 'name', ''),
                product_price=current_price,
                price=current_price,  # Alias for JavaScript compatibility
                quantity=getattr(item, 'quantity', 0),
                total_price=item_total,
                price_at_time=current_price
            ))
    
    return response_items

@router.post("/add/{product_id}")
def add_to_cart(
    product_id: int,
    quantity: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add product to cart"""
    # Check if product exists and is active
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Handle None stock quantity
    stock_quantity = int(getattr(product, 'stock_quantity', 0) or 0)
    if stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == getattr(current_user, 'id', 0),
        CartItem.product_id == product_id
    ).first()
    
    if existing_item:
        current_quantity = getattr(existing_item, 'quantity', 0) or 0
        setattr(existing_item, 'quantity', current_quantity + quantity)
    else:
        cart_item = CartItem(
            user_id=getattr(current_user, 'id', 0),
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)
    
    db.commit()
    return {"message": "Product added to cart successfully"}

@router.put("/{item_id}")
def update_cart_item(
    item_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Check stock availability
    product = db.query(Product).filter(Product.id == getattr(cart_item, 'product_id', 0)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    stock_quantity = int(getattr(product, 'stock_quantity', 0) or 0)
    if stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    setattr(cart_item, 'quantity', quantity)
    db.commit()
    
    return {"message": "Cart item updated successfully"}

@router.delete("/{item_id}")
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart successfully"}

@router.delete("/clear")
def clear_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Clear all items from cart"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    for item in cart_items:
        db.delete(item)
    
    db.commit()
    return {"message": "Cart cleared successfully"}

@router.get("/total")
def get_cart_total(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get cart total"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    total = 0.0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == getattr(item, 'product_id', 0)).first()
        if product:
            total += getattr(product, 'current_price', 0.0) * getattr(item, 'quantity', 0)
    
    return {"total": total}

# Keep the old endpoints for backward compatibility
@router.put("/update/{item_id}")
def update_cart_item_old(
    item_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity (legacy endpoint)"""
    return update_cart_item(item_id, quantity, current_user, db)

@router.delete("/remove/{item_id}")
def remove_from_cart_old(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart (legacy endpoint)"""
    return remove_from_cart(item_id, current_user, db)

# Additional endpoints for checkout functionality
@router.get("/items", response_model=List[CartItemResponse])
def get_cart_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's cart items (alias for /)"""
    return get_cart(current_user, db)

@router.put("/update/{product_id}")
def update_cart_item_by_product(
    product_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity by product ID"""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    cart_item = db.query(CartItem).filter(
        CartItem.product_id == product_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Check stock availability
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stock_quantity = int(getattr(product, 'stock_quantity', 0) or 0)
    if stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    setattr(cart_item, 'quantity', quantity)
    db.commit()
    
    return {"message": "Cart item updated successfully"}

@router.delete("/remove/{product_id}")
def remove_from_cart_by_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart by product ID"""
    cart_item = db.query(CartItem).filter(
        CartItem.product_id == product_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart successfully"} 