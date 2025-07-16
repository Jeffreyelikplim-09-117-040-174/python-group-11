#!/usr/bin/env python3
"""
Direct database fix using the same connection as the app
"""

from app.core.database import engine
from sqlalchemy import text

def direct_fix():
    print("🔧 Direct database fix...")
    
    try:
        with engine.connect() as conn:
            # Check current columns
            result = conn.execute(text("PRAGMA table_info(orders)"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"📋 Current columns: {column_names}")
            
            # Check if payment_method exists
            if 'payment_method' not in column_names:
                print("❌ payment_method column missing. Adding...")
                conn.execute(text("ALTER TABLE orders ADD COLUMN payment_method VARCHAR"))
                conn.commit()
                print("✅ payment_method column added!")
                
                # Verify
                result = conn.execute(text("PRAGMA table_info(orders)"))
                columns = result.fetchall()
                column_names = [col[1] for col in columns]
                print(f"📋 Updated columns: {column_names}")
            else:
                print("✅ payment_method column already exists")
            
            # Test inserting a dummy order to verify everything works
            print("🧪 Testing order creation...")
            try:
                conn.execute(text("""
                    INSERT INTO orders (user_id, total_amount, status, shipping_address, payment_method, customer_name, customer_email)
                    VALUES (1, 100.0, 'pending', 'Test Address', 'card', 'Test User', 'test@example.com')
                """))
                conn.commit()
                print("✅ Test order created successfully!")
                
                # Clean up test order
                conn.execute(text("DELETE FROM orders WHERE customer_email = 'test@example.com'"))
                conn.commit()
                print("🧹 Test order cleaned up")
                
            except Exception as e:
                print(f"❌ Test order failed: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    direct_fix() 