# Paystack Payment Integration Setup

## Overview
This application now uses **Paystack** as the only payment method for processing orders.

## Setup Instructions

### 1. Get Paystack API Keys

1. Go to [Paystack Dashboard](https://dashboard.paystack.com/)
2. Sign up or log in to your account
3. Navigate to **Settings** → **Developer** → **API Keys**
4. Copy your **Secret Key** and **Public Key**

### 2. Configure Environment Variables

1. Copy `env_example.txt` to `.env`:
   ```bash
   cp env_example.txt .env
   ```

2. Edit the `.env` file and replace the Paystack keys:
   ```env
   # Paystack Configuration (REQUIRED)
   PAYSTACK_SECRET_KEY=sk_test_your_actual_secret_key_here
   PAYSTACK_PUBLIC_KEY=pk_test_your_actual_public_key_here
   PAYSTACK_BASE_URL=https://api.paystack.co
   PAYSTACK_CURRENCY=GHS
   ```

### 3. API Keys Format

- **Test Keys** (for development):
  - Secret Key: `sk_test_...`
  - Public Key: `pk_test_...`

- **Live Keys** (for production):
  - Secret Key: `sk_live_...`
  - Public Key: `pk_live_...`

### 4. Payment Flow

1. **Order Creation**: When a user creates an order, the system:
   - Calculates total amount (including tax and shipping)
   - Initializes Paystack transaction
   - Returns authorization URL for payment

2. **Payment Processing**: 
   - User is redirected to Paystack payment page
   - User completes payment
   - Paystack redirects back to your callback URL

3. **Payment Verification**:
   - System verifies payment status with Paystack
   - Updates order status to "completed" if successful

### 5. Testing

For testing, you can use Paystack's test cards:
- **Card Number**: 4084 0840 8408 4081
- **Expiry**: Any future date
- **CVV**: Any 3 digits
- **PIN**: Any 4 digits

### 6. Webhook Setup (Optional)

For production, set up webhooks to receive payment notifications:
1. Go to Paystack Dashboard → Settings → Developer → Webhooks
2. Add webhook URL: `https://yourdomain.com/payment/webhook`
3. Select events: `charge.success`, `transfer.success`

## API Endpoints

- `POST /orders/` - Create order with Paystack payment
- `POST /orders/verify-payment/{reference}` - Verify payment status
- `GET /orders/` - Get user orders
- `GET /orders/{order_id}` - Get specific order details

## Error Handling

The system handles common Paystack errors:
- Invalid API keys
- Insufficient funds
- Network errors
- Payment verification failures

## Security Notes

- Never commit your `.env` file to version control
- Use test keys for development
- Switch to live keys only for production
- Keep your secret key secure and private 