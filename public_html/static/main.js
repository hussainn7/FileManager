// Main JavaScript file

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any components
    initializeComponents();
    
    // Add event listeners
    setupEventListeners();
});

// Initialize UI components
function initializeComponents() {
    // Add mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        const nav = document.querySelector('nav ul');
        menuToggle.addEventListener('click', () => {
            nav.classList.toggle('active');
        });
    }

    // Initialize form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
}

// Set up event listeners
function setupEventListeners() {
    // Add smooth scrolling to all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
}

// Form validation
function validateForm(e) {
    const form = e.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            showError(field, 'This field is required');
        } else {
            clearError(field);
        }
    });

    if (!isValid) {
        e.preventDefault();
    }
}

// Show error message
function showError(field, message) {
    const errorDiv = field.nextElementSibling?.classList.contains('error-message') 
        ? field.nextElementSibling 
        : document.createElement('div');
    
    if (!field.nextElementSibling?.classList.contains('error-message')) {
        errorDiv.classList.add('error-message');
        errorDiv.style.color = 'red';
        errorDiv.style.fontSize = '0.8rem';
        field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }
    
    errorDiv.textContent = message;
    field.classList.add('error');
}

// Clear error message
function clearError(field) {
    const errorDiv = field.nextElementSibling;
    if (errorDiv?.classList.contains('error-message')) {
        errorDiv.remove();
    }
    field.classList.remove('error');
}

// Utility function to format dates
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

// Utility function to handle API requests
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
} 