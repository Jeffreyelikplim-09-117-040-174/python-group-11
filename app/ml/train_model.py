#!/usr/bin/env python3
"""
Training Script for Dynamic Pricing Model
Trains the PyTorch model using processed eCommerce data
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Add the parent directory to the path to import the model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the model from the same directory
from dynamic_pricing_model import DynamicPricingModel, DynamicPricingEngine

class ModelTrainer:
    def __init__(self, model_path: str = "app/ml/models/dynamic_pricing_model.pth"):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
    def load_data(self, data_path: str = "data/amazon_processed_data.csv"):
        """Load processed training data from Amazon dataset"""
        print("Loading Amazon training data...")
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Amazon processed data not found at {data_path}")
        
        df = pd.read_csv(data_path)
        print(f"Loaded Amazon dataset with shape: {df.shape}")
        
        # Process features for Amazon data
        df = self.process_amazon_features(df)
        
        # Select features and target
        feature_columns = [
            'price_log', 'title_length', 'word_count', 'category_encoded',
            'cat_mean_price', 'cat_std_price', 'price_percentile',
            'views', 'add_to_cart', 'purchases', 'conversion_rate',
            'stock_percentage', 'competitor_price', 'price_ratio', 'month'
        ]
        
        # Ensure all required columns exist
        for col in feature_columns:
            if col not in df.columns:
                print(f"Warning: Column {col} not found, adding default values")
                if col == 'price_log':
                    df[col] = np.log(df['price'] + 1)
                elif col == 'category_encoded':
                    df[col] = pd.Categorical(df['category']).codes
                elif col == 'conversion_rate':
                    df[col] = df['purchases'] / df['views'].replace(0, 1)
                elif col == 'stock_percentage':
                    df[col] = df['stock_quantity'] / df['stock_quantity'].max()
                elif col == 'price_ratio':
                    df[col] = df['price'] / df['competitor_price'].replace(0, 1)
                else:
                    df[col] = 0.0
        
        X = df[feature_columns].values
        y = df['optimal_price'].values
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"Training set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test, feature_columns
    
    def process_amazon_features(self, df):
        """Process Amazon dataset features"""
        print("Processing Amazon dataset features...")
        
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
        
        # Derived features
        df['conversion_rate'] = df['purchases'] / df['views'].replace(0, 1)
        df['stock_percentage'] = df['stock_quantity'] / df['stock_quantity'].max()
        df['price_ratio'] = df['price'] / df['competitor_price'].replace(0, 1)
        
        return df
    
    def create_data_loaders(self, X_train, X_test, y_train, y_test, batch_size=32):
        """Create PyTorch data loaders"""
        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train)
        y_train_tensor = torch.FloatTensor(y_train)
        X_test_tensor = torch.FloatTensor(X_test)
        y_test_tensor = torch.FloatTensor(y_test)
        
        # Create datasets
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        return train_loader, test_loader
    
    def train_model(self, train_loader, test_loader, input_size, epochs=100, lr=0.001):
        """Train the dynamic pricing model"""
        print("Initializing model...")
        
        # Initialize model
        model = DynamicPricingModel(input_size=input_size).to(self.device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
        
        # Training history
        train_losses = []
        test_losses = []
        
        print("Starting training...")
        for epoch in range(epochs):
            # Training phase
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
            
            # Validation phase
            model.eval()
            test_loss = 0.0
            predictions = []
            actuals = []
            
            with torch.no_grad():
                for batch_X, batch_y in test_loader:
                    batch_X = batch_X.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    outputs = model(batch_X).squeeze()
                    loss = criterion(outputs, batch_y)
                    test_loss += loss.item()
                    
                    predictions.extend(outputs.cpu().numpy())
                    actuals.extend(batch_y.cpu().numpy())
            
            # Calculate average losses
            avg_train_loss = train_loss / len(train_loader)
            avg_test_loss = test_loss / len(test_loader)
            
            train_losses.append(avg_train_loss)
            test_losses.append(avg_test_loss)
            
            # Update learning rate
            scheduler.step(avg_test_loss)
            
            # Print progress
            if epoch % 10 == 0:
                print(f"Epoch {epoch}/{epochs}")
                print(f"Train Loss: {avg_train_loss:.4f}")
                print(f"Test Loss: {avg_test_loss:.4f}")
                print(f"Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")
                print("-" * 50)
            
            # Early stopping
            if len(test_losses) > 20 and test_losses[-1] > test_losses[-20]:
                print("Early stopping triggered")
                break
        
        # Calculate final metrics
        final_metrics = self.calculate_metrics(predictions, actuals)
        
        return model, train_losses, test_losses, final_metrics
    
    def calculate_metrics(self, predictions, actuals):
        """Calculate model performance metrics"""
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)
        
        # Calculate percentage error
        mape = np.mean(np.abs((np.array(actuals) - np.array(predictions)) / np.array(actuals))) * 100
        
        return {
            'mse': mse,
            'mae': mae,
            'r2': r2,
            'mape': mape
        }
    
    def save_model(self, model, feature_columns, metrics, model_path=None):
        """Save the trained model and metadata"""
        if model_path is None:
            model_path = self.model_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        torch.save(model.state_dict(), model_path)
        
        # Save metadata
        metadata = {
            'feature_columns': feature_columns,
            'model_architecture': 'DynamicPricingModel',
            'training_date': datetime.now().isoformat(),
            'metrics': metrics,
            'device_used': str(self.device)
        }
        
        metadata_path = model_path.replace('.pth', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved to {model_path}")
        print(f"Metadata saved to {metadata_path}")
    
    def plot_training_history(self, train_losses, test_losses, save_path=None):
        """Plot training history"""
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label='Training Loss', color='blue')
        plt.plot(test_losses, label='Validation Loss', color='red')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training History')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
            print(f"Training history plot saved to {save_path}")
        else:
            plt.show()
    
    def evaluate_model(self, model, test_loader):
        """Evaluate the trained model"""
        model.eval()
        predictions = []
        actuals = []
        
        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X = batch_X.to(self.device)
                outputs = model(batch_X).squeeze()
                
                predictions.extend(outputs.cpu().numpy())
                actuals.extend(batch_y.numpy())
        
        metrics = self.calculate_metrics(predictions, actuals)
        
        print("Model Evaluation Results:")
        print(f"Mean Squared Error: {metrics['mse']:.4f}")
        print(f"Mean Absolute Error: {metrics['mae']:.4f}")
        print(f"R² Score: {metrics['r2']:.4f}")
        print(f"Mean Absolute Percentage Error: {metrics['mape']:.2f}%")
        
        return metrics
    
    def train(self, data_path: str = "data/amazon_processed_data.csv"):
        """Main training pipeline"""
        print("Starting model training pipeline...")
        
        # Load data
        X_train, X_test, y_train, y_test, feature_columns = self.load_data(data_path)
        
        # Create data loaders
        train_loader, test_loader = self.create_data_loaders(X_train, X_test, y_train, y_test)
        
        # Train model
        model, train_losses, test_losses, metrics = self.train_model(
            train_loader, test_loader, input_size=len(feature_columns)
        )
        
        # Save model
        self.save_model(model, feature_columns, metrics)
        
        # Plot training history
        plot_path = self.model_path.replace('.pth', '_training_history.png')
        self.plot_training_history(train_losses, test_losses, plot_path)
        
        # Evaluate model
        final_metrics = self.evaluate_model(model, test_loader)
        
        print("Training completed successfully!")
        return model, final_metrics

def main():
    """Main function to run the training"""
    trainer = ModelTrainer()
    
    try:
        model, metrics = trainer.train()
        print("Model training completed successfully!")
        print(f"Final R² Score: {metrics['r2']:.4f}")
    except Exception as e:
        print(f"Error during training: {e}")
        print("Please ensure the processed data is available at data/amazon_processed_data.csv")

if __name__ == "__main__":
    main() 