# Admin Login Guide

## How to Test Admin Login and Access

### Step 1: Start the Application
```bash
python run.py
```

### Step 2: Access the Website
1. Open your browser
2. Go to: `http://localhost:8000`

### Step 3: Login as Admin
1. Click the "Login" button in the top navigation
2. Enter the admin credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Click "Login"

### Step 4: Verify Admin Redirect
After successful login, you should see:
1. A success message: "Welcome Admin! Redirecting to admin dashboard..."
2. After 1 second, you'll be automatically redirected to: `http://localhost:8000/admin`

### Step 5: Admin Dashboard Features
Once on the admin dashboard, you can:
- **Dashboard**: View statistics and recent activity
- **Products**: Add, edit, and manage products
- **Dynamic Pricing**: Update product prices using AI
- **Users**: Manage user accounts and permissions
- **Analytics**: View detailed analytics and reports

## Troubleshooting

### If Admin Login Doesn't Redirect:
1. **Check Browser Console**: Press F12 and look for any JavaScript errors
2. **Debug Admin Status**: In the browser console, type: `debugAdminStatus()`
3. **Manual Access**: Try going directly to `http://localhost:8000/admin`

### If Admin Dashboard Shows Errors:
1. **Check Network Tab**: In browser dev tools, look for failed API calls
2. **Verify Token**: The admin page should automatically check your authentication
3. **Refresh Page**: Sometimes a page refresh helps

### Common Issues:
- **401 Unauthorized**: Token expired or invalid - try logging in again
- **403 Forbidden**: User doesn't have admin role - verify credentials
- **Page Not Loading**: Check if the server is running properly

## Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`

## Test Script
You can also run the automated test:
```bash
python test_admin_login.py
```

This will verify all admin functionality is working correctly.

## Admin API Endpoints
- `/api/admin/stats` - Dashboard statistics
- `/api/admin/users` - User management
- `/api/admin/recent-price-changes` - Price change history
- `/api/products/{id}/update-price` - Update product prices

All admin endpoints require proper authentication and admin role. 