#!/usr/bin/env python3
"""
Test script to verify admin login and access
"""

import requests
import json

def test_admin_login():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Admin Login Flow...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return
    
    # Test 2: Test admin login
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = requests.post(f"{base_url}/api/auth/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print("✅ Admin login successful")
            print(f"   Token received: {access_token[:20]}...")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Test admin user info
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User info retrieved")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   Email: {user_data.get('email')}")
            
            if user_data.get('role') == 'admin':
                print("✅ User has admin role")
            else:
                print("❌ User does not have admin role")
                return
        else:
            print(f"❌ Failed to get user info: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ User info error: {e}")
        return
    
    # Test 4: Test admin dashboard access
    try:
        response = requests.get(f"{base_url}/admin")
        if response.status_code == 200:
            print("✅ Admin dashboard page accessible")
        else:
            print(f"❌ Admin dashboard access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin dashboard error: {e}")
    
    # Test 5: Test admin API endpoints
    try:
        response = requests.get(f"{base_url}/api/admin/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Admin stats API working")
            print(f"   Total products: {stats.get('total_products')}")
            print(f"   Total users: {stats.get('total_users')}")
            print(f"   Total orders: {stats.get('total_orders')}")
        else:
            print(f"❌ Admin stats API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Admin stats error: {e}")
    
    # Test 6: Test admin users API
    try:
        response = requests.get(f"{base_url}/api/admin/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print("✅ Admin users API working")
            print(f"   Total users: {len(users)}")
        else:
            print(f"❌ Admin users API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin users error: {e}")
    
    print("\n🎉 Admin login test completed!")
    print("\n📋 Summary:")
    print("   - Admin credentials: admin / admin123")
    print("   - Admin dashboard: http://localhost:8000/admin")
    print("   - After login, you should be redirected to admin dashboard")

if __name__ == "__main__":
    test_admin_login() 