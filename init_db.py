#!/usr/bin/env python3
"""
Simple script to initialize the database tables
"""

from app.core.database import engine
from app.models import base, user, product, order, analytics

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    base.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database() 