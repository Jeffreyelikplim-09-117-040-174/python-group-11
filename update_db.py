#!/usr/bin/env python3
"""
Script to update database schema for payment methods
"""

from app.core.database import engine
from sqlalchemy import text

def update_database():
    print("Updating database schema...")
    
    try:
        with engine.connect() as conn:
            # For SQLite, we'll try to add the column and catch the error if it exists
            try:
                conn.execute(text("ALTER TABLE orders ADD COLUMN payment_method VARCHAR"))
                print("✅ Added payment_method column to orders table")
            except Exception as e:
                if "duplicate column name" in str(e) or "already exists" in str(e):
                    print("✅ payment_method column already exists")
                else:
                    raise e
            
            conn.commit()
            print("✅ Database update completed successfully!")
            
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    update_database() 