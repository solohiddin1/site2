/**
 * API Client for Minishop
 * Handles all API requests to the Django backend
 */

const API_BASE_URL = 'http://localhost:8000/api';
const MEDIA_BASE_URL = 'http://localhost:8000/media';

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.mediaURL = MEDIA_BASE_URL;
    }

    /**
     * Generic fetch method with error handling
     */
    async fetch(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return { success: true, data };
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get full media URL
     */
    getMediaUrl(path) {
        if (!path) return '';
        if (path.startsWith('http')) return path;
        return `${this.mediaURL}/${path}`;
    }

    /**
     * Get all products
     */
    async getProducts(categoryId = null) {
        if (categoryId) {
            return this.fetch(`/products/?category=${categoryId}`);
        } else {
            // Use the all products endpoint
            return this.fetch('/products/all/');
        }
    }

    /**
     * Get single product by ID
     */
    async getProduct(productId) {
        return this.fetch(`/products/${productId}/`);
    }

    /**
     * Get product images
     */
    async getProductImages(productId) {
        return this.fetch(`/product-images/?product=${productId}`);
    }

    /**
     * Get all categories
     */
    async getCategories() {
        return this.fetch('/categories/');
    }

    /**
     * Get single category by ID
     */
    async getCategory(categoryId) {
        return this.fetch(`/categories/${categoryId}/`);
    }

    /**
     * Get company information
     */
    async getCompany() {
        return this.fetch('/companies/');
    }

    /**
     * Get partners
     */
    async getPartners() {
        return this.fetch('/partners/');
    }

    /**
     * Get certificates
     */
    async getCertificates() {
        return this.fetch('/certificates/');
    }

    /**
     * Get cities
     */
    async getCities() {
        return this.fetch('/cities/');
    }

    /**
     * Get service locations
     */
    async getServiceLocations() {
        return this.fetch('/service-locations/');
    }

    /**
     * Get service center descriptions
     */
    async getServiceCenterDescriptions() {
        return this.fetch('/service-center-descriptions/');
    }
}

// Create global API client instance
const apiClient = new APIClient();

