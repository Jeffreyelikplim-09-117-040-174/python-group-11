#!/usr/bin/env python3
"""
Script to add sample analytics data for testing
"""

from app.core.database import SessionLocal
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product, PriceHistory
from app.models.user import User
from datetime import datetime, timedelta
import random

def add_sample_analytics_data():
    print("Adding sample analytics data...")
    db = SessionLocal()
    
    try:
        # Get existing products and users
        products = db.query(Product).filter(Product.is_active == True).all()
        users = db.query(User).filter(User.role == "customer").all()
        
        if not products or not users:
            print("No products or users found. Please run add_sample_data.py first.")
            return
        
        # Add sample orders over the last 30 days
        for i in range(30):
            order_date = datetime.now() - timedelta(days=i)
            
            # Create 1-3 orders per day
            for j in range(random.randint(1, 3)):
                # Random user
                user = random.choice(users)
                
                # Random products (1-3 products per order)
                order_products = random.sample(products, random.randint(1, min(3, len(products))))
                
                # Calculate total
                total_amount = 0.0
                order_items = []
                
                for product in order_products:
                    quantity = random.randint(1, 3)
                    price = getattr(product, 'current_price', 0.0)
                    total_amount += price * quantity
                    
                    order_item = OrderItem(
                        product_id=product.id,
                        quantity=quantity,
                        price_at_time=price
                    )
                    order_items.append(order_item)
                
                # Add shipping and tax
                shipping = 50 if total_amount < 1000 else 0
                tax = (total_amount + shipping) * 0.125
                total_amount += shipping + tax
                
                # Create order
                order = Order(
                    user_id=user.id,
                    total_amount=total_amount,
                    status=random.choice([OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED]),
                    shipping_address=f"Sample Address {i}-{j}",
                    customer_name=user.full_name,
                    customer_email=user.email,
                    created_at=order_date
                )
                
                db.add(order)
                db.flush()  # Get order ID
                
                # Add order items
                for item in order_items:
                    item.order_id = order.id
                    db.add(item)
        
        # Add sample price history
        for product in products:
            # Add 2-5 price changes over the last 30 days
            for i in range(random.randint(2, 5)):
                change_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                # Random price change
                price_change = random.uniform(-0.15, 0.20)  # -15% to +20%
                new_price = product.base_price * (1 + price_change)
                
                price_history = PriceHistory(
                    product_id=product.id,
                    price=new_price,
                    reason=random.choice(['ai_dynamic_pricing', 'competition', 'demand']),
                    created_at=change_date
                )
                
                db.add(price_history)
        
        db.commit()
        print("✅ Sample analytics data added successfully!")
        print(f"📊 Added orders and price history for {len(products)} products")
        
    except Exception as e:
        print(f"❌ Error adding analytics data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_analytics_data() 