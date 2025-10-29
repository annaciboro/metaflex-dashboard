/**
 * MetaFlex Navigation Header - Dynamic JavaScript
 * Automatically detects current page and applies active styling
 * Place this in your metaflex_nav folder and load via st.components.v1.html()
 */

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        navItems: [
            { id: 'home', label: 'Home', page: 'Home' },
            { id: 'my_tasks', label: 'My Tasks', page: 'My Tasks' },
            { id: 'team_tasks', label: 'Team Tasks', page: 'Team Tasks' },
            { id: 'archive', label: 'Archive', page: 'Archive' },
            { id: 'sales_portal', label: 'Sales Portal', page: 'Sales Portal' },
            { id: 'investor_portal', label: 'Investor Portal', page: 'Investor Portal' }
        ],
        logoText: 'X',
        userBadgeText: 'Téa',
        logoutText: 'Logout'
    };

    /**
     * Get current page from Streamlit's session state
     * This works by checking the URL or page title
     */
    function getCurrentPage() {
        // Try to get page from URL parameters first
        const urlParams = new URLSearchParams(window.location.search);
        const pageParam = urlParams.get('page');
        if (pageParam) return pageParam;

        // Try to get from document title
        const title = document.title;
        for (const item of CONFIG.navItems) {
            if (title.includes(item.page)) {
                return item.page;
            }
        }

        // Default to Home
        return 'Home';
    }

    /**
     * Create the navigation HTML structure
     */
    function createNavHTML() {
        const currentPage = getCurrentPage();
        
        let navItemsHTML = '';
        for (const item of CONFIG.navItems) {
            const isActive = item.page === currentPage;
            const activeClass = isActive ? ' active' : '';
            navItemsHTML += `
                <button class="nav-button${activeClass}" 
                        data-page="${item.page}" 
                        onclick="navigateToPage('${item.page}')">
                    ${item.label}
                </button>
            `;
        }

        return `
            <div class="nav-container">
                <div class="logo-section">
                    <div class="logo">${CONFIG.logoText}</div>
                </div>
                
                <div class="nav-items">
                    ${navItemsHTML}
                </div>
                
                <div class="user-section">
                    <div class="user-badge">${CONFIG.userBadgeText}</div>
                    <button class="logout-button" onclick="handleLogout()">
                        ${CONFIG.logoutText}
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Handle page navigation
     */
    window.navigateToPage = function(page) {
        // Send message to Streamlit
        if (window.parent) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: page
            }, '*');
        }
        
        // Update active state
        updateActiveButton(page);
    };

    /**
     * Handle logout
     */
    window.handleLogout = function() {
        if (window.parent) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'LOGOUT'
            }, '*');
        }
    };

    /**
     * Update which button appears active
     */
    function updateActiveButton(page) {
        const buttons = document.querySelectorAll('.nav-button');
        buttons.forEach(button => {
            if (button.dataset.page === page) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }

    /**
     * Initialize navigation
     */
    function initNav() {
        // Create nav element
        const navElement = document.createElement('div');
        navElement.innerHTML = createNavHTML();
        
        // Insert at top of body
        if (document.body.firstChild) {
            document.body.insertBefore(navElement, document.body.firstChild);
        } else {
            document.body.appendChild(navElement);
        }

        // Add padding to body to account for fixed nav
        document.body.style.paddingTop = '68px';
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNav);
    } else {
        initNav();
    }

})();