#!/usr/bin/env python3
"""
Process Kaggle Amazon Dataset for AI Model Training
Converts the real Amazon dataset into the format expected by the training pipeline
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import re

def process_kaggle_amazon_data():
    """Process the Kaggle Amazon dataset for training"""
    print("Processing Kaggle Amazon dataset...")
    
    # Load the raw Kaggle dataset
    raw_data_path = "archive/home/sdf/marketing_sample_for_amazon_com-ecommerce__20200101_20200131__10k_data.csv"
    
    if not os.path.exists(raw_data_path):
        print(f"Raw dataset not found at {raw_data_path}")
        return False
    
    # Read the CSV file
    df = pd.read_csv(raw_data_path)
    print(f"Loaded raw dataset with shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Clean and process the data
    processed_data = []
    
    for idx, row in df.iterrows():
        try:
            # Extract price information
            list_price = extract_price(row.get('List Price', ''))
            selling_price = extract_price(row.get('Selling Price', ''))
            
            if not selling_price or selling_price <= 0:
                continue
            
            # Extract category
            category = extract_category(row.get('Category', ''))
            
            # Extract product name and calculate features
            product_name = str(row.get('Product Name', ''))
            title_length = len(product_name)
            word_count = len(product_name.split())
            
            # Generate synthetic demand metrics (since real data doesn't have these)
            views = np.random.randint(100, 10000)
            add_to_cart = np.random.randint(10, int(views * 0.1))
            purchases = np.random.randint(1, int(add_to_cart * 0.3))
            stock_quantity = np.random.randint(10, 200)
            
            # Calculate derived features
            conversion_rate = purchases / views if views > 0 else 0
            stock_percentage = stock_quantity / 200.0
            
            # Generate competitor price (synthetic)
            competitor_price = selling_price * np.random.uniform(0.7, 1.3)
            price_ratio = selling_price / competitor_price if competitor_price > 0 else 1.0
            
            # Calculate optimal price (target variable)
            # This is a simplified calculation - in reality, this would be based on historical performance
            optimal_price = (
                selling_price * 0.6 +
                competitor_price * 0.25 +
                (list_price or selling_price) * 0.15
            ) + np.random.normal(0, selling_price * 0.05)
            
            # Create processed record
            processed_record = {
                'price': float(selling_price),
                'title_length': int(title_length),
                'word_count': int(word_count),
                'category': category,
                'views': int(views),
                'add_to_cart': int(add_to_cart),
                'purchases': int(purchases),
                'stock_quantity': int(stock_quantity),
                'competitor_price': float(competitor_price),
                'month': np.random.randint(1, 13),  # Random month
                'optimal_price': float(optimal_price),
                'conversion_rate': float(conversion_rate),
                'stock_percentage': float(stock_percentage),
                'price_ratio': float(price_ratio)
            }
            
            processed_data.append(processed_record)
            
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    # Convert to DataFrame
    processed_df = pd.DataFrame(processed_data)
    
    print(f"Processed {len(processed_df)} records")
    print(f"Final dataset shape: {processed_df.shape}")
    
    # Save processed data
    output_path = "data/amazon_processed_data.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    processed_df.to_csv(output_path, index=False)
    
    print(f"Processed data saved to {output_path}")
    
    # Print some statistics
    print("\nDataset Statistics:")
    print(f"Average price: ${processed_df['price'].mean():.2f}")
    print(f"Price range: ${processed_df['price'].min():.2f} - ${processed_df['price'].max():.2f}")
    print(f"Categories: {processed_df['category'].nunique()}")
    print(f"Average conversion rate: {processed_df['conversion_rate'].mean():.4f}")
    
    return True

def extract_price(price_str):
    """Extract numeric price from string"""
    if pd.isna(price_str) or price_str == '':
        return None
    
    # Remove currency symbols and extract numbers
    price_str = str(price_str)
    price_match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    
    if price_match:
        try:
            return float(price_match.group())
        except:
            return None
    return None

def extract_category(category_str):
    """Extract main category from category string"""
    if pd.isna(category_str) or category_str == '':
        return 'Other'
    
    # Split by | and take the first part
    categories = str(category_str).split('|')
    main_category = categories[0].strip()
    
    # Map to simplified categories
    category_mapping = {
        'Sports & Outdoors': 'sports',
        'Toys & Games': 'toys',
        'Electronics': 'electronics',
        'Home & Kitchen': 'home',
        'Clothing, Shoes & Jewelry': 'clothing',
        'Books': 'books',
        'Beauty & Personal Care': 'beauty',
        'Health & Household': 'health',
        'Automotive': 'automotive',
        'Tools & Home Improvement': 'tools',
        'Garden & Outdoor': 'garden',
        'Pet Supplies': 'pets',
        'Baby Products': 'baby',
        'Office Products': 'office',
        'Industrial & Scientific': 'industrial'
    }
    
    for key, value in category_mapping.items():
        if key in main_category:
            return value
    
    return 'other'

if __name__ == "__main__":
    print("=" * 60)
    print("Kaggle Amazon Dataset Processor")
    print("=" * 60)
    
    success = process_kaggle_amazon_data()
    
    if success:
        print("\n" + "=" * 60)
        print("Dataset processing completed successfully!")
        print("=" * 60)
    else:
        print("\nDataset processing failed!") 