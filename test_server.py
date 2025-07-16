#!/usr/bin/env python3
"""
Test Server Script
Tests if the FastAPI application is running properly
"""

import requests
import time

def test_server():
    """Test if the server is running and responding"""
    print("Testing server...")
    
    # Wait a moment for server to fully start
    time.sleep(2)
    
    try:
        # Test main endpoint
        response = requests.get("http://localhost:8000/", timeout=10)
        print(f"Main endpoint status: {response.status_code}")
        
        # Test docs endpoint
        response = requests.get("http://localhost:8000/docs", timeout=10)
        print(f"Docs endpoint status: {response.status_code}")
        
        # Test API endpoints
        response = requests.get("http://localhost:8000/api/products", timeout=10)
        print(f"Products API status: {response.status_code}")
        
        print("\n✅ Server is running successfully!")
        print("\nAccess your application at:")
        print("🌐 Main Store: http://localhost:8000/")
        print("📊 Admin Dashboard: http://localhost:8000/admin")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("📈 Analytics: http://localhost:8000/analytics")
        
        print("\n🔑 Admin Login:")
        print("   Username: admin")
        print("   Password: admin123")
        
    except requests.exceptions.ConnectionError:
        print("❌ Server is not responding")
        print("Please check if the server is running")
    except Exception as e:
        print(f"❌ Error testing server: {e}")

if __name__ == "__main__":
    test_server() 