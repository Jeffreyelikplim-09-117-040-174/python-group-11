#!/usr/bin/env python3
"""
Script to download and organize images for the e-commerce website
"""

import os
import requests
from pathlib import Path
import urllib.parse

def create_image_directories():
    """Create necessary image directories"""
    directories = [
        "app/static/images",
        "app/static/images/products",
        "app/static/images/categories",
        "app/static/images/icons"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def download_image(url, filepath):
    """Download an image from URL to filepath"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def create_placeholder_image(text, filename, width=300, height=200):
    """Create a placeholder image with text"""
    url = f"https://via.placeholder.com/{width}x{height}/4A90E2/FFFFFF?text={urllib.parse.quote(text)}"
    filepath = f"app/static/images/products/{filename}"
    return download_image(url, filepath)

def download_product_images():
    """Download product images"""
    print("\n📸 Downloading product images...")
    
    # Product images with better URLs
    products = [
        {
            "name": "iPhone 15 Pro",
            "filename": "iphone15pro.jpg",
            "url": "https://via.placeholder.com/300x200/000000/FFFFFF?text=iPhone+15+Pro"
        },
        {
            "name": "Samsung Galaxy S24",
            "filename": "samsung-s24.jpg", 
            "url": "https://via.placeholder.com/300x200/1428A0/FFFFFF?text=Samsung+Galaxy+S24"
        },
        {
            "name": "MacBook Air M3",
            "filename": "macbook-air-m3.jpg",
            "url": "https://via.placeholder.com/300x200/555555/FFFFFF?text=MacBook+Air+M3"
        },
        {
            "name": "Nike Air Max 270",
            "filename": "nike-airmax-270.jpg",
            "url": "https://via.placeholder.com/300x200/FF6600/FFFFFF?text=Nike+Air+Max+270"
        },
        {
            "name": "Python Programming Book",
            "filename": "python-book.jpg",
            "url": "https://via.placeholder.com/300x200/3776AB/FFFFFF?text=Python+Book"
        }
    ]
    
    for product in products:
        download_image(product["url"], f"app/static/images/products/{product['filename']}")

def download_category_icons():
    """Download category icons"""
    print("\n🏷️ Downloading category icons...")
    
    categories = [
        {
            "name": "Electronics",
            "filename": "electronics.png",
            "url": "https://via.placeholder.com/64x64/4A90E2/FFFFFF?text=📱"
        },
        {
            "name": "Clothing", 
            "filename": "clothing.png",
            "url": "https://via.placeholder.com/64x64/7ED321/FFFFFF?text=👕"
        },
        {
            "name": "Books",
            "filename": "books.png", 
            "url": "https://via.placeholder.com/64x64/F5A623/FFFFFF?text=📚"
        },
        {
            "name": "Home",
            "filename": "home.png",
            "url": "https://via.placeholder.com/64x64/BD10E0/FFFFFF?text=🏠"
        }
    ]
    
    for category in categories:
        download_image(category["url"], f"app/static/images/categories/{category['filename']}")

def download_website_assets():
    """Download website assets"""
    print("\n🎨 Downloading website assets...")
    
    assets = [
        {
            "name": "Logo",
            "filename": "logo.png",
            "url": "https://via.placeholder.com/200x60/4A90E2/FFFFFF?text=Dynamic+Pricing+Store"
        },
        {
            "name": "Favicon",
            "filename": "favicon.ico",
            "url": "https://via.placeholder.com/32x32/4A90E2/FFFFFF?text=DP"
        },
        {
            "name": "Placeholder",
            "filename": "placeholder.jpg",
            "url": "https://via.placeholder.com/300x200/E5E5E5/999999?text=No+Image"
        }
    ]
    
    for asset in assets:
        download_image(asset["url"], f"app/static/images/{asset['filename']}")

def update_product_image_urls():
    """Update the sample data to use local image URLs"""
    print("\n🔄 Updating product image URLs...")
    
    # Read the current add_sample_data.py
    with open('add_sample_data.py', 'r') as f:
        content = f.read()
    
    # Update image URLs to use local files
    replacements = [
        ('https://via.placeholder.com/300x200?text=iPhone+15+Pro', '/static/images/products/iphone15pro.jpg'),
        ('https://via.placeholder.com/300x200?text=Samsung+Galaxy+S24', '/static/images/products/samsung-s24.jpg'),
        ('https://via.placeholder.com/300x200?text=MacBook+Air+M3', '/static/images/products/macbook-air-m3.jpg'),
        ('https://via.placeholder.com/300x200?text=Nike+Air+Max+270', '/static/images/products/nike-airmax-270.jpg'),
        ('https://via.placeholder.com/300x200?text=Python+Book', '/static/images/products/python-book.jpg')
    ]
    
    for old_url, new_url in replacements:
        content = content.replace(old_url, new_url)
    
    # Write back the updated file
    with open('add_sample_data.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated product image URLs in sample data")

def main():
    """Main function to download all images"""
    print("🖼️ Starting image download process...")
    
    # Create directories
    create_image_directories()
    
    # Download images
    download_product_images()
    download_category_icons()
    download_website_assets()
    
    # Update sample data
    update_product_image_urls()
    
    print("\n🎉 Image download process completed!")
    print("\n📁 Images are now available in:")
    print("   - app/static/images/products/ (Product images)")
    print("   - app/static/images/categories/ (Category icons)")
    print("   - app/static/images/ (Website assets)")
    print("\n🔄 Run 'python add_sample_data.py' to update products with new image URLs")

if __name__ == "__main__":
    main() 