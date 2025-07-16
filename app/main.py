from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import auth, products, cart, orders, admin, analytics
from app.core.config import settings
from app.core.database import engine
from app.models import base
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.ml.train_model import ModelTrainer
from app.ml.dynamic_pricing_model import DynamicPricingEngine
from app.models.product import Product
from app.core.database import SessionLocal
import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Driven Dynamic Pricing Engine",
    description="Ecommerce platform with AI-powered dynamic pricing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

def retrain_and_update_prices():
    logger.info("Starting scheduled model retraining and price update...")
    try:
        # Retrain the model
        trainer = ModelTrainer()
        trainer.train()
        logger.info("Model retrained successfully.")
        # Load the trained model for price prediction
        engine = DynamicPricingEngine()
        engine.load_model()
        # Open DB session
        db: Session = SessionLocal()
        products = db.query(Product).filter(Product.is_active == True).all()
        updated_count = 0
        for product in products:
            # Example: gather features for prediction
            # You may want to fetch demand, competition, and user behavior metrics here
            product_data = {
                'base_price': product.base_price,
                'competitor_avg_price': product.base_price,  # TODO: Replace with real competitor data
                'demand_score': 1.0,  # TODO: Replace with real demand score
                'stock_level': product.stock_quantity,
                'seasonality_factor': engine.calculate_seasonality_factor(datetime.datetime.now().month),
                'user_engagement': 1.0,  # TODO: Replace with real engagement
                'conversion_rate': 1.0,  # TODO: Replace with real conversion rate
                'time_since_last_price_change': 1.0  # TODO: Replace with real value
            }
            new_price = engine.predict_optimal_price(product_data)
            if new_price > 0:
                product.current_price = float(new_price)
                updated_count += 1
        db.commit()
        db.close()
        logger.info(f"Updated prices for {updated_count} products.")
    except Exception as e:
        logger.error(f"Scheduled retraining or price update failed: {e}")

# Set up the scheduler to run daily
scheduler = BackgroundScheduler()
scheduler.add_job(retrain_and_update_prices, 'interval', days=1)
scheduler.start()

@app.get("/")
async def home(request: Request):
    """Main ecommerce store page"""
    return templates.TemplateResponse("store.html", {"request": request})

@app.get("/checkout")
async def checkout_page(request: Request):
    """Checkout page"""
    return templates.TemplateResponse("checkout.html", {"request": request})

@app.get("/admin")
async def admin_dashboard(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/analytics")
async def analytics_dashboard(request: Request):
    """Analytics dashboard page"""
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/payment/callback")
async def payment_callback(request: Request):
    """Payment callback page for Paystack redirects"""
    return templates.TemplateResponse("payment_callback.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 