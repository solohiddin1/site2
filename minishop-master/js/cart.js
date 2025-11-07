/**
 * Cart Management System
 * Uses localStorage to persist cart data
 */

class CartManager {
    constructor() {
        this.storageKey = 'minishop_cart';
        this.cart = this.loadCart();
    }

    /**
     * Load cart from localStorage
     */
    loadCart() {
        try {
            const cartData = localStorage.getItem(this.storageKey);
            return cartData ? JSON.parse(cartData) : [];
        } catch (error) {
            console.error('Error loading cart:', error);
            return [];
        }
    }

    /**
     * Save cart to localStorage
     */
    saveCart() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.cart));
            this.updateCartUI();
        } catch (error) {
            console.error('Error saving cart:', error);
        }
    }

    /**
     * Add product to cart
     */
    addToCart(product, quantity = 1) {
        const existingItem = this.cart.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.cart.push({
                id: product.id,
                name: this.getProductName(product),
                price: parseFloat(product.price),
                image: this.getProductImage(product),
                quantity: quantity
            });
        }
        
        this.saveCart();
        this.showNotification('Product added to cart!');
    }

    /**
     * Remove product from cart
     */
    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
    }

    /**
     * Update product quantity in cart
     */
    updateQuantity(productId, quantity) {
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeFromCart(productId);
            } else {
                item.quantity = quantity;
                this.saveCart();
            }
        }
    }

    /**
     * Get cart total items count
     */
    getTotalItems() {
        return this.cart.reduce((total, item) => total + item.quantity, 0);
    }

    /**
     * Get cart total price
     */
    getTotalPrice() {
        return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    /**
     * Clear cart
     */
    clearCart() {
        this.cart = [];
        this.saveCart();
    }

    /**
     * Get all cart items
     */
    getCartItems() {
        return this.cart;
    }

    /**
     * Check if product is in cart
     */
    isInCart(productId) {
        return this.cart.some(item => item.id === productId);
    }

    /**
     * Get product name (handles translations)
     */
    getProductName(product) {
        if (product.translations && product.translations.length > 0) {
            // Try to get current language or default to first translation
            const currentLang = this.getCurrentLanguage();
            const translation = product.translations.find(t => t.language_code === currentLang) 
                || product.translations[0];
            return translation.name || 'Unnamed Product';
        }
        return product.name || 'Unnamed Product';
    }

    /**
     * Get product image URL
     */
    getProductImage(product) {
        // This will be populated when we fetch product images
        return product.image || '';
    }

    /**
     * Get current language (default to 'en')
     */
    getCurrentLanguage() {
        // You can implement language detection here
        return 'en';
    }

    /**
     * Update cart UI (cart icon count)
     */
    updateCartUI() {
        const cartCount = this.getTotalItems();
        const cartElements = document.querySelectorAll('.cart-count, .icon-shopping_cart + [data-count]');
        cartElements.forEach(el => {
            if (el.classList.contains('cart-count')) {
                el.textContent = `[${cartCount}]`;
            } else {
                el.textContent = cartCount;
            }
        });

        // Update cart badge in navbar
        const cartBadge = document.querySelector('.cta-colored .nav-link');
        if (cartBadge) {
            const countSpan = cartBadge.querySelector('span:not(.icon-shopping_cart)') || 
                            cartBadge.querySelector('[data-count]');
            if (countSpan) {
                countSpan.textContent = `[${cartCount}]`;
            } else {
                // Add count if it doesn't exist
                const countEl = document.createElement('span');
                countEl.textContent = `[${cartCount}]`;
                countEl.className = 'cart-count';
                cartBadge.appendChild(countEl);
            }
        }
    }

    /**
     * Show notification
     */
    showNotification(message) {
        // Simple notification - you can enhance this with a toast library
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 10000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
}

// Create global cart manager instance
const cartManager = new CartManager();

// Initialize cart UI on page load
document.addEventListener('DOMContentLoaded', () => {
    cartManager.updateCartUI();
});

