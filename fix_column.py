#!/usr/bin/env python3
"""
Simple script to add payment_method column to orders table
"""

import sqlite3

def fix_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('dynamic_pricing.db')
        cursor = conn.cursor()
        
        # Add the payment_method column
        cursor.execute("ALTER TABLE orders ADD COLUMN payment_method VARCHAR")
        conn.commit()
        
        print("✅ Successfully added payment_method column to orders table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()
        
        payment_method_exists = any(col[1] == 'payment_method' for col in columns)
        if payment_method_exists:
            print("✅ payment_method column verified in database")
        else:
            print("❌ payment_method column not found")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ payment_method column already exists")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    fix_database()