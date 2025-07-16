#!/usr/bin/env python3
"""
Script to add sample data to the database for testing
"""

print("Starting sample data creation...")

from app.core.database import SessionLocal
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.order import CartItem
from passlib.context import CryptContext

print("Imports successful")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_sample_data():
    print("Creating sample data...")
    db = SessionLocal()
    
    try:
        # Check if products already exist
        existing_products = db.query(Product).count()
        print(f"Existing products: {existing_products}")
        if existing_products > 0:
            print("Sample products already exist. Skipping...")
            return
        
        # Create sample products
        sample_products = [
            {
                "name": "iPhone 15 Pro",
                "description": "Latest iPhone with advanced camera system",
                "category": "electronics",
                "base_price": 4500.0,
                "current_price": 4500.0,
                "stock_quantity": 10,
                "image_url": "/static/images/products/iphone15pro.jpg",
                "is_active": True
            },
            {
                "name": "Samsung Galaxy S24",
                "description": "Premium Android smartphone with AI features",
                "category": "electronics",
                "base_price": 3800.0,
                "current_price": 3800.0,
                "stock_quantity": 15,
                "image_url": "/static/images/products/samsung-s24.jpg",
                "is_active": True
            },
            {
                "name": "MacBook Air M3",
                "description": "Lightweight laptop with powerful M3 chip",
                "category": "electronics",
                "base_price": 8500.0,
                "current_price": 8500.0,
                "stock_quantity": 8,
                "image_url": "/static/images/products/macbook-air-m3.jpg",
                "is_active": True
            },
            {
                "name": "Nike Air Max 270",
                "description": "Comfortable running shoes with Air Max technology",
                "category": "clothing",
                "base_price": 450.0,
                "current_price": 450.0,
                "stock_quantity": 25,
                "image_url": "/static/images/products/nike-airmax-270.jpg",
                "is_active": True
            },
            {
                "name": "Python Programming Book",
                "description": "Comprehensive guide to Python programming",
                "category": "books",
                "base_price": 120.0,
                "current_price": 120.0,
                "stock_quantity": 50,
                "image_url": "/static/images/products/python-book.jpg",
                "is_active": True
            }
        ]
        
        print("Adding products...")
        for product_data in sample_products:
            product = Product(**product_data)
            db.add(product)
            print(f"Added product: {product_data['name']}")
        
        # Create a test user if it doesn't exist
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            print("Creating test user...")
            hashed_password = pwd_context.hash("password123")
            test_user = User(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                hashed_password=hashed_password,
                is_active=True,
                role=UserRole.CUSTOMER
            )
            db.add(test_user)
            print("Test user created")
        else:
            print("Test user already exists")
        
        # Create an admin user if it doesn't exist
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            print("Creating admin user...")
            hashed_password = pwd_context.hash("admin123")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="Admin User",
                hashed_password=hashed_password,
                is_active=True,
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            print("Admin user created")
        else:
            print("Admin user already exists")
        
        db.commit()
        print("Sample data created successfully!")
        print("Test user: test@example.com / password123")
        print("Admin user: admin@example.com / admin123")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data() 