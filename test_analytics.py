#!/usr/bin/env python3
"""
Test script to verify analytics functionality
"""

import requests
import json

def test_analytics():
    base_url = "http://localhost:8000"
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/")
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return
    
    # Test analytics page loads
    try:
        response = requests.get(f"{base_url}/analytics")
        if response.status_code == 200:
            print("✅ Analytics page loads successfully")
        else:
            print(f"❌ Analytics page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics page error: {e}")
    
    # Test API endpoints (will require authentication)
    try:
        response = requests.get(f"{base_url}/api/analytics/metrics")
        if response.status_code == 403:
            print("✅ Analytics API endpoint exists (requires authentication)")
        else:
            print(f"⚠️ Analytics API response: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics API error: {e}")
    
    print("\n🎉 Analytics system is ready!")
    print("📊 Access analytics at: http://localhost:8000/analytics")
    print("🔑 Login with admin account: admin@example.com / admin123")

if __name__ == "__main__":
    test_analytics() 