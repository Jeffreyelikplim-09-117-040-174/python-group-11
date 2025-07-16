#!/usr/bin/env python3
"""
Dataset Processor for Dynamic Pricing Model
Processes eCommerce data for ML model training
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

class DatasetProcessor:
    def __init__(self, output_path: str = "data/processed_data.csv"):
        self.output_path = output_path
        
    def generate_sample_data(self, num_products: int = 1000):
        """Generate sample eCommerce data for training"""
        print("Generating sample eCommerce data...")
        
        # Product categories
        categories = ['electronics', 'clothing', 'books', 'home', 'sports', 'beauty', 'toys']
        
        # Generate product data
        products = []
        for i in range(num_products):
            category = random.choice(categories)
            base_price = random.uniform(50, 5000)
            
            # Generate realistic product features
            product = {
                'product_id': i + 1,
                'name': f"Product {i + 1}",
                'category': category,
                'base_price': base_price,
                'current_price': base_price * random.uniform(0.8, 1.2),
                'title_length': random.randint(20, 100),
                'word_count': random.randint(5, 20),
                'views': random.randint(100, 10000),
                'add_to_cart': random.randint(10, 1000),
                'purchases': random.randint(1, 100),
                'stock_quantity': random.randint(10, 200),
                'competitor_price': base_price * random.uniform(0.7, 1.3),
                'month': random.randint(1, 12)
            }
            
            # Calculate derived features
            product['conversion_rate'] = product['purchases'] / max(product['views'], 1)
            product['stock_percentage'] = product['stock_quantity'] / 200.0
            product['price_ratio'] = product['current_price'] / max(product['competitor_price'], 1)
            product['price_percentile'] = random.uniform(0, 1)
            
            products.append(product)
        
        return pd.DataFrame(products)
    
    def process_features(self, df: pd.DataFrame):
        """Process and engineer features for ML model"""
        print("Processing features...")
        
        # Category encoding
        df['category_encoded'] = pd.Categorical(df['category']).codes
        
        # Price features
        df['price_log'] = np.log(df['current_price'] + 1)
        
        # Category statistics
        cat_stats = df.groupby('category').agg({
            'current_price': ['mean', 'std']
        }).reset_index()
        cat_stats.columns = ['category', 'cat_mean_price', 'cat_std_price']
        
        df = df.merge(cat_stats, on='category', how='left')
        
        # Fill NaN values
        df['cat_std_price'] = df['cat_std_price'].fillna(df['cat_std_price'].mean())
        
        # Calculate optimal price (target variable)
        # This is a simplified calculation - in reality, this would be more complex
        df['optimal_price'] = (
            df['current_price'] * 0.7 +  # Base price influence
            df['competitor_price'] * 0.2 +  # Competition influence
            df['cat_mean_price'] * 0.1  # Category average influence
        )
        
        # Add some noise to make it realistic
        df['optimal_price'] += np.random.normal(0, df['current_price'] * 0.05)
        df['optimal_price'] = np.maximum(df['optimal_price'], df['current_price'] * 0.5)
        
        return df
    
    def process(self, use_sample_data: bool = True):
        """Main processing function"""
        if use_sample_data:
            df = self.generate_sample_data()
        else:
            # Load real data if available
            raise NotImplementedError("Real data processing not implemented yet")
        
        # Process features
        df = self.process_features(df)
        
        # Save processed data
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_csv(self.output_path, index=False)
        
        print(f"Processed data saved to {self.output_path}")
        print(f"Dataset shape: {df.shape}")
        
        return df 