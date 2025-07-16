from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./dynamic_pricing.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    
    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_your_stripe_secret_key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_your_stripe_publishable_key"
    
    # Paystack Configuration
    PAYSTACK_SECRET_KEY: str = "sk_test_your_paystack_secret_key_here"
    PAYSTACK_PUBLIC_KEY: str = "pk_test_your_paystack_public_key_here"
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"
    PAYSTACK_CURRENCY: str = "GHS"  # Ghanaian Cedi
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # ML Model
    MODEL_PATH: str = "app/ml/models/dynamic_pricing_model.pth"
    
    # Web Scraping
    SCRAPING_DELAY: int = 2
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file

settings = Settings() 