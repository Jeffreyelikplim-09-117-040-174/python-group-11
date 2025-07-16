#!/usr/bin/env python3
"""
Main Run Script for AI-Driven Dynamic Pricing Engine
Handles application startup, database initialization, and model loading
"""

import os
import sys
import uvicorn
from pathlib import Path
import importlib.util

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('torch', 'torch'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('sklearn', 'scikit-learn'),
        ('bs4', 'beautifulsoup4'),
        ('requests', 'requests'),
        ('stripe', 'stripe')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    print("All dependencies are installed!")
    return True

def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "app/ml/models",
        "app/static/images",
        "data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Directories setup completed")

def check_environment():
    """Check environment configuration"""
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found")
        print("Please create a .env file based on env_example.txt")
        print("Using default configuration...")
    
    # Set default environment variables if not present
    os.environ.setdefault('DATABASE_URL', 'sqlite:///./dynamic_pricing.db')
    os.environ.setdefault('SECRET_KEY', 'your-secret-key-here-change-in-production')

def initialize_database():
    """Initialize database and create tables"""
    try:
        from app.core.database import engine
        from app.models import base, user, product, order, analytics
        
        # Create all tables
        base.Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
        
        # Create admin user if not exists
        create_admin_user()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    
    return True

def create_admin_user():
    """Create default admin user if not exists"""
    try:
        from app.core.database import SessionLocal
        from app.models.user import User, UserRole
        from app.api.auth import get_password_hash
        
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            admin_user = User(
                email="admin@dynamicpricing.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created:")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Please change the password after first login!")
        
        db.close()
        
    except Exception as e:
        print(f"Error creating admin user: {e}")

def load_sample_data():
    """Load sample data for testing"""
    try:
        from app.core.database import SessionLocal
        from app.models.product import Product
        
        db = SessionLocal()
        
        # Check if products exist
        existing_products = db.query(Product).count()
        
        if existing_products == 0:
            sample_products = [
                {
                    "name": "Wireless Bluetooth Headphones",
                    "description": "High-quality wireless headphones with noise cancellation",
                    "category": "electronics",
                    "base_price": 1199.88,
                    "current_price": 1199.88,
                    "stock_quantity": 50,
                    "image_url": "https://via.placeholder.com/300x200?text=Headphones"
                },
                {
                    "name": "Smart Fitness Watch",
                    "description": "Advanced fitness tracking with heart rate monitor",
                    "category": "electronics",
                    "base_price": 2399.88,
                    "current_price": 2399.88,
                    "stock_quantity": 30,
                    "image_url": "https://via.placeholder.com/300x200?text=Smart+Watch"
                },
                {
                    "name": "Organic Cotton T-Shirt",
                    "description": "Comfortable organic cotton t-shirt",
                    "category": "clothing",
                    "base_price": 359.88,
                    "current_price": 359.88,
                    "stock_quantity": 100,
                    "image_url": "https://via.placeholder.com/300x200?text=T-Shirt"
                },
                {
                    "name": "Python Programming Book",
                    "description": "Comprehensive guide to Python programming",
                    "category": "books",
                    "base_price": 599.88,
                    "current_price": 599.88,
                    "stock_quantity": 25,
                    "image_url": "https://via.placeholder.com/300x200?text=Python+Book"
                },
                {
                    "name": "Smart Home Hub",
                    "description": "Control your smart home devices from one place",
                    "category": "home",
                    "base_price": 1799.88,
                    "current_price": 1799.88,
                    "stock_quantity": 20,
                    "image_url": "https://via.placeholder.com/300x200?text=Smart+Hub"
                }
            ]
            
            for product_data in sample_products:
                product = Product(**product_data)
                db.add(product)
            
            db.commit()
            print(f"Loaded {len(sample_products)} sample products")
        
        db.close()
        
    except Exception as e:
        print(f"Error loading sample data: {e}")

def check_ml_model():
    """Check if ML model exists and load it"""
    try:
        from app.ml.dynamic_pricing_model import DynamicPricingEngine
        
        model_path = "app/ml/models/dynamic_pricing_model.pth"
        
        if not os.path.exists(model_path):
            print("ML model not found. Training new model...")
            train_model()
        else:
            print("ML model found and loaded successfully")
            
    except Exception as e:
        print(f"Error checking ML model: {e}")

def train_model():
    """Train the ML model if needed"""
    try:
        # Check if processed data exists
        data_path = "data/processed_data.csv"
        
        if not os.path.exists(data_path):
            print("Processed data not found. Generating sample data...")
            from data.process_dataset import DatasetProcessor
            processor = DatasetProcessor()
            processor.process(use_sample_data=True)
        
        # Train model
        from app.ml.train_model import ModelTrainer
        trainer = ModelTrainer()
        trainer.train()
        
    except Exception as e:
        print(f"Error training model: {e}")
        print("Continuing without ML model...")

def main():
    """Main function to run the application"""
    print("=" * 60)
    print("AI-Driven Dynamic Pricing Engine")
    print("=" * 60)
    
    # Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Setup directories
    print("\n2. Setting up directories...")
    setup_directories()
    
    # Check environment
    print("\n3. Checking environment...")
    check_environment()
    
    # Initialize database
    print("\n4. Initializing database...")
    if not initialize_database():
        print("Failed to initialize database")
        sys.exit(1)
    
    # Load sample data
    print("\n5. Loading sample data...")
    load_sample_data()
    
    # Check ML model
    print("\n6. Checking ML model...")
    check_ml_model()
    
    print("\n" + "=" * 60)
    print("Application setup completed successfully!")
    print("=" * 60)
    
    # Start the application
    print("\nStarting the application...")
    print("Access the application at: http://localhost:8000")
    print("Admin dashboard at: http://localhost:8000/admin")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the application")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main() 