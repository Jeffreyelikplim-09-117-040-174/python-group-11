#!/usr/bin/env python3
"""
Database Setup Script
Creates all database tables without relying on config settings
"""

import sqlite3
import os

def create_database():
    """Create SQLite database and tables"""
    print("Setting up database...")
    
    # Create database file
    db_path = "dynamic_pricing.db"
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR UNIQUE NOT NULL,
            username VARCHAR UNIQUE NOT NULL,
            hashed_password VARCHAR NOT NULL,
            full_name VARCHAR,
            is_active BOOLEAN DEFAULT TRUE,
            role VARCHAR DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL,
            description TEXT,
            category VARCHAR,
            base_price DECIMAL(10,2) NOT NULL,
            current_price DECIMAL(10,2) NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            image_url VARCHAR,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            status VARCHAR DEFAULT 'pending',
            shipping_address TEXT,
            customer_name VARCHAR,
            customer_email VARCHAR,
            order_notes TEXT,
            payment_method VARCHAR,
            payment_reference VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create order_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price_at_time DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Create cart_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Create price_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            reason VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Insert default admin user
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, username, hashed_password, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        'admin@dynamicpricing.com',
        'admin',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO',  # admin123
        'System Administrator',
        'admin',
        True
    ))
    
    # Insert sample products
    sample_products = [
        ('Wireless Bluetooth Headphones', 'High-quality wireless headphones with noise cancellation', 'electronics', 1199.88, 1199.88, 50),
        ('Smart Fitness Watch', 'Advanced fitness tracking with heart rate monitor', 'electronics', 2399.88, 2399.88, 30),
        ('Organic Cotton T-Shirt', 'Comfortable organic cotton t-shirt', 'clothing', 359.88, 359.88, 100),
        ('Python Programming Book', 'Comprehensive guide to Python programming', 'books', 599.88, 599.88, 25),
        ('Smart Home Hub', 'Control your smart home devices from one place', 'home', 1799.88, 1799.88, 20)
    ]
    
    for product in sample_products:
        cursor.execute('''
            INSERT OR IGNORE INTO products (name, description, category, base_price, current_price, stock_quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', product)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database created successfully at {db_path}")
    print("Default admin user created:")
    print("  Username: admin")
    print("  Password: admin123")
    print(f"Sample products added: {len(sample_products)}")

if __name__ == "__main__":
    create_database() 