#!/usr/bin/env python3
"""
Script to check database structure and identify issues
"""

from app.core.database import engine
from sqlalchemy import text

def check_database():
    print("Checking database structure...")
    
    try:
        with engine.connect() as conn:
            # Check if orders table exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"))
            if not result.fetchone():
                print("❌ Orders table does not exist!")
                return
            
            # Get table schema
            result = conn.execute(text("PRAGMA table_info(orders)"))
            columns = result.fetchall()
            
            print("📋 Orders table columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
            
            # Check if payment_method column exists
            payment_method_exists = any(col[1] == 'payment_method' for col in columns)
            if not payment_method_exists:
                print("❌ payment_method column is missing!")
                print("Adding payment_method column...")
                try:
                    conn.execute(text("ALTER TABLE orders ADD COLUMN payment_method VARCHAR"))
                    conn.commit()
                    print("✅ Added payment_method column")
                except Exception as e:
                    print(f"❌ Failed to add column: {e}")
            else:
                print("✅ payment_method column exists")
            
            # Check for any existing orders
            result = conn.execute(text("SELECT COUNT(*) FROM orders"))
            order_count = result.scalar() or 0
            print(f"📊 Total orders in database: {order_count}")
            
            if order_count > 0:
                # Check a sample order
                result = conn.execute(text("SELECT * FROM orders LIMIT 1"))
                sample_order = result.fetchone()
                if sample_order:
                    print("📝 Sample order structure:")
                    for i, col in enumerate(columns):
                        print(f"  {col[1]}: {sample_order[i]}")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database() 