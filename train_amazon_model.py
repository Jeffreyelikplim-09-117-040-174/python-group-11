#!/usr/bin/env python3
"""
Amazon Dataset AI Model Training Script
"""

import pandas as pd
import numpy as np
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import json

class AmazonModelTrainer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
    def generate_amazon_data(self, num_samples=10000):
        """Generate synthetic Amazon-like data for training"""
        print("Generating Amazon-like training data...")
        
        np.random.seed(42)
        
        # Generate realistic Amazon product data
        categories = ['electronics', 'clothing', 'books', 'home', 'sports', 'beauty', 'toys']
        
        data = []
        for i in range(num_samples):
            category = np.random.choice(categories)
            
            # Generate realistic price based on category
            if category == 'electronics':
                base_price = np.random.uniform(50, 2000)
            elif category == 'clothing':
                base_price = np.random.uniform(20, 500)
            elif category == 'books':
                base_price = np.random.uniform(10, 200)
            else:
                base_price = np.random.uniform(30, 800)
            
            # Add some variation
            current_price = base_price * np.random.uniform(0.8, 1.2)
            
            # Generate features
            product = {
                'price': current_price,
                'title_length': np.random.randint(20, 100),
                'word_count': np.random.randint(5, 20),
                'category': category,
                'views': np.random.randint(100, 10000),
                'add_to_cart': np.random.randint(10, 1000),
                'purchases': np.random.randint(1, 100),
                'stock_quantity': np.random.randint(10, 200),
                'competitor_price': current_price * np.random.uniform(0.7, 1.3),
                'month': np.random.randint(1, 13)
            }
            
            # Calculate derived features
            product['conversion_rate'] = product['purchases'] / product['views']
            product['stock_percentage'] = product['stock_quantity'] / 200.0
            product['price_ratio'] = product['price'] / product['competitor_price']
            
            # Calculate optimal price (target variable)
            product['optimal_price'] = (
                product['price'] * 0.6 +
                product['competitor_price'] * 0.25 +
                base_price * 0.15
            ) + np.random.normal(0, product['price'] * 0.05)
            
            data.append(product)
        
        return pd.DataFrame(data)
    
    def process_features(self, df):
        """Process features for the model"""
        print("Processing features...")
        
        # Category encoding
        df['category_encoded'] = pd.Categorical(df['category']).codes
        
        # Price features
        df['price_log'] = np.log(df['price'] + 1)
        
        # Category statistics
        cat_stats = df.groupby('category').agg({
            'price': ['mean', 'std']
        }).reset_index()
        cat_stats.columns = ['category', 'cat_mean_price', 'cat_std_price']
        
        df = df.merge(cat_stats, on='category', how='left')
        df['cat_std_price'] = df['cat_std_price'].fillna(df['cat_std_price'].mean())
        
        # Price percentile
        df['price_percentile'] = df.groupby('category')['price'].rank(pct=True)
        
        return df
    
    def train_model(self, data_path="data/amazon_processed_data.csv"):
        """Train the dynamic pricing model"""
        print("Training Amazon dynamic pricing model...")
        
        # Generate or load data
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            print(f"Loaded existing data: {df.shape}")
        else:
            df = self.generate_amazon_data()
            df = self.process_features(df)
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            df.to_csv(data_path, index=False)
            print(f"Generated new data: {df.shape}")
        
        # Select features and target
        feature_columns = [
            'price_log', 'title_length', 'word_count', 'category_encoded',
            'cat_mean_price', 'cat_std_price', 'price_percentile',
            'views', 'add_to_cart', 'purchases', 'conversion_rate',
            'stock_percentage', 'competitor_price', 'price_ratio', 'month'
        ]
        
        X = df[feature_columns].values
        y = df['optimal_price'].values
        
        # Split and scale data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Create data loaders
        train_dataset = TensorDataset(torch.FloatTensor(X_train_scaled), torch.FloatTensor(y_train))
        test_dataset = TensorDataset(torch.FloatTensor(X_test_scaled), torch.FloatTensor(y_test))
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        # Define model
        class DynamicPricingModel(nn.Module):
            def __init__(self, input_size):
                super().__init__()
                self.layer1 = nn.Linear(input_size, 128)
                self.layer2 = nn.Linear(128, 64)
                self.layer3 = nn.Linear(64, 32)
                self.layer4 = nn.Linear(32, 1)
                self.relu = nn.ReLU()
                self.dropout = nn.Dropout(0.2)
                
            def forward(self, x):
                x = self.relu(self.layer1(x))
                x = self.dropout(x)
                x = self.relu(self.layer2(x))
                x = self.dropout(x)
                x = self.relu(self.layer3(x))
                x = self.layer4(x)
                return x
        
        # Initialize model
        model = DynamicPricingModel(input_size=len(feature_columns)).to(self.device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        # Training loop
        print("Starting training...")
        for epoch in range(50):
            model.train()
            train_loss = 0.0
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_X).squeeze()
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Train Loss: {train_loss/len(train_loader):.4f}")
        
        # Evaluate model
        model.eval()
        predictions = []
        actuals = []
        
        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                outputs = model(batch_X).squeeze()
                predictions.extend(outputs.cpu().numpy())
                actuals.extend(batch_y.cpu().numpy())
        
        # Calculate metrics
        mse = float(mean_squared_error(actuals, predictions))
        r2 = float(r2_score(actuals, predictions))
        
        print(f"\nModel Performance:")
        print(f"MSE: {mse:.4f}")
        print(f"R² Score: {r2:.4f}")
        
        # Save model
        model_path = "app/ml/models/amazon_dynamic_pricing_model.pth"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        torch.save(model.state_dict(), model_path)
        
        # Save metadata
        metadata = {
            'feature_columns': feature_columns,
            'training_date': str(pd.Timestamp.now()),
            'metrics': {'mse': mse, 'r2': r2},
            'dataset': 'Amazon Product Dataset (Synthetic)'
        }
        
        metadata_path = model_path.replace('.pth', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\nModel saved to {model_path}")
        print(f"Metadata saved to {metadata_path}")
        
        return model, metadata

def main():
    print("=" * 60)
    print("Amazon Dataset AI Model Training")
    print("=" * 60)
    
    trainer = AmazonModelTrainer()
    model, metadata = trainer.train_model()
    
    print("\n" + "=" * 60)
    print("Training completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main() 