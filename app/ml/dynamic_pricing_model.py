import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class DynamicPricingModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 128):
        super(DynamicPricingModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, 1)
        )
        
    def forward(self, x):
        return self.network(x)

class DynamicPricingEngine:
    def __init__(self, model_path: str = "app/ml/models/dynamic_pricing_model.pth"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'base_price', 'competitor_avg_price', 'demand_score', 
            'stock_level', 'seasonality_factor', 'user_engagement',
            'conversion_rate', 'time_since_last_price_change'
        ]
        
    def prepare_features(self, product_data: Dict) -> np.ndarray:
        """Prepare features for the model"""
        features = []
        for feature in self.feature_names:
            if feature in product_data:
                features.append(product_data[feature])
            else:
                features.append(0.0)  # Default value
        return np.array(features).reshape(1, -1)
    
    def train_model(self, training_data: List[Dict]):
        """Train the dynamic pricing model"""
        # Prepare training data
        X = []
        y = []
        
        for data_point in training_data:
            features = self.prepare_features(data_point)
            X.append(features.flatten())
            y.append(data_point['optimal_price'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize model
        self.model = DynamicPricingModel(input_size=len(self.feature_names))
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Training loop
        epochs = 100
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(torch.FloatTensor(X_train_scaled))
            loss = criterion(outputs.squeeze(), torch.FloatTensor(y_train))
            loss.backward()
            optimizer.step()
            
            if epoch % 20 == 0:
                print(f'Epoch {epoch}, Loss: {loss.item():.4f}')
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)
        joblib.dump(self.scaler, self.model_path.replace('.pth', '_scaler.pkl'))
        
        # Evaluate model
        self.model.eval()
        with torch.no_grad():
            test_outputs = self.model(torch.FloatTensor(X_test_scaled))
            test_loss = criterion(test_outputs.squeeze(), torch.FloatTensor(y_test))
            print(f'Test Loss: {test_loss.item():.4f}')
    
    def load_model(self):
        """Load the trained model"""
        if os.path.exists(self.model_path):
            self.model = DynamicPricingModel(input_size=len(self.feature_names))
            self.model.load_state_dict(torch.load(self.model_path))
            self.model.eval()
            
            scaler_path = self.model_path.replace('.pth', '_scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            return True
        return False
    
    def predict_optimal_price(self, product_data: Dict) -> float:
        """Predict optimal price for a product"""
        if self.model is None:
            if not self.load_model():
                return product_data.get('base_price', 0.0)
        
        features = self.prepare_features(product_data)
        features_scaled = self.scaler.transform(features)
        
        with torch.no_grad():
            prediction = self.model(torch.FloatTensor(features_scaled))
            return prediction.item()
    
    def calculate_demand_score(self, views: int, add_to_cart: int, purchases: int) -> float:
        """Calculate demand score based on user behavior"""
        if views == 0:
            return 0.0
        
        conversion_rate = purchases / views
        engagement_rate = (add_to_cart + purchases) / views
        
        return (conversion_rate * 0.6) + (engagement_rate * 0.4)
    
    def calculate_seasonality_factor(self, month: int) -> float:
        """Calculate seasonality factor based on month"""
        # Simple seasonality model - can be enhanced with more sophisticated approaches
        seasonal_factors = {
            1: 0.8, 2: 0.7, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.2,
            7: 1.3, 8: 1.2, 9: 1.1, 10: 1.0, 11: 1.2, 12: 1.4
        }
        return seasonal_factors.get(month, 1.0) 