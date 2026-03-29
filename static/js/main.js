/**
 * Wholesale - Main JavaScript
 */

// CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Toast Notification System
function showToast(message, type = 'info') {
    // Create toast container if not exists
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        container.style.marginTop = '70px';
        document.body.appendChild(container);
    }

    // Create toast element
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' :
                    type === 'danger' ? 'bg-danger' :
                    type === 'warning' ? 'bg-warning' : 'bg-primary';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${type === 'success' ? '<i class="bi bi-check-circle me-2"></i>' : ''}
                    ${type === 'danger' ? '<i class="bi bi-exclamation-circle me-2"></i>' : ''}
                    ${type === 'warning' ? '<i class="bi bi-exclamation-triangle me-2"></i>' : ''}
                    ${type === 'info' ? '<i class="bi bi-info-circle me-2"></i>' : ''}
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    toast.show();

    // Remove toast element after hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Add to Cart
function addToCart(productId, quantity = 1) {
    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `product_id=${productId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (data.message.includes('Tizimga kiring')) {
                showToast('Savatchaga qo\'shish uchun tizimga kiring', 'warning');
                setTimeout(() => {
                    window.location.href = '/login/?next=' + window.location.pathname;
                }, 1500);
            } else {
                showToast(data.message, 'danger');
            }
        } else {
            showToast(data.message, 'success');
            updateCartBadge();
        }
    })
    .catch(error => {
        showToast('Xatolik yuz berdi', 'danger');
        console.error('Error:', error);
    });
}

// Update Cart Badge
function updateCartBadge() {
    fetch('/cart/', {
        headers: {
            'Accept': 'text/html'
        }
    })
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newBadge = doc.querySelector('#cart-badge');
        const currentBadge = document.querySelector('#cart-badge');

        if (newBadge && currentBadge) {
            currentBadge.textContent = newBadge.textContent;
            currentBadge.classList.add('pulse');
            setTimeout(() => currentBadge.classList.remove('pulse'), 500);
        } else if (newBadge) {
            const cartLink = document.querySelector('a[href="/cart/"]');
            if (cartLink) {
                const badge = document.createElement('span');
                badge.id = 'cart-badge';
                badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger pulse';
                badge.textContent = newBadge.textContent;
                cartLink.classList.add('position-relative');
                cartLink.appendChild(badge);
            }
        }
    })
    .catch(error => console.error('Error updating cart badge:', error));
}

// Add to Wishlist
function addToWishlist(productId) {
    fetch('/account/wishlist/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `product_id=${productId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (data.message.includes('Tizimga kiring')) {
                showToast('Sevimlilarga qo\'shish uchun tizimga kiring', 'warning');
                setTimeout(() => {
                    window.location.href = '/login/?next=' + window.location.pathname;
                }, 1500);
            } else {
                showToast(data.message, 'danger');
            }
        } else {
            showToast(data.message, 'success');
            // Update heart icon
            const btn = document.querySelector(`.wishlist-btn[data-product-id="${productId}"]`);
            if (btn) {
                btn.querySelector('i').classList.remove('bi-heart');
                btn.querySelector('i').classList.add('bi-heart-fill');
            }
        }
    })
    .catch(error => {
        showToast('Xatolik yuz berdi', 'danger');
        console.error('Error:', error);
    });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', function() {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productId = this.dataset.productId;
            addToCart(productId);
        });
    });

    // Wishlist buttons
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productId = this.dataset.productId;
            addToWishlist(productId);
        });
    });

    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Search input debounce
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        const debouncedSearch = debounce(function(value) {
            if (value.length >= 2 || value.length === 0) {
                searchInput.form.submit();
            }
        }, 500);

        // Optional: Enable live search
        // searchInput.addEventListener('input', function() {
        //     debouncedSearch(this.value);
        // });
    }

    // Smooth scroll to top
    const scrollTopBtn = document.querySelector('.scroll-top-btn');
    if (scrollTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollTopBtn.classList.remove('d-none');
            } else {
                scrollTopBtn.classList.add('d-none');
            }
        });

        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Lazy load images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Tooltips initialization
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Price formatting
    document.querySelectorAll('.price-format').forEach(el => {
        const value = parseFloat(el.textContent);
        if (!isNaN(value)) {
            el.textContent = new Intl.NumberFormat('uz-UZ').format(value) + ' so\'m';
        }
    });
});

// Quantity input handlers
function incrementQuantity() {
    const input = document.getElementById('quantity');
    if (input) {
        const max = parseInt(input.max) || 999;
        if (parseInt(input.value) < max) {
            input.value = parseInt(input.value) + 1;
        }
    }
}

function decrementQuantity() {
    const input = document.getElementById('quantity');
    if (input && parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
    }
}

// Format number as price
function formatPrice(number) {
    return new Intl.NumberFormat('uz-UZ').format(number) + ' so\'m';
}

// Loading state helper
function setLoading(element, loading = true) {
    if (loading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Export functions for global access
window.getCookie = getCookie;
window.showToast = showToast;
window.addToCart = addToCart;
window.addToWishlist = addToWishlist;
window.updateCartBadge = updateCartBadge;
window.incrementQuantity = incrementQuantity;
window.decrementQuantity = decrementQuantity;
window.formatPrice = formatPrice;
window.setLoading = setLoading;
