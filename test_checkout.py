#!/usr/bin/env python3
"""
Test script to verify checkout functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_checkout_functionality():
    print("Testing Checkout Functionality")
    print("=" * 40)
    
    # Test 1: Check if checkout page loads
    print("\n1. Testing checkout page access...")
    try:
        response = requests.get(f"{BASE_URL}/checkout")
        if response.status_code == 200:
            print("✅ Checkout page loads successfully")
        else:
            print(f"❌ Checkout page failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing checkout page: {e}")
    
    # Test 2: Check cart API endpoints
    print("\n2. Testing cart API endpoints...")
    
    # Test cart GET endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/cart/")
        print(f"Cart GET endpoint: {response.status_code}")
        if response.status_code in [200, 401]:  # 401 is expected for unauthenticated users
            print("✅ Cart GET endpoint accessible")
        else:
            print(f"❌ Cart GET endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing cart GET: {e}")
    
    # Test 3: Check if cart item deletion endpoint exists
    print("\n3. Testing cart item deletion endpoint...")
    try:
        response = requests.delete(f"{BASE_URL}/api/cart/1")
        print(f"Cart DELETE endpoint: {response.status_code}")
        if response.status_code in [200, 401, 404]:  # Expected responses
            print("✅ Cart DELETE endpoint accessible")
        else:
            print(f"❌ Cart DELETE endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing cart DELETE: {e}")
    
    # Test 4: Check if cart item update endpoint exists
    print("\n4. Testing cart item update endpoint...")
    try:
        response = requests.put(f"{BASE_URL}/api/cart/1", json={"quantity": 2})
        print(f"Cart PUT endpoint: {response.status_code}")
        if response.status_code in [200, 401, 404]:  # Expected responses
            print("✅ Cart PUT endpoint accessible")
        else:
            print(f"❌ Cart PUT endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing cart PUT: {e}")
    
    # Test 5: Check order creation endpoint
    print("\n5. Testing order creation endpoint...")
    try:
        order_data = {
            "customer_name": "Test User",
            "customer_email": "test@example.com",
            "shipping_address": "123 Test St, Test City",
            "payment_method": "mobile_money",
            "order_notes": "Test order"
        }
        response = requests.post(f"{BASE_URL}/api/orders/", json=order_data)
        print(f"Order creation endpoint: {response.status_code}")
        if response.status_code in [200, 201, 401, 422]:  # Expected responses
            print("✅ Order creation endpoint accessible")
        else:
            print(f"❌ Order creation endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing order creation: {e}")
    
    print("\n" + "=" * 40)
    print("Checkout functionality test completed!")

if __name__ == "__main__":
    test_checkout_functionality() 