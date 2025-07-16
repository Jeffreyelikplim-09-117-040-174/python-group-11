from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from pydantic import BaseModel
from datetime import datetime
import requests
import json

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, CartItem
from app.models.product import Product
from app.api.auth import get_current_user

router = APIRouter()

class CustomerInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str

class PaystackPayment(BaseModel):
    email: str
    amount: float
    reference: Optional[str] = None
    callback_url: Optional[str] = None

class OrderCreate(BaseModel):
    shipping_address: str
    customer_info: Optional[CustomerInfo] = None
    payment_info: PaystackPayment
    order_notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    shipping_address: str
    created_at: datetime
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    payment_method: Optional[str] = None
    paystack_reference: Optional[str] = None
    
    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    shipping_address: str
    created_at: datetime
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    order_notes: Optional[str] = None
    payment_method: Optional[str] = None
    paystack_reference: Optional[str] = None
    items: List[dict]
    
    class Config:
        from_attributes = True

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart items with Paystack payment"""
    # Get user's cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == getattr(current_user, 'id', 0)).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Validate payment info
    if not validate_paystack_payment_info(order_data.payment_info):
        raise HTTPException(status_code=400, detail="Invalid payment information")
    
    # Calculate total amount
    total_amount = 0.0
    order_items = []
    
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == getattr(cart_item, 'product_id', 0)).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {getattr(cart_item, 'product_id', 0)} not found")
        
        # Check stock using the actual values
        stock_quantity = getattr(product, 'stock_quantity', 0) or 0
        cart_quantity = getattr(cart_item, 'quantity', 0) or 0
        if stock_quantity < cart_quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for {getattr(product, 'name', 'Unknown Product')}"
            )
        
        current_price = getattr(product, 'current_price', 0.0) or 0.0
        item_total = current_price * cart_quantity
        total_amount += item_total
        
        # Create order item
        order_item = OrderItem(
            product_id=getattr(cart_item, 'product_id', 0),
            quantity=cart_quantity,
            price_at_time=current_price
        )
        order_items.append(order_item)
        
        # Update stock - use setattr to avoid SQLAlchemy issues
        new_stock = stock_quantity - cart_quantity
        setattr(product, 'stock_quantity', new_stock)
    
    # Add shipping cost (free over GHS 1000, otherwise GHS 50)
    shipping_cost = 0 if total_amount > 1000.0 else 50.0
    total_amount += shipping_cost
    
    # Add tax (12.5% VAT)
    tax_amount = total_amount * 0.125
    total_amount += tax_amount
    
    # Create order with enhanced information
    customer_name = None
    customer_email = None
    if order_data.customer_info:
        customer_name = f"{order_data.customer_info.first_name} {order_data.customer_info.last_name}"
        customer_email = order_data.customer_info.email
    
    # Initialize order status as pending
    initial_status = OrderStatus.PENDING
    
    order = Order(
        user_id=getattr(current_user, 'id', 0),
        total_amount=total_amount,
        status=initial_status,
        shipping_address=order_data.shipping_address,
        customer_name=customer_name,
        customer_email=customer_email,
        order_notes=order_data.order_notes,
        payment_method="paystack"
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Add order items
    for order_item in order_items:
        order_item.order_id = order.id
        db.add(order_item)
    
    # Clear cart
    for cart_item in cart_items:
        db.delete(cart_item)
    
    db.commit()
    db.refresh(order)
    
    # Log the order for analytics
    log_order_analytics(order, db)
    
    # Process Paystack payment
    try:
        payment_result = process_paystack_payment(order_data.payment_info, order)
        return payment_result
    except Exception as e:
        print(f"Payment processing error for order {order.id}: {str(e)}")
        # Return order with payment pending status
        return order

def validate_paystack_payment_info(payment_info: PaystackPayment) -> bool:
    """Validate Paystack payment information"""
    try:
        return (
            'email' in payment_info.__dict__ and
            'amount' in payment_info.__dict__ and
            payment_info.amount > 0
        )
    except:
        return False

def process_paystack_payment(payment_info: PaystackPayment, order: Order):
    """Process payment using Paystack API"""
    try:
        # Initialize Paystack transaction
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        # Convert amount to kobo (Paystack uses kobo for amounts)
        amount_in_kobo = int(payment_info.amount * 100)
        
        payload = {
            "email": payment_info.email,
            "amount": amount_in_kobo,
            "currency": settings.PAYSTACK_CURRENCY,
            "reference": payment_info.reference or f"order_{order.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "callback_url": payment_info.callback_url or f"http://localhost:8000/payment/callback",
            "metadata": {
                "order_id": order.id,
                "customer_name": getattr(order, 'customer_name', ''),
                "shipping_address": getattr(order, 'shipping_address', '')
            }
        }
        
        # Make API call to Paystack
        response = requests.post(
            f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status'):
                # Update order with Paystack reference
                setattr(order, 'payment_reference', result['data']['reference'])
                
                return {
                    "id": getattr(order, 'id', 0),
                    "total_amount": getattr(order, 'total_amount', 0),
                    "status": "pending",
                    "shipping_address": getattr(order, 'shipping_address', ''),
                    "created_at": getattr(order, 'created_at', datetime.now()),
                    "customer_name": getattr(order, 'customer_name', ''),
                    "customer_email": getattr(order, 'customer_email', ''),
                    "payment_method": "paystack",
                    "paystack_reference": result['data']['reference'],
                    "authorization_url": result['data']['authorization_url']
                }
            else:
                raise HTTPException(status_code=400, detail="Paystack payment initialization failed")
        else:
            raise HTTPException(status_code=400, detail=f"Paystack API error: {response.text}")
            
    except Exception as e:
        print(f"Paystack payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

@router.post("/verify-payment/{reference}")
async def verify_payment(
    reference: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Paystack payment status"""
    try:
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') and result['data']['status'] == 'success':
                # Update order status to completed
                order = db.query(Order).filter(
                    Order.payment_reference == reference,
                    Order.user_id == getattr(current_user, 'id', 0)
                ).first()
                
                if order:
                    setattr(order, 'status', OrderStatus.COMPLETED)
                    db.commit()
                    
                    return {
                        "status": "success",
                        "message": "Payment verified successfully",
                        "order_id": getattr(order, 'id', 0)
                    }
                else:
                    raise HTTPException(status_code=404, detail="Order not found")
            else:
                return {
                    "status": "failed",
                    "message": "Payment verification failed"
                }
        else:
            raise HTTPException(status_code=400, detail="Payment verification failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification error: {str(e)}")

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order details with items"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order items
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    # Get product details for each item
    items_data = []
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_data.append({
            "product_name": product.name if product else "Unknown Product",
            "quantity": item.quantity,
            "price_at_time": item.price_at_time,
            "total": item.quantity * item.price_at_time
        })
    
    # Create response with items
    response_data = {
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status.value,
        "shipping_address": order.shipping_address,
        "created_at": order.created_at,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "order_notes": order.order_notes,
        "items": items_data
    }
    
    return response_data

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status (Admin only)"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Use setattr to avoid SQLAlchemy enum issues
    setattr(order, 'status', status)
    db.commit()
    db.refresh(order)
    
    return {"message": "Order status updated successfully"}

@router.get("/admin/all", response_model=List[OrderDetailResponse])
async def get_all_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[OrderStatus] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all orders (Admin only) with filtering and pagination"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    
    # Get detailed order information
    detailed_orders = []
    for order in orders:
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        items_data = []
        for item in order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items_data.append({
                "product_name": product.name if product else "Unknown Product",
                "quantity": item.quantity,
                "price_at_time": item.price_at_time,
                "total": item.quantity * item.price_at_time
            })
        
        detailed_orders.append({
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status.value,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "order_notes": order.order_notes,
            "items": items_data
        })
    
    return detailed_orders

def log_order_analytics(order: Order, db: Session):
    """Log order data for analytics and AI model training"""
    try:
        # For now, just log the order data
        # In a full implementation, this would create analytics records
        print(f"Order analytics logged: Order {order.id}, Amount: {order.total_amount}")
        
        # Trigger AI model update if needed
        trigger_ai_update(order, db)
        
    except Exception as e:
        print(f"Error logging order analytics: {e}")

def trigger_ai_update(order: Order, db: Session):
    """Trigger AI model update based on new order data"""
    try:
        # This would typically trigger a background task to update the AI model
        # For now, we'll just log that an update should be triggered
        print(f"AI model update triggered for order {order.id}")
        
        # In a production system, this would:
        # 1. Add the order data to the training dataset
        # 2. Trigger a background task to retrain the model
        # 3. Update product prices based on new demand patterns
        
    except Exception as e:
        print(f"Error triggering AI update: {e}") 