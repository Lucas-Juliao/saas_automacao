/**
 * JT Sistemas - Sidebar Navigation Handler
 * Enhanced sidebar functionality with smooth animations and responsive behavior
 */

class SidebarManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.mainContent = document.getElementById('main-content');
        this.isMobile = window.innerWidth <= 768;
        this.isExpanded = false;
        this.hoverTimeout = null;
        
        this.init();
    }

    init() {
        if (!this.sidebar) return;
        
        this.setupEventListeners();
        this.setupDropdowns();
        this.updateLayout();
        this.highlightCurrentPage();
    }

    setupEventListeners() {
        // Mobile toggle button
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSidebar();
            });
        }

        // Desktop hover functionality
        if (!this.isMobile) {
            this.sidebar.addEventListener('mouseenter', () => {
                this.expandSidebar();
            });

            this.sidebar.addEventListener('mouseleave', () => {
                this.collapseSidebar();
            });
        }

        // Window resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Click outside to close (mobile)
        document.addEventListener('click', (e) => {
            if (this.isMobile && this.isExpanded) {
                if (!this.sidebar.contains(e.target) && 
                    !this.sidebarToggle.contains(e.target)) {
                    this.collapseSidebar();
                }
            }
        });

        // Prevent sidebar close when clicking inside
        this.sidebar.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        // Close sidebar fully after navigating to any route (mobile and desktop collapse)
        const navLinks = this.sidebar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Ignore clicks that only toggle submenus
                const isToggle = link.getAttribute('data-bs-toggle') === 'collapse';
                if (isToggle) return;

                // Force close sidebar completely
                this.forceCloseSidebar();
            });
        });

        // Also close when clicking any submenu item specifically
        const subLinks = this.sidebar.querySelectorAll('.collapse .nav-link');
        subLinks.forEach(sublink => {
            sublink.addEventListener('click', () => {
                this.forceCloseSidebar();
            });
        });
    }

    setupDropdowns() {
        const dropdownToggles = this.sidebar.querySelectorAll('[data-bs-toggle="collapse"]');
        
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleDropdownToggle(toggle);
            });
        });
    }

    handleDropdownToggle(toggle) {
        const targetId = toggle.getAttribute('data-bs-target');
        const target = document.querySelector(targetId);
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

        // Close other dropdowns
        const allToggles = this.sidebar.querySelectorAll('[data-bs-toggle="collapse"]');
        allToggles.forEach(otherToggle => {
            if (otherToggle !== toggle) {
                const otherTargetId = otherToggle.getAttribute('data-bs-target');
                const otherTarget = document.querySelector(otherTargetId);
                
                otherToggle.setAttribute('aria-expanded', 'false');
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

        // Ensure sidebar stays expanded while dropdown is open
        if (!isExpanded && !this.isMobile) {
            this.sidebar.classList.add('expanded');
        }
    }

    toggleSidebar() {
        if (this.isMobile) {
            this.isExpanded = !this.isExpanded;
            this.sidebar.classList.toggle('show', this.isExpanded);
            this.toggleBodyOverflow(this.isExpanded);
        }
    }

    expandSidebar() {
        if (!this.isMobile) {
            clearTimeout(this.hoverTimeout);
            this.sidebar.classList.add('expanded');
            this.isExpanded = true;
            
            // Add smooth transition
            this.sidebar.style.transition = 'width 0.3s ease';
        }
    }

    collapseSidebar() {
        if (!this.isMobile) {
            this.hoverTimeout = setTimeout(() => {
                // Don't collapse if a dropdown is open
                const openDropdown = this.sidebar.querySelector('.collapse.show');
                if (!openDropdown) {
                    this.sidebar.classList.remove('expanded');
                    this.isExpanded = false;
                }
            }, 150);
        } else {
            this.isExpanded = false;
            this.sidebar.classList.remove('show');
            this.toggleBodyOverflow(false);
        }
    }

    toggleBodyOverflow(lock) {
        document.body.style.overflow = lock ? 'hidden' : '';
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;

        if (wasMobile !== this.isMobile) {
            // Reset sidebar state when switching between mobile and desktop
            this.sidebar.classList.remove('show', 'expanded');
            this.toggleBodyOverflow(false);
            this.isExpanded = false;
            
            // Re-setup event listeners for new mode
            this.updateLayout();
        }
    }

    updateLayout() {
        if (this.isMobile) {
            this.sidebar.classList.remove('expanded');
        }
    }

    highlightCurrentPage() {
        const currentPath = window.location.pathname;
        const navLinks = this.sidebar.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            link.classList.remove('active');
            
            const href = link.getAttribute('href');
            if (href) {
                // Exact match for root path
                if (currentPath === '/' && href === '/') {
                    link.classList.add('active');
                }
                // Partial match for other paths
                else if (href !== '/' && currentPath.startsWith(href)) {
                    link.classList.add('active');
                    
                    // Expand parent dropdown if needed
                    const parentCollapse = link.closest('.collapse');
                    if (parentCollapse) {
                        parentCollapse.classList.add('show');
                        const toggleButton = this.sidebar.querySelector(`[data-bs-target="#${parentCollapse.id}"]`);
                        if (toggleButton) {
                            toggleButton.setAttribute('aria-expanded', 'true');
                        }
                    }
                }
            }
        });
    }

    // Public methods for external access
    forceExpand() {
        this.expandSidebar();
    }

    forceCollapse() {
        this.collapseSidebar();
    }

    forceCloseSidebar() {
        // Force close sidebar completely regardless of mode
        this.isExpanded = false;
        this.sidebar.classList.remove('show', 'expanded');
        this.toggleBodyOverflow(false);
        
        // Close all dropdowns
        const openDropdowns = this.sidebar.querySelectorAll('.collapse.show');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
        
        // Reset all toggle buttons
        const toggleButtons = this.sidebar.querySelectorAll('[data-bs-toggle="collapse"]');
        toggleButtons.forEach(button => {
            button.setAttribute('aria-expanded', 'false');
        });
    }

    isCurrentlyExpanded() {
        return this.isExpanded;
    }
}

// Animation helpers
class SidebarAnimations {
    static fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            element.style.opacity = Math.min(progress / duration, 1);
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }

    static slideDown(element, duration = 300) {
        element.style.height = '0px';
        element.style.overflow = 'hidden';
        element.style.display = 'block';
        
        const targetHeight = element.scrollHeight;
        let start = null;
        
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            
            const currentHeight = (progress / duration) * targetHeight;
            element.style.height = Math.min(currentHeight, targetHeight) + 'px';
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            } else {
                element.style.height = '';
                element.style.overflow = '';
            }
        }
        
        requestAnimationFrame(animate);
    }
}

// Theme management for sidebar
class SidebarTheme {
    static applyTheme(theme = 'default') {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        // Remove existing theme classes
        sidebar.classList.remove('theme-dark', 'theme-light', 'theme-blue');
        
        // Apply new theme
        switch(theme) {
            case 'dark':
                sidebar.classList.add('theme-dark');
                break;
            case 'light':
                sidebar.classList.add('theme-light');
                break;
            case 'blue':
                sidebar.classList.add('theme-blue');
                break;
            default:
                // Default theme - no additional class needed
                break;
        }
    }

    static saveThemePreference(theme) {
        localStorage.setItem('jt-sidebar-theme', theme);
    }

    static loadThemePreference() {
        return localStorage.getItem('jt-sidebar-theme') || 'default';
    }
}

// Accessibility enhancements
class SidebarAccessibility {
    static setupKeyboardNavigation(sidebar) {
        const navLinks = sidebar.querySelectorAll('.nav-link');
        
        navLinks.forEach((link, index) => {
            link.addEventListener('keydown', (e) => {
                switch(e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        this.focusNext(navLinks, index);
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        this.focusPrevious(navLinks, index);
                        break;
                    case 'Home':
                        e.preventDefault();
                        navLinks[0].focus();
                        break;
                    case 'End':
                        e.preventDefault();
                        navLinks[navLinks.length - 1].focus();
                        break;
                }
            });
        });
    }

    static focusNext(links, currentIndex) {
        const nextIndex = (currentIndex + 1) % links.length;
        links[nextIndex].focus();
    }

    static focusPrevious(links, currentIndex) {
        const prevIndex = currentIndex === 0 ? links.length - 1 : currentIndex - 1;
        links[prevIndex].focus();
    }

    static announceStateChange(isExpanded) {
        const announcement = isExpanded ? 'Menu expandido' : 'Menu recolhido';
        
        // Create temporary screen reader announcement
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        announcer.textContent = announcement;
        
        document.body.appendChild(announcer);
        
        setTimeout(() => {
            document.body.removeChild(announcer);
        }, 1000);
    }
}

// Initialize sidebar when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main sidebar manager
    const sidebarManager = new SidebarManager();
    
    // Setup accessibility features
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        SidebarAccessibility.setupKeyboardNavigation(sidebar);
    }
    
    // Load and apply saved theme
    const savedTheme = SidebarTheme.loadThemePreference();
    SidebarTheme.applyTheme(savedTheme);
    
    // Make sidebar manager available globally
    window.sidebarManager = sidebarManager;
    
    // Setup ARIA labels and roles for better accessibility
    if (sidebar) {
        sidebar.setAttribute('role', 'navigation');
        sidebar.setAttribute('aria-label', 'Menu principal');
        
        const navList = sidebar.querySelector('.sidebar-nav ul');
        if (navList) {
            navList.setAttribute('role', 'menubar');
        }
        
        const navItems = sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            if (link) {
                link.setAttribute('role', 'menuitem');
            }
        });
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SidebarManager,
        SidebarAnimations,
        SidebarTheme,
        SidebarAccessibility
    };
}

