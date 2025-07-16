#!/usr/bin/env python3
"""
Test script to verify admin dashboard functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_endpoints():
    print("Testing Admin Dashboard Endpoints...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start the server first.")
        return
    
    # Test 2: Test admin page access
    try:
        response = requests.get(f"{BASE_URL}/admin")
        print(f"✓ Admin page accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error accessing admin page: {e}")
    
    # Test 3: Test admin API endpoints (without auth - should fail)
    endpoints = [
        "/api/admin/stats",
        "/api/admin/users", 
        "/api/admin/recent-price-changes"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✓ {endpoint} - Authentication required (expected)")
            else:
                print(f"⚠ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")
    
    # Test 4: Test login endpoint
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✓ Admin login successful - Token received")
            
            # Test 5: Test admin endpoints with token
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✓ {endpoint} - Success: {len(data) if isinstance(data, list) else 'Data received'}")
                    else:
                        print(f"✗ {endpoint} - Status: {response.status_code}")
                        if response.text:
                            print(f"  Error: {response.text}")
                except Exception as e:
                    print(f"✗ {endpoint} - Error: {e}")
        else:
            print(f"✗ Admin login failed - Status: {response.status_code}")
            if response.text:
                print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Login error: {e}")
    
    print("\n" + "=" * 50)
    print("Admin Dashboard Test Complete")

if __name__ == "__main__":
    test_admin_endpoints() 