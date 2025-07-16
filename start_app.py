#!/usr/bin/env python3
"""
Simple Application Startup Script
Bypasses config issues and starts the FastAPI application directly
"""

import uvicorn
import os
import sys

def main():
    """Start the FastAPI application"""
    print("=" * 60)
    print("Starting Dynamic Pricing E-commerce Application")
    print("=" * 60)
    
    # Set environment variables directly
    os.environ.setdefault("DATABASE_URL", "sqlite:///./dynamic_pricing.db")
    os.environ.setdefault("SECRET_KEY", "your-secret-key-here-change-this-in-production")
    os.environ.setdefault("ALGORITHM", "HS256")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    os.environ.setdefault("PAYSTACK_SECRET_KEY", "sk_test_your_paystack_secret_key_here")
    os.environ.setdefault("PAYSTACK_PUBLIC_KEY", "pk_test_your_paystack_public_key_here")
    os.environ.setdefault("PAYSTACK_BASE_URL", "https://api.paystack.co")
    os.environ.setdefault("PAYSTACK_CURRENCY", "GHS")
    
    print("Environment variables set")
    print("Starting server...")
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
        sys.exit(1)

if __name__ == "__main__":
    main() 