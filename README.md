# AI-Driven Dynamic Pricing E-commerce Platform

A modern e-commerce platform with AI-powered dynamic pricing, real-time analytics, and intelligent inventory management.

## Features

### 🛒 E-commerce Features
- **Product Catalog**: Browse products with dynamic pricing
- **Shopping Cart**: Add, remove, and manage cart items
- **Checkout System**: Complete checkout with payment processing
- **Order Management**: Track orders and view order history
- **User Authentication**: Secure login/registration system

### 🤖 AI & Analytics
- **Dynamic Pricing**: AI-driven price adjustments based on demand
- **Real-time Analytics**: Track user behavior and sales metrics
- **Competitor Monitoring**: Automated price comparison
- **Inventory Optimization**: Smart stock management

### 👨‍💼 Admin Features
- **Admin Dashboard**: Comprehensive management interface
- **Product Management**: Add, edit, and manage products
- **Order Processing**: Process and update order status
- **Analytics Dashboard**: View business insights and trends

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd python-group-11
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database**
   ```bash
   python add_sample_data.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Open your browser**
   Navigate to: `http://localhost:8000`

## 📱 How to Use the Website

### For Customers

1. **Browse Products**
   - Visit the homepage to see all available products
   - Products display current prices with dynamic pricing indicators
   - Click on products to view details

2. **Add to Cart**
   - Click "Add to Cart" on any product
   - You must be logged in to add items to cart
   - View your cart by clicking the cart icon in the navigation

3. **Checkout Process**
   - Click "Checkout" from your cart
   - Fill in shipping information:
     - First and Last Name
     - Email Address
     - Phone Number
     - Shipping Address
     - City and Postal Code
   - Enter payment information:
     - Card Number (formatted automatically)
     - Expiry Date (MM/YY format)
     - CVV
     - Name on Card
   - Add optional order notes
   - Accept terms and conditions
   - Click "Place Order"

4. **Order Confirmation**
   - After successful payment, you'll see an order confirmation
   - Order details include order number, total amount, and shipping address
   - You can view your order history in your account

### For Administrators

1. **Access Admin Dashboard**
   - Login with admin credentials: `admin@example.com` / `admin123`
   - Navigate to `/admin` or click "Admin" in the navigation

2. **Manage Products**
   - Add new products with pricing and inventory
   - Edit existing product details
   - Monitor dynamic pricing changes

3. **Process Orders**
   - View all customer orders
   - Update order status (Pending, Processing, Shipped, Delivered)
   - Track order analytics

4. **View Analytics**
   - Access the analytics dashboard at `/analytics`
   - Monitor sales trends, popular products, and user behavior
   - View AI-driven insights and recommendations

## 🔐 Default Login Credentials

### Test User
- **Email**: `test@example.com`
- **Password**: `password123`
- **Role**: Customer

### Admin User
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Role**: Administrator

## 🛠️ Technical Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **API**: RESTful API with automatic documentation

### Frontend
- **Templates**: Jinja2 with Bootstrap 5
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Styling**: Bootstrap 5 with custom CSS
- **Icons**: Font Awesome

### AI/ML Components
- **Dynamic Pricing**: Machine learning models for price optimization
- **Analytics**: Real-time data processing and visualization
- **Competitor Monitoring**: Web scraping and price comparison

## 📁 Project Structure

```
python-group-11/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── auth.py         # Authentication
│   │   ├── products.py     # Product management
│   │   ├── cart.py         # Shopping cart
│   │   ├── orders.py       # Order processing
│   │   ├── admin.py        # Admin functions
│   │   └── analytics.py    # Analytics and tracking
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings
│   │   └── database.py     # Database setup
│   ├── models/             # Database models
│   │   ├── user.py         # User model
│   │   ├── product.py      # Product model
│   │   └── order.py        # Order models
│   ├── ml/                 # Machine learning
│   │   └── dynamic_pricing_model.py
│   ├── static/             # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/          # HTML templates
│   └── main.py            # Main application
├── data/                   # Data processing
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
├── run.py                 # Application runner
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./dynamic_pricing.db
DEBUG=True
```

### Database
The application uses SQLite by default. For production, consider using PostgreSQL or MySQL.

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Production Deployment
1. Set up a production server (Ubuntu, CentOS, etc.)
2. Install Python and dependencies
3. Configure environment variables
4. Set up a reverse proxy (Nginx)
5. Use a process manager (systemd, supervisor)
6. Configure SSL certificates

## 📊 API Documentation

Once the application is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the logs in the `logs/` directory
2. Verify your database is properly initialized
3. Ensure all dependencies are installed
4. Check the API documentation at `/docs`

## 🔄 Updates and Maintenance

- **Regular Updates**: Keep dependencies updated
- **Database Backups**: Regular backups of the SQLite database
- **Log Monitoring**: Monitor application logs for errors
- **Performance**: Monitor response times and optimize as needed

---

**Happy Shopping! 🛍️** 