// Main JavaScript for Dynamic Pricing Engine

// Global variables
let currentUser = null;
let cartItems = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    setupEventListeners();
    updateCartCount();
});

// Check authentication status
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    if (token) {
        fetchCurrentUser();
    } else {
        showAuthButtons();
    }
}

// Fetch current user information
async function fetchCurrentUser() {
    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            showUserInfo();
        } else {
            localStorage.removeItem('access_token');
            showAuthButtons();
        }
    } catch (error) {
        console.error('Error fetching user:', error);
        showAuthButtons();
    }
}

// Show authentication buttons
function showAuthButtons() {
    const userDropdown = document.getElementById('userDropdown');
    const cartIcon = document.getElementById('cartIcon');
    
    if (userDropdown) {
        userDropdown.style.display = 'none';
    }
    
    if (cartIcon) {
        cartIcon.style.display = 'none';
    }
}

// Show user information
function showUserInfo() {
    const userDropdown = document.getElementById('userDropdown');
    const cartIcon = document.getElementById('cartIcon');
    
    if (userDropdown) {
        userDropdown.style.display = 'block';
        userDropdown.textContent = currentUser.username;
    }
    
    if (cartIcon) {
        cartIcon.style.display = 'block';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Cart icon
    const cartIcon = document.getElementById('cartIcon');
    if (cartIcon) {
        cartIcon.addEventListener('click', showCart);
    }
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            
            bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
            showToast('Login successful!', 'success');
            
            // Directly check user role after login
            try {
                const userResponse = await fetch('/api/auth/me', {
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`
                    }
                });
                
                if (userResponse.ok) {
                    const user = await userResponse.json();
                    currentUser = user;
                    showUserInfo();
                    
                    // Check if user is admin and redirect
                    if (user.role === 'admin') {
                        showToast('Welcome Admin! Redirecting to admin dashboard...', 'success');
                        setTimeout(() => {
                            window.location.href = '/admin';
                        }, 1000);
                        return;
                    }
                }
            } catch (userError) {
                console.error('Error fetching user info:', userError);
            }
            
            // If not admin, load cart
            loadCart();
        } else {
            const error = await response.json();
            showToast(error.detail, 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed', 'error');
    }
}

// Handle registration
async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const fullName = document.getElementById('registerFullName').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                username: username,
                full_name: fullName,
                password: password
            })
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
            showToast('Registration successful! Please login.', 'success');
            
            // Clear form
            document.getElementById('registerForm').reset();
        } else {
            const error = await response.json();
            showToast(error.detail, 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Registration failed', 'error');
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    currentUser = null;
    cartItems = [];
    
    showAuthButtons();
    updateCartCount();
    showToast('Logged out successfully', 'info');
    
    // Redirect to home page
    window.location.href = '/';
}

// Load cart items
async function loadCart() {
    if (!getToken()) return;
    
    try {
        const response = await fetch('/api/cart/', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            cartItems = await response.json();
            updateCartCount();
        }
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

// Update cart count
function updateCartCount() {
    const cartCount = document.getElementById('cartCount');
    if (cartCount) {
        cartCount.textContent = cartItems.length;
    }
}

// Show cart modal
function showCart() {
    if (!getToken()) {
        showToast('Please login to view cart', 'error');
        return;
    }
    
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = '<p class="text-center text-muted">Your cart is empty</p>';
        cartTotal.textContent = '0.00';
    } else {
        cartItemsContainer.innerHTML = cartItems.map(item => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <h6 class="mb-0">${item.product_name}</h6>
                    <small class="text-muted">GHS ${item.product_price.toFixed(2)} x ${item.quantity}</small>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <span class="fw-bold">GHS ${item.total_price.toFixed(2)}</span>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
        const total = cartItems.reduce((sum, item) => sum + item.total_price, 0);
        cartTotal.textContent = total.toFixed(2);
    }
    
    new bootstrap.Modal(document.getElementById('cartModal')).show();
}

// Remove item from cart
async function removeFromCart(itemId) {
    try {
        const response = await fetch(`/api/cart/remove/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            await loadCart();
            showCart(); // Refresh cart modal
            showToast('Item removed from cart', 'success');
        } else {
            const error = await response.json();
            showToast(error.detail, 'error');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showToast('Error removing item', 'error');
    }
}

// Clear cart
async function clearCart() {
    try {
        const response = await fetch('/api/cart/clear', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            cartItems = [];
            updateCartCount();
            showCart(); // Refresh cart modal
            showToast('Cart cleared', 'success');
        } else {
            const error = await response.json();
            showToast(error.detail, 'error');
        }
    } catch (error) {
        console.error('Error clearing cart:', error);
        showToast('Error clearing cart', 'error');
    }
}

// Initialize popovers
document.addEventListener('DOMContentLoaded', function() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize checkout if on checkout page
    initializeCheckout();
});

// Enhanced checkout functionality
function checkout() {
    if (!getToken()) {
        showToast('Please login to checkout', 'error');
        return;
    }
    
    // Redirect to checkout page
    window.location.href = '/checkout';
}

// Initialize checkout page
function initializeCheckout() {
    if (document.getElementById('checkoutForm')) {
        loadCartForCheckout();
        setupCheckoutForm();
        setupFormValidation();
    }
}

// Load cart items for checkout
async function loadCartForCheckout() {
    if (!getToken()) return;
    
    try {
        const response = await fetch('/api/cart/', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            const cartItems = await response.json();
            displayCheckoutItems(cartItems);
            calculateCheckoutTotals(cartItems);
        }
    } catch (error) {
        console.error('Error loading cart for checkout:', error);
        showToast('Error loading cart items', 'error');
    }
}

// Display checkout items with delete functionality
function displayCheckoutItems(cartItems) {
    const cartItemsContainer = document.getElementById('cartItems');
    if (!cartItemsContainer) return;
    
    if (!cartItems || cartItems.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <h6>Your cart is empty</h6>
                <p class="text-muted">Add some products to get started</p>
                <a href="/" class="btn btn-primary">Continue Shopping</a>
            </div>
        `;
        return;
    }
    
    let itemsHTML = '';
    
    cartItems.forEach(item => {
        const itemTotal = item.quantity * item.price_at_time;
        itemsHTML += `
            <div class="cart-item" data-item-id="${item.id}">
                <div class="cart-item-header">
                    <h6 class="cart-item-title">${item.product_name}</h6>
                    <button type="button" class="cart-item-delete" onclick="removeFromCheckout(${item.id})" title="Remove item">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="cart-item-details">
                    <span class="cart-item-price">GHS ${item.price_at_time.toFixed(2)}</span>
                    <div class="cart-item-quantity">
                        <span class="text-muted">Qty:</span>
                        <div class="quantity-control">
                            <button type="button" class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity - 1})" ${item.quantity <= 1 ? 'disabled' : ''}>
                                <i class="fas fa-minus"></i>
                            </button>
                            <input type="number" class="quantity-input" value="${item.quantity}" min="1" max="99" 
                                   onchange="updateQuantity(${item.id}, this.value)" onblur="updateQuantity(${item.id}, this.value)">
                            <button type="button" class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                </div>
                <div class="cart-item-total">
                    GHS ${itemTotal.toFixed(2)}
                </div>
            </div>
        `;
    });
    
    cartItemsContainer.innerHTML = itemsHTML;
}

// Remove item from checkout
async function removeFromCheckout(itemId) {
    if (!confirm('Are you sure you want to remove this item from your cart?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/cart/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            showToast('Item removed from cart', 'success');
            // Reload cart items
            await loadCartForCheckout();
            // Update cart count
            updateCartCount();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to remove item', 'error');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showToast('Failed to remove item', 'error');
    }
}

// Update quantity in checkout
async function updateQuantity(itemId, newQuantity) {
    newQuantity = parseInt(newQuantity);
    
    if (newQuantity < 1) {
        newQuantity = 1;
    }
    
    if (newQuantity > 99) {
        newQuantity = 99;
    }
    
    try {
        const response = await fetch(`/api/cart/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                quantity: newQuantity
            })
        });
        
        if (response.ok) {
            // Reload cart items to reflect changes
            await loadCartForCheckout();
            // Update cart count
            updateCartCount();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to update quantity', 'error');
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
        showToast('Failed to update quantity', 'error');
    }
}

// Calculate checkout totals
function calculateCheckoutTotals(cartItems) {
    const subtotalElement = document.getElementById('subtotal');
    const shippingElement = document.getElementById('shipping');
    const taxElement = document.getElementById('tax');
    const totalElement = document.getElementById('total');
    
    if (!subtotalElement || !shippingElement || !taxElement || !totalElement) return;
    
    const subtotal = cartItems.reduce((sum, item) => sum + item.total_price, 0);
    const shipping = subtotal > 1000 ? 0 : 50; // Free shipping over GHS 1000
    const tax = (subtotal + shipping) * 0.125; // 12.5% VAT
    const total = subtotal + shipping + tax;
    
    subtotalElement.textContent = `GHS ${subtotal.toFixed(2)}`;
    shippingElement.textContent = `GHS ${shipping.toFixed(2)}`;
    taxElement.textContent = `GHS ${tax.toFixed(2)}`;
    totalElement.textContent = `GHS ${total.toFixed(2)}`;
}

// Setup checkout form
function setupCheckoutForm() {
    const checkoutForm = document.getElementById('checkoutForm');
    if (!checkoutForm) return;
    
    checkoutForm.addEventListener('submit', handleCheckoutSubmission);
    
    // Auto-fill user information if available
    if (currentUser) {
        const emailField = document.getElementById('email');
        if (emailField) {
            emailField.value = currentUser.email || '';
        }
        
        const fullName = currentUser.full_name || '';
        if (fullName) {
            const nameParts = fullName.split(' ');
            const firstNameField = document.getElementById('firstName');
            const lastNameField = document.getElementById('lastName');
            
            if (firstNameField && nameParts.length > 0) {
                firstNameField.value = nameParts[0];
            }
            if (lastNameField && nameParts.length > 1) {
                lastNameField.value = nameParts.slice(1).join(' ');
            }
        }
    }
}

// Setup payment method selection
function setupPaymentMethodSelection() {
    const paymentRadios = document.querySelectorAll('input[name="paymentMethod"]');
    const paymentDetails = document.getElementById('paymentDetails');
    
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                showPaymentDetails(this.value);
            }
        });
    });
    
    // Setup crypto type selection
    const cryptoTypeSelect = document.getElementById('cryptoType');
    if (cryptoTypeSelect) {
        cryptoTypeSelect.addEventListener('change', function() {
            if (this.value) {
                generateCryptoPaymentInfo(this.value);
            } else {
                document.getElementById('cryptoPaymentInfo').style.display = 'none';
            }
        });
    }
}

// Show payment details based on selected method
function showPaymentDetails(paymentMethod) {
    const paymentDetails = document.getElementById('paymentDetails');
    const allDetails = document.querySelectorAll('.payment-details');
    
    // Hide all payment details
    allDetails.forEach(detail => {
        detail.style.display = 'none';
    });
    
    // Show payment details container
    paymentDetails.style.display = 'block';
    
    // Show specific payment details
    switch (paymentMethod) {
        case 'mobile_money':
            document.getElementById('mobileMoneyDetails').style.display = 'block';
            break;
        case 'paypal':
            document.getElementById('paypalDetails').style.display = 'block';
            break;
        case 'bank_transfer':
            document.getElementById('bankTransferDetails').style.display = 'block';
            generateBankReference();
            break;
        case 'card':
            document.getElementById('cardDetails').style.display = 'block';
            break;
        case 'crypto':
            document.getElementById('cryptoDetails').style.display = 'block';
            break;
    }
}

// Generate bank transfer reference
function generateBankReference() {
    const orderRef = 'ORDER-' + Date.now().toString().slice(-8);
    const bankRefElement = document.getElementById('orderRef');
    if (bankRefElement) {
        bankRefElement.textContent = orderRef;
    }
}

// Generate crypto payment information
function generateCryptoPaymentInfo(cryptoType) {
    const cryptoPaymentInfo = document.getElementById('cryptoPaymentInfo');
    const cryptoAddress = document.getElementById('cryptoAddress');
    const cryptoAmount = document.getElementById('cryptoAmount');
    
    // Get total amount
    const totalElement = document.getElementById('total');
    const totalText = totalElement ? totalElement.textContent : 'GHS 0.00';
    const totalAmount = parseFloat(totalText.replace('GHS ', ''));
    
    // Generate mock crypto addresses and amounts
    const cryptoData = {
        btc: {
            address: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
            rate: 0.0000012 // Mock BTC rate
        },
        eth: {
            address: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            rate: 0.00018 // Mock ETH rate
        },
        usdt: {
            address: 'TQn9Y2khDD95J42FQtQTdwVVRZqjqH3qKk',
            rate: 0.15 // Mock USDT rate
        },
        ltc: {
            address: 'ltc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
            rate: 0.0085 // Mock LTC rate
        }
    };
    
    const selectedCrypto = cryptoData[cryptoType];
    if (selectedCrypto) {
        const cryptoAmountValue = totalAmount * selectedCrypto.rate;
        
        cryptoAddress.textContent = selectedCrypto.address;
        cryptoAmount.textContent = cryptoAmountValue.toFixed(8) + ' ' + cryptoType.toUpperCase();
        
        cryptoPaymentInfo.style.display = 'block';
    }
}

// Copy crypto address to clipboard
function copyCryptoAddress() {
    const cryptoAddress = document.getElementById('cryptoAddress');
    if (cryptoAddress) {
        navigator.clipboard.writeText(cryptoAddress.textContent).then(() => {
            showToast('Crypto address copied to clipboard!', 'success');
        }).catch(() => {
            showToast('Failed to copy address', 'error');
        });
    }
}

// Setup form validation
function setupFormValidation() {
    // Card number formatting
    const cardNumberField = document.getElementById('cardNumber');
    if (cardNumberField) {
        cardNumberField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            value = value.replace(/\D/g, '');
            value = value.replace(/(\d{4})/g, '$1 ').trim();
            e.target.value = value.substring(0, 19);
        });
    }
    
    // Expiry date formatting
    const expiryField = document.getElementById('expiryDate');
    if (expiryField) {
        expiryField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value.substring(0, 5);
        });
    }
    
    // CVV formatting
    const cvvField = document.getElementById('cvv');
    if (cvvField) {
        cvvField.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
        });
    }
    
    // Mobile number formatting
    const mobileNumberField = document.getElementById('mobileNumber');
    if (mobileNumberField) {
        mobileNumberField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0 && !value.startsWith('0')) {
                value = '0' + value;
            }
            e.target.value = value.substring(0, 10);
        });
    }
}

// Handle checkout form submission
async function handleCheckoutSubmission(event) {
    event.preventDefault();
    
    if (!getToken()) {
        showToast('Please login to complete checkout', 'error');
        return;
    }
    
    // Get selected payment method
    const selectedPaymentMethod = document.querySelector('input[name="paymentMethod"]:checked');
    if (!selectedPaymentMethod) {
        showToast('Please select a payment method', 'error');
        return;
    }
    
    // Validate form fields
    if (!validateCheckoutForm()) {
        return;
    }
    
    // Show loading state
    const submitBtn = document.getElementById('placeOrderBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        btnText.textContent = 'Processing Payment...';
        btnSpinner.classList.remove('d-none');
    }
    
    try {
        // Get form data
        const formData = new FormData(event.target);
        const totalAmount = parseFloat(document.getElementById('total').textContent.replace('GHS ', ''));
        
        const orderData = {
            shipping_address: `${formData.get('address')}, ${formData.get('city')} ${formData.get('postalCode')}`,
            customer_info: {
                first_name: formData.get('firstName'),
                last_name: formData.get('lastName'),
                email: formData.get('email'),
                phone: formData.get('phone')
            },
            payment_method: 'paystack',
            payment_info: {
                email: formData.get('email'),
                amount: totalAmount,
                callback_url: `${window.location.origin}/payment/callback`
            },
            order_notes: formData.get('orderNotes') || ''
        };
        
        // Create order with Paystack payment
        const response = await fetch('/api/orders/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
            const order = await response.json();
            
            // Initialize Paystack payment
            if (order.authorization_url) {
                // Redirect to Paystack payment page
                window.location.href = order.authorization_url;
            } else {
                throw new Error('Payment initialization failed');
            }
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create order');
        }
        
    } catch (error) {
        console.error('Checkout error:', error);
        showToast(error.message || 'Checkout failed. Please try again.', 'error');
        
        // Reset button state
        if (submitBtn) {
            submitBtn.disabled = false;
            btnText.textContent = 'Place Order';
            btnSpinner.classList.add('d-none');
        }
    }
}

// Validate checkout form
function validateCheckoutForm() {
    const requiredFields = ['firstName', 'lastName', 'email', 'phone', 'address', 'city', 'postalCode'];
    
    for (const field of requiredFields) {
        const element = document.getElementById(field);
        if (!element || !element.value.trim()) {
            showToast(`Please fill in ${field.replace(/([A-Z])/g, ' $1').toLowerCase()}`, 'error');
            if (element) element.focus();
            return false;
        }
    }
    
    // Validate email format
    const email = document.getElementById('email').value;
    if (!isValidEmail(email)) {
        showToast('Please enter a valid email address', 'error');
        document.getElementById('email').focus();
        return false;
    }
    
    // Validate phone number
    const phone = document.getElementById('phone').value;
    if (phone.length < 10) {
        showToast('Please enter a valid phone number', 'error');
        document.getElementById('phone').focus();
        return false;
    }
    
    // Check terms acceptance
    const termsAccepted = document.getElementById('termsAccepted');
    if (!termsAccepted || !termsAccepted.checked) {
        showToast('Please accept the terms and conditions', 'error');
        return false;
    }
    
    return true;
}

// Get payment information based on method
function getPaymentInfo(paymentMethod, formData) {
    switch (paymentMethod) {
        case 'mobile_money':
            return {
                provider: formData.get('mobileProvider'),
                mobile_number: formData.get('mobileNumber')
            };
            
        case 'paypal':
            return {
                email: formData.get('paypalEmail')
            };
            
        case 'bank_transfer':
            return {
                reference: document.getElementById('orderRef').textContent,
                receipt_file: formData.get('bankReceipt')
            };
            
        case 'card':
            return {
                card_number: formData.get('cardNumber').replace(/\s/g, ''),
                expiry_date: formData.get('expiryDate'),
                cvv: formData.get('cvv'),
                card_name: formData.get('cardName')
            };
            
        case 'crypto':
            return {
                crypto_type: formData.get('cryptoType'),
                address: document.getElementById('cryptoAddress').textContent,
                amount: document.getElementById('cryptoAmount').textContent
            };
            
        default:
            return {};
    }
}

// Validate card payment
function validateCardPayment() {
    const cardNumber = document.getElementById('cardNumber').value.replace(/\s/g, '');
    const expiryDate = document.getElementById('expiryDate').value;
    const cvv = document.getElementById('cvv').value;
    const cardName = document.getElementById('cardName').value;
    
    if (!cardNumber || cardNumber.length < 13) {
        showToast('Invalid card number', 'error');
        return false;
    }
    
    if (!expiryDate || !/^\d{2}\/\d{2}$/.test(expiryDate)) {
        showToast('Invalid expiry date (use MM/YY format)', 'error');
        return false;
    }
    
    if (!cvv || cvv.length < 3) {
        showToast('Invalid CVV', 'error');
        return false;
    }
    
    if (!cardName || cardName.trim().length === 0) {
        showToast('Please enter the name on card', 'error');
        return false;
    }
    
    return true;
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show payment processing modal
function showPaymentProcessingModal() {
    const modalElement = document.getElementById('paymentModal');
    if (modalElement) {
        try {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            
            // Update progress bar
            const progressBar = document.querySelector('#paymentModal .progress-bar');
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                if (progressBar) {
                    progressBar.style.width = progress + '%';
                }
                if (progress >= 100) {
                    clearInterval(interval);
                }
            }, 200);
        } catch (error) {
            console.error('Error showing payment modal:', error);
            // Fallback: just show the modal without Bootstrap
            modalElement.style.display = 'block';
            modalElement.classList.add('show');
        }
    }
}

// Hide payment processing modal
function hidePaymentProcessingModal() {
    const modalElement = document.getElementById('paymentModal');
    if (modalElement) {
        try {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            } else {
                // Fallback: hide manually
                modalElement.style.display = 'none';
                modalElement.classList.remove('show');
            }
        } catch (error) {
            console.error('Error hiding payment modal:', error);
            // Fallback: hide manually
            modalElement.style.display = 'none';
            modalElement.classList.remove('show');
        }
    }
}

// Simulate payment processing
async function simulatePaymentProcessing(paymentMethod) {
    const statusElement = document.getElementById('paymentStatus');
    const steps = {
        'mobile_money': [
            'Initiating mobile money payment...',
            'Sending payment request to your phone...',
            'Waiting for payment confirmation...',
            'Payment confirmed!'
        ],
        'paypal': [
            'Redirecting to PayPal...',
            'Processing PayPal payment...',
            'Verifying payment...',
            'Payment successful!'
        ],
        'bank_transfer': [
            'Processing bank transfer...',
            'Verifying payment receipt...',
            'Confirming payment...',
            'Payment confirmed!'
        ],
        'card': [
            'Processing card payment...',
            'Verifying card details...',
            'Authorizing payment...',
            'Payment authorized!'
        ],
        'crypto': [
            'Processing cryptocurrency payment...',
            'Generating payment address...',
            'Waiting for blockchain confirmation...',
            'Payment confirmed!'
        ]
    };
    
    const paymentSteps = steps[paymentMethod] || steps['card'];
    
    for (let i = 0; i < paymentSteps.length; i++) {
        if (statusElement) {
            statusElement.textContent = paymentSteps[i];
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

// Show order confirmation
function showOrderConfirmation(order) {
    // Create confirmation modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'orderConfirmationModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-check-circle me-2"></i>
                        Order Confirmed!
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="text-center mb-4">
                        <i class="fas fa-shopping-bag text-success" style="font-size: 3rem;"></i>
                        <h4 class="mt-3">Thank you for your order!</h4>
                        <p class="text-muted">Order #${order.id}</p>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Order Details</h6>
                            <p><strong>Total Amount:</strong> GHS ${order.total_amount.toFixed(2)}</p>
                            <p><strong>Status:</strong> <span class="badge bg-warning">Pending</span></p>
                            <p><strong>Order Date:</strong> ${formatDate(order.created_at)}</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Shipping Address</h6>
                            <p class="text-muted">${order.shipping_address}</p>
                        </div>
                    </div>
                    
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        You will receive an email confirmation shortly. We'll notify you when your order ships.
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Continue Shopping</button>
                    <button type="button" class="btn btn-primary" onclick="viewOrder(${order.id})">View Order</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Show modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Clean up modal after it's hidden
    modal.addEventListener('hidden.bs.modal', function() {
        modal.remove();
        // Redirect to home page
        window.location.href = '/';
    });
}

// View order details
function viewOrder(orderId) {
    window.location.href = `/orders/${orderId}`;
}

// Get authentication token
function getToken() {
    return localStorage.getItem('access_token');
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getToastIcon(type)} me-2"></i>
            <span>${message}</span>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

// Get toast icon based on type
function getToastIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-triangle';
        case 'warning': return 'exclamation-circle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-GH', {
        style: 'currency',
        currency: 'GHS'
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Add to cart function (called from product pages)
async function addToCart(productId, quantity = 1) {
    if (!getToken()) {
        showToast('Please login to add items to cart', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/cart/add/${productId}?quantity=${quantity}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            await loadCart();
            showToast('Product added to cart!', 'success');
        } else {
            const error = await response.json();
            showToast(error.detail, 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showToast('Error adding to cart', 'error');
    }
}

// Track user behavior
function trackUserBehavior(action, productId = null) {
    if (!getToken() || !productId) return;
    
    fetch('/api/analytics/track-behavior', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            action: action,
            product_id: productId,
            timestamp: new Date().toISOString()
        })
    }).catch(error => {
        console.error('Error tracking behavior:', error);
    });
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Debug function to check admin status
function debugAdminStatus() {
    const token = getToken();
    console.log('🔍 Debug Admin Status:');
    console.log('Token exists:', !!token);
    console.log('Current user:', currentUser);
    
    if (token) {
        fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(user => {
            console.log('User from API:', user);
            console.log('Is admin:', user.role === 'admin');
        })
        .catch(error => {
            console.error('Error fetching user:', error);
        });
    }
}

// Make debug function available globally
window.debugAdminStatus = debugAdminStatus;

// Handle Paystack payment callback
function handlePaystackCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const reference = urlParams.get('reference');
    const trxref = urlParams.get('trxref');
    
    if (reference || trxref) {
        const paymentRef = reference || trxref;
        
        // Show loading state
        showToast('Verifying payment...', 'info');
        
        // Verify payment with backend
        fetch(`/api/orders/verify-payment/${paymentRef}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Payment successful! Your order has been confirmed.', 'success');
                // Redirect to order confirmation page or show success message
                setTimeout(() => {
                    window.location.href = '/orders';
                }, 2000);
            } else {
                showToast('Payment verification failed. Please contact support.', 'error');
            }
        })
        .catch(error => {
            console.error('Payment verification error:', error);
            showToast('Payment verification failed. Please contact support.', 'error');
        });
    }
}

// Initialize payment callback handler on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if this is a payment callback page
    if (window.location.pathname === '/payment/callback' || 
        window.location.search.includes('reference=') || 
        window.location.search.includes('trxref=')) {
        handlePaystackCallback();
    }
}); 