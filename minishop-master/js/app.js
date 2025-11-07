/**
 * Main Application JavaScript
 * Handles rendering of dynamic content from API
 */

// Language support (default to 'en')
let currentLanguage = 'en';

/**
 * Initialize the application
 */
async function initApp() {
    try {
        // Load company info for header/footer
        await loadCompanyInfo();
        
        // Load products
        await loadProducts();
        
        // Load categories for navigation
        await loadCategories();
        
        // Load partners
        await loadPartners();
        
        // Load certificates
        await loadCertificates();
        
        // Update cart UI
        cartManager.updateCartUI();
        
    } catch (error) {
        console.error('Error initializing app:', error);
        // Show user-friendly error message
        const container = document.getElementById('products-container');
        if (container) {
            container.innerHTML = '<div class="col-12 text-center py-5"><p class="text-danger">Failed to load content. Please check your API connection.</p></div>';
        }
    }
}

/**
 * Load and render company information
 */
async function loadCompanyInfo() {
    try {
        const result = await apiClient.getCompany();
        
        if (result.success && result.data && result.data.length > 0) {
            const company = result.data[0];
            
            // Handle translations - could be array or object
            let translation = null;
            if (company.translations) {
                translation = getTranslation(company.translations);
            }
            
            // Update header contact info
            const phoneElement = document.querySelector('.icon-phone2')?.nextElementSibling;
            const emailElement = document.querySelector('.icon-paper-plane')?.nextElementSibling;
            const addressElement = document.querySelector('.col-md-5.pr-4 .text');
            
            if (phoneElement && company.phone) {
                phoneElement.textContent = company.phone;
            }
            if (emailElement && company.email) {
                emailElement.textContent = company.email;
            }
            if (addressElement && translation?.address) {
                addressElement.textContent = translation.address;
            }
            
            // Update footer - find first footer widget
            const footerWidget = document.querySelector('.ftco-footer-widget');
            if (footerWidget) {
                const footerTitle = footerWidget.querySelector('h2');
                const footerText = footerWidget.querySelector('p');
                if (footerTitle && translation?.name) {
                    footerTitle.textContent = translation.name;
                }
                if (footerText && translation?.about_us) {
                    footerText.textContent = translation.about_us;
                }
            }
            
            // Update footer contact info
            const footerPhone = document.querySelector('.block-23 .icon-phone')?.nextElementSibling;
            const footerEmail = document.querySelector('.block-23 .icon-envelope')?.nextElementSibling;
            const footerAddress = document.querySelector('.block-23 .icon-map-marker')?.nextElementSibling;
            
            if (footerPhone && company.phone) {
                footerPhone.textContent = company.phone;
            }
            if (footerEmail && company.email) {
                footerEmail.textContent = company.email;
            }
            if (footerAddress && translation?.address) {
                footerAddress.textContent = translation.address;
            }
        } else if (result.success && (!result.data || result.data.length === 0)) {
            // No company data available, use defaults
            console.info('No company data available from API');
        }
    } catch (error) {
        console.warn('Failed to load company info:', error);
        // Continue without company info - use default template values
    }
}

/**
 * Load and render products
 */
async function loadProducts(categoryId = null) {
    const result = await apiClient.getProducts(categoryId);
    
    if (result.success && result.data) {
        const products = result.data;
        if (products.length > 0) {
            renderProducts(products);
        } else {
            const container = document.getElementById('products-container');
            if (container) {
                container.innerHTML = '<div class="col-12 text-center py-5"><p>No products available</p></div>';
            }
        }
    } else {
        showError('Failed to load products');
        const container = document.getElementById('products-container');
        if (container) {
            container.innerHTML = '<div class="col-12 text-center py-5"><p class="text-danger">Failed to load products. Please try again later.</p></div>';
        }
    }
}

/**
 * Render products to the page
 */
async function renderProducts(products) {
    const container = document.getElementById('products-container');
    if (!container) {
        console.error('Products container not found');
        return;
    }

    container.innerHTML = ''; // Clear existing content

    if (products.length === 0) {
        container.innerHTML = '<div class="col-12 text-center"><p>No products available</p></div>';
        return;
    }

    for (const product of products) {
        const productCard = await createProductCard(product);
        container.appendChild(productCard);
    }

    // Reinitialize animations if needed
    if (typeof AOS !== 'undefined') {
        AOS.refresh();
    }
}

/**
 * Create a product card element
 */
async function createProductCard(product) {
    // Handle translations - could be array or object
    let translation = null;
    if (product.translations) {
        translation = getTranslation(product.translations);
    }
    
    const productName = translation?.name || 'Unnamed Product';
    const productDescription = translation?.description || '';
    
    // Get product images
    const imagesResult = await apiClient.getProductImages(product.id);
    const productImages = imagesResult.success && imagesResult.data ? imagesResult.data : [];
    const mainImage = productImages.length > 0 
        ? apiClient.getMediaUrl(productImages[0].image)
        : 'images/product-1.png'; // Fallback image
    
    // Get category name
    let categoryName = 'Lifestyle';
    if (product.category) {
        const categoryResult = await apiClient.getCategory(product.category);
        if (categoryResult.success && categoryResult.data) {
            let catTranslation = null;
            if (categoryResult.data.translations) {
                catTranslation = getTranslation(categoryResult.data.translations);
            }
            categoryName = catTranslation?.name || 'Lifestyle';
        }
    }

    const col = document.createElement('div');
    col.className = 'col-sm-12 col-md-6 col-lg-3 ftco-animate d-flex';
    
    const price = parseFloat(product.price || 0);
    const hasDiscount = false; // You can add discount logic here
    const discountPrice = hasDiscount ? price * 0.8 : null;

    col.innerHTML = `
        <div class="product d-flex flex-column">
            <a href="product-single.html?id=${product.id}" class="img-prod">
                <img class="img-fluid" src="${mainImage}" alt="${productName}">
                ${hasDiscount ? '<span class="status">50% Off</span>' : ''}
                <div class="overlay"></div>
            </a>
            <div class="text py-3 pb-4 px-3">
                <div class="d-flex">
                    <div class="cat">
                        <span>${categoryName}</span>
                    </div>
                    <div class="rating">
                        <p class="text-right mb-0">
                            <a href="#"><span class="ion-ios-star-outline"></span></a>
                            <a href="#"><span class="ion-ios-star-outline"></span></a>
                            <a href="#"><span class="ion-ios-star-outline"></span></a>
                            <a href="#"><span class="ion-ios-star-outline"></span></a>
                            <a href="#"><span class="ion-ios-star-outline"></span></a>
                        </p>
                    </div>
                </div>
                <h3><a href="product-single.html?id=${product.id}">${productName}</a></h3>
                <div class="pricing">
                    ${discountPrice 
                        ? `<p class="price"><span class="mr-2 price-dc">$${price.toFixed(2)}</span><span class="price-sale">$${discountPrice.toFixed(2)}</span></p>`
                        : `<p class="price"><span>$${price.toFixed(2)}</span></p>`
                    }
                </div>
                <p class="bottom-area d-flex px-3">
                    <a href="#" class="add-to-cart text-center py-2 mr-1" data-product-id="${product.id}">
                        <span>Add to cart <i class="ion-ios-add ml-1"></i></span>
                    </a>
                    <a href="product-single.html?id=${product.id}" class="buy-now text-center py-2">
                        Buy now<span><i class="ion-ios-cart ml-1"></i></span>
                    </a>
                </p>
            </div>
        </div>
    `;

    // Add event listener for add to cart
    const addToCartBtn = col.querySelector('.add-to-cart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            cartManager.addToCart({
                id: product.id,
                name: productName,
                price: price,
                image: mainImage,
                translations: product.translations
            });
        });
    }

    return col;
}

/**
 * Load and render categories
 */
async function loadCategories() {
    const result = await apiClient.getCategories();
    
    if (result.success && result.data) {
        const categories = result.data;
        // You can render categories in navigation or dropdown
        renderCategories(categories);
    }
}

/**
 * Render categories in navigation
 */
function renderCategories(categories) {
    // Find the dropdown menu - it's a sibling of the dropdown toggle
    const dropdownToggle = document.querySelector('#dropdown04');
    if (!dropdownToggle) return;
    
    const dropdown = dropdownToggle.nextElementSibling || 
                     document.querySelector('#dropdown04 ~ .dropdown-menu') ||
                     dropdownToggle.parentElement.querySelector('.dropdown-menu');
    
    if (dropdown) {
        // Keep Shop link if it exists
        const existingLinks = dropdown.querySelectorAll('a');
        const shopLink = Array.from(existingLinks).find(link => link.href.includes('shop.html'));
        
        // Clear existing category items but keep Shop
        if (shopLink) {
            dropdown.innerHTML = '';
            const shopItem = document.createElement('a');
            shopItem.className = 'dropdown-item';
            shopItem.href = shopLink.href;
            shopItem.textContent = shopLink.textContent;
            dropdown.appendChild(shopItem);
        } else {
            dropdown.innerHTML = '';
        }

        // Add category links
        categories.forEach(category => {
            let translation = null;
            if (category.translations) {
                translation = getTranslation(category.translations);
            }
            const categoryName = translation?.name || 'Category';
            
            const link = document.createElement('a');
            link.className = 'dropdown-item';
            link.href = `shop.html?category=${category.id}`;
            link.textContent = categoryName;
            dropdown.appendChild(link);
        });
    }
}

/**
 * Load and render partners
 */
async function loadPartners() {
    const result = await apiClient.getPartners();
    
    if (result.success && result.data) {
        const partners = result.data;
        // Render partners if there's a partners section
        // renderPartners(partners);
    }
}

/**
 * Load and render certificates
 */
async function loadCertificates() {
    const result = await apiClient.getCertificates();
    
    if (result.success && result.data) {
        const certificates = result.data;
        // Render certificates if there's a certificates section
        // renderCertificates(certificates);
    }
}

/**
 * Get translation for current language
 * Handles both array and object formats from parler_rest
 */
function getTranslation(translations) {
    if (!translations) return null;
    
    // Handle object format: { "uz": {...}, "en": {...} }
    if (typeof translations === 'object' && !Array.isArray(translations)) {
        // Try current language first
        if (translations[currentLanguage]) {
            return translations[currentLanguage];
        }
        // Fallback to any available language
        const keys = Object.keys(translations);
        if (keys.length > 0) {
            return translations[keys[0]];
        }
        return null;
    }
    
    // Handle array format: [{ language_code: "uz", ... }, ...]
    if (Array.isArray(translations)) {
        if (translations.length === 0) return null;
        
        // Try to find translation for current language
        let translation = translations.find(t => t && (t.language_code === currentLanguage || t.language === currentLanguage));
        
        // Fallback to first available translation
        if (!translation && translations.length > 0) {
            translation = translations[0];
        }
        
        return translation;
    }
    
    // If translations is neither array nor object, log for debugging
    if (translations !== null && translations !== undefined) {
        console.warn('Unexpected translation format:', typeof translations, translations);
    }
    
    return null;
}

/**
 * Update element text content
 */
function updateElement(selector, text) {
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = text;
    }
}

/**
 * Show error message
 */
function showError(message) {
    console.error(message);
    // You can implement a toast notification here
}

/**
 * Set current language
 */
function setLanguage(lang) {
    currentLanguage = lang;
    // Reload data with new language
    initApp();
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

