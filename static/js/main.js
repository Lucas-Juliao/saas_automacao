/**
 * JT Sistemas - Main JavaScript File
 * Handles sidebar navigation, UI interactions, and common functionality
 */

class JTSistemas {
    constructor() {
        this.init();
    }

    init() {
        this.setupSidebar();
        this.setupAlerts();
        this.setupFormValidation();
        this.setupTooltips();
        this.setupModals();
        this.setupDateInputs();
        this.highlightActiveNavItem();
        this.enforceUppercaseInputs();
    }

    /**
     * Setup sidebar functionality
     */
    setupSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const mainContent = document.getElementById('main-content');

        if (!sidebar || !sidebarToggle) return;

        // Mobile sidebar toggle
        sidebarToggle.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('show');
                this.toggleBodyOverflow();
            }
        });

        // Close sidebar on mobile when clicking outside
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                    this.toggleBodyOverflow(false);
                }
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('show');
                this.toggleBodyOverflow(false);
            }
        });

        // Smooth hover effects for desktop
        if (window.innerWidth > 768) {
            let hoverTimeout;

            sidebar.addEventListener('mouseenter', () => {
                clearTimeout(hoverTimeout);
                sidebar.classList.add('expanded');
            });

            sidebar.addEventListener('mouseleave', () => {
                hoverTimeout = setTimeout(() => {
                    sidebar.classList.remove('expanded');
                }, 150);
            });
        }

        // Handle dropdown menus in sidebar
        const dropdownToggles = sidebar.querySelectorAll('[data-bs-toggle="collapse"]');
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(toggle.dataset.bsTarget);
                const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
                
                // Close other dropdowns
                dropdownToggles.forEach(otherToggle => {
                    if (otherToggle !== toggle) {
                        otherToggle.setAttribute('aria-expanded', 'false');
                        const otherTarget = document.querySelector(otherToggle.dataset.bsTarget);
                        if (otherTarget) {
                            otherTarget.classList.remove('show');
                        }
                    }
                });

                // Toggle current dropdown
                toggle.setAttribute('aria-expanded', !isExpanded);
                if (target) {
                    target.classList.toggle('show');
                }
            });
        });
    }

    /**
     * Toggle body overflow for mobile sidebar
     */
    toggleBodyOverflow(force = null) {
        if (force !== null) {
            document.body.style.overflow = force ? 'hidden' : '';
        } else {
            const sidebar = document.getElementById('sidebar');
            document.body.style.overflow = sidebar.classList.contains('show') ? 'hidden' : '';
        }
    }

    /**
     * Setup alert auto-dismiss functionality
     */
    setupAlerts() {
        const alerts = document.querySelectorAll('.alert');
        
        alerts.forEach(alert => {
            // Auto-dismiss success and info alerts after 5 seconds
            if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                setTimeout(() => {
                    this.dismissAlert(alert);
                }, 5000);
            }

            // Add click handler for manual dismiss
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.dismissAlert(alert);
                });
            }
        });
    }

    /**
     * Dismiss alert with animation
     */
    dismissAlert(alert) {
        alert.style.transition = 'all 0.3s ease';
        alert.style.transform = 'translateX(100%)';
        alert.style.opacity = '0';
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    }

    /**
     * Setup form validation and enhancement
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Add loading state to submit buttons
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="spinner"></span> Processando...';
                    
                    // Re-enable button after 5 seconds as failsafe
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }, 5000);
                }
            });

            // Real-time validation feedback
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });

                input.addEventListener('input', () => {
                    // Clear previous validation states on input
                    input.classList.remove('is-valid', 'is-invalid');
                    const feedback = input.parentNode.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.style.display = 'none';
                    }
                });
            });
        });
    }

    /**
     * Validate individual form field
     */
    validateField(field) {
        let isValid = true;
        let message = '';

        // Required field validation
        if (field.hasAttribute('required') && !field.value.trim()) {
            isValid = false;
            message = 'Este campo é obrigatório.';
        }

        // Email validation
        if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                isValid = false;
                message = 'Por favor, insira um email válido.';
            }
        }

        // Password confirmation
        if (field.name === 'password2') {
            const passwordField = document.querySelector('input[name="password"]');
            if (passwordField && field.value !== passwordField.value) {
                isValid = false;
                message = 'As senhas não coincidem.';
            }
        }

        // Apply validation classes
        field.classList.toggle('is-valid', isValid && field.value.trim());
        field.classList.toggle('is-invalid', !isValid);

        // Show/hide feedback
        let feedback = field.parentNode.querySelector('.invalid-feedback');
        if (!feedback && !isValid) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }

        if (feedback) {
            feedback.textContent = message;
            feedback.style.display = isValid ? 'none' : 'block';
        }
    }

    /**
     * Setup tooltips
     */
    setupTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    /**
     * Setup modal enhancements
     */
    setupModals() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                // Focus first input when modal opens
                const firstInput = modal.querySelector('input, select, textarea');
                if (firstInput) {
                    firstInput.focus();
                }
            });

            modal.addEventListener('hidden.bs.modal', () => {
                // Reset form when modal closes
                const form = modal.querySelector('form');
                if (form) {
                    form.reset();
                    // Clear validation states
                    form.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
                        field.classList.remove('is-valid', 'is-invalid');
                    });
                    form.querySelectorAll('.invalid-feedback').forEach(feedback => {
                        feedback.style.display = 'none';
                    });
                }
            });
        });
    }

    /**
     * Setup date inputs with proper formatting
     */
    setupDateInputs() {
        const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
        
        dateInputs.forEach(input => {
            // Set minimum date to current date/time
            if (!input.hasAttribute('min')) {
                const now = new Date();
                now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
                input.min = now.toISOString().slice(0, 16);
            }
        });
    }

    /**
     * Highlight active navigation item
     */
    highlightActiveNavItem() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && (currentPath === href || (href !== '/' && currentPath.startsWith(href)))) {
                link.classList.add('active');
                
                // Expand parent dropdown if needed
                const parentCollapse = link.closest('.collapse');
                if (parentCollapse) {
                    parentCollapse.classList.add('show');
                    const toggle = document.querySelector(`[data-bs-target="#${parentCollapse.id}"]`);
                    if (toggle) {
                        toggle.setAttribute('aria-expanded', 'true');
                    }
                }
            }
        });
    }

    /**
     * Show success notification
     */
    showNotification(message, type = 'success') {
        const alertContainer = document.querySelector('.alert-container') || this.createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto dismiss
        setTimeout(() => {
            this.dismissAlert(alert);
        }, 5000);
    }

    /**
     * Create alert container if it doesn't exist
     */
    createAlertContainer() {
        const container = document.createElement('div');
        container.className = 'alert-container';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Format currency values
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    /**
     * Format date values
     */
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return new Intl.DateTimeFormat('pt-BR', { ...defaultOptions, ...options }).format(new Date(date));
    }

    /**
     * Confirm action with custom message
     */
    confirmAction(message = 'Tem certeza que deseja realizar esta ação?') {
        return confirm(message);
    }

    /**
     * Enforce uppercase on all text inputs and textareas across the app
     */
    enforceUppercaseInputs() {
        // Skip on login page
        if (document.getElementById('login-form')) {
            return;
        }
        const selector = 'input[type="text"], input:not([type]), textarea';
        const fields = document.querySelectorAll(selector);
        const toUpper = (el) => {
            if (!el || el.readOnly || el.disabled) return;
            const start = el.selectionStart;
            const end = el.selectionEnd;
            el.value = el.value.toUpperCase();
            if (typeof start === 'number' && typeof end === 'number') {
                el.setSelectionRange(start, end);
            }
        };
        fields.forEach(el => {
            // Initial transform
            toUpper(el);
            // On input
            el.addEventListener('input', () => toUpper(el));
            // On change/paste
            el.addEventListener('change', () => toUpper(el));
        });
        // Observe dynamic elements
        const observer = new MutationObserver(() => {
            document.querySelectorAll(selector).forEach(el => {
                if (!el._upperBound) {
                    el._upperBound = true;
                    toUpper(el);
                    el.addEventListener('input', () => toUpper(el));
                    el.addEventListener('change', () => toUpper(el));
                }
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Texto copiado para a área de transferência!', 'info');
        } catch (err) {
            console.error('Erro ao copiar texto:', err);
            this.showNotification('Erro ao copiar texto.', 'danger');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.JTSistemas = new JTSistemas();
});

// Utility functions for global access
window.showNotification = (message, type) => {
    if (window.JTSistemas) {
        window.JTSistemas.showNotification(message, type);
    }
};

window.confirmAction = (message) => {
    if (window.JTSistemas) {
        return window.JTSistemas.confirmAction(message);
    }
    return confirm(message);
};

