# 🚀 Quick Setup Guide

## Windows Users

### Option 1: One-Click Start (Recommended)
1. Double-click `start_website.bat`
2. Wait for the setup to complete
3. Open your browser and go to `http://localhost:8000`

### Option 2: Manual Setup
1. Open Command Prompt in this folder
2. Run: `python -m venv venv`
3. Run: `venv\Scripts\activate`
4. Run: `pip install -r requirements.txt`
5. Run: `python add_sample_data.py`
6. Run: `python run.py`
7. Open browser to `http://localhost:8000`

## macOS/Linux Users

### Option 1: One-Click Start (Recommended)
1. Open Terminal in this folder
2. Run: `./start_website.sh`
3. Wait for the setup to complete
4. Open your browser and go to `http://localhost:8000`

### Option 2: Manual Setup
1. Open Terminal in this folder
2. Run: `python3 -m venv venv`
3. Run: `source venv/bin/activate`
4. Run: `pip install -r requirements.txt`
5. Run: `python add_sample_data.py`
6. Run: `python run.py`
7. Open browser to `http://localhost:8000`

## 🔐 Login Credentials

### Test Customer Account
- **Email**: `test@example.com`
- **Password**: `password123`

### Admin Account
- **Email**: `admin@example.com`
- **Password**: `admin123`

## 🛒 How to Test the Checkout

1. **Login** with the test account
2. **Browse products** on the homepage
3. **Add items to cart** by clicking "Add to Cart"
4. **View cart** by clicking the cart icon
5. **Click "Checkout"** to go to the checkout page
6. **Fill in the form**:
   - Shipping information (name, address, etc.)
   - Payment information (use any test card numbers)
   - Accept terms and conditions
7. **Click "Place Order"** to complete the purchase
8. **View order confirmation** with order details

## 📱 Website Features

- **Homepage**: Browse all products with dynamic pricing
- **Product Details**: View individual product information
- **Shopping Cart**: Manage your cart items
- **Checkout**: Complete purchase with payment
- **Admin Dashboard**: Manage products and orders (admin only)
- **Analytics**: View business insights (admin only)

## 🆘 Troubleshooting

### Common Issues

1. **"Python not found"**
   - Install Python 3.8+ from https://python.org
   - Make sure Python is added to PATH

2. **"Port 8000 already in use"**
   - Close other applications using port 8000
   - Or change the port in `run.py`

3. **"Database error"**
   - Delete `dynamic_pricing.db` and run `python add_sample_data.py` again

4. **"Module not found"**
   - Make sure you're in the virtual environment
   - Run `pip install -r requirements.txt`

### Getting Help

- Check the full README.md for detailed documentation
- View API docs at `http://localhost:8000/docs` when running
- Check logs in the `logs/` directory

---

**Happy Shopping! 🛍️** 