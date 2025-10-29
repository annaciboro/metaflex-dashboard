/* ============================================
   METAFLEX OPERATIONS SYSTEM - PREMIUM JS
   Version 5.0 - "GET A GRIP ON LIFE"
   Brand Personality: Bold, Empowering, Dynamic
   ============================================ */

(function() {
    'use strict';
    
    // Wait for DOM to be fully loaded
    function initMetaFlexSystem() {
        console.log('🚀 MetaFlex Operations System Initializing...');
        
        // ============================================
        // 1. LOGO GRIP INTERACTION
        // ============================================
        function initLogoGrip() {
            const logos = document.querySelectorAll('[data-testid="stImage"] img, .logo, [alt*="MetaFlex"], img[src*="logo"]');
            
            logos.forEach(logo => {
                if (!logo) return;
                
                logo.style.cursor = 'grab';
                logo.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                
                // Add pulse animation
                logo.style.animation = 'pulse 2s ease-in-out infinite';
                
                logo.addEventListener('mousedown', function(e) {
                    this.style.cursor = 'grabbing';
                    this.style.transform = 'rotate(15deg) scale(1.15)';
                    this.style.filter = 'drop-shadow(0 6px 20px rgba(212, 255, 0, 0.6))';
                });
                
                logo.addEventListener('mouseup', function(e) {
                    this.style.cursor = 'grab';
                    this.style.transform = 'rotate(0deg) scale(1)';
                    this.style.filter = 'drop-shadow(0 2px 8px rgba(212, 255, 0, 0.3))';
                });
                
                logo.addEventListener('mouseleave', function(e) {
                    this.style.cursor = 'grab';
                    this.style.transform = 'rotate(0deg) scale(1)';
                    this.style.filter = 'drop-shadow(0 2px 8px rgba(212, 255, 0, 0.3))';
                });
            });
            
            console.log('✅ Logo grip initialized');
        }
        
        // ============================================
        // 2. VICTORY SPARKLES ON METRIC HOVER
        // ============================================
        function initMetricSparkles() {
            const metrics = document.querySelectorAll('[data-testid="metric-container"]');
            
            metrics.forEach(metric => {
                metric.addEventListener('mouseenter', function() {
                    // Create sparkle element
                    const sparkle = document.createElement('div');
                    sparkle.innerHTML = '⚡';
                    sparkle.style.cssText = `
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        font-size: 32px;
                        animation: sparkleAnimation 0.8s ease-out;
                        pointer-events: none;
                        z-index: 10;
                    `;
                    
                    this.style.position = 'relative';
                    this.appendChild(sparkle);
                    
                    // Add grip texture on hover
                    this.classList.add('grip-texture');
                    
                    setTimeout(() => {
                        sparkle.remove();
                        this.classList.remove('grip-texture');
                    }, 800);
                });
            });
            
            console.log('✅ Metric sparkles initialized');
        }
        
        // ============================================
        // 3. ANIMATED NUMBER COUNTERS
        // ============================================
        function initNumberCounters() {
            const metrics = document.querySelectorAll('[data-testid="stMetricValue"]');
            
            metrics.forEach(metric => {
                const text = metric.textContent.trim();
                const number = parseInt(text.replace(/[^0-9]/g, ''));
                
                if (isNaN(number) || number === 0) return;
                
                // Only animate on first load
                if (metric.dataset.animated) return;
                metric.dataset.animated = 'true';
                
                let currentValue = 0;
                const increment = number / 40;
                const duration = 1500;
                const stepTime = duration / 40;
                
                metric.textContent = '0';
                
                const timer = setInterval(() => {
                    currentValue += increment;
                    if (currentValue >= number) {
                        metric.textContent = text; // Restore original text with any prefixes/suffixes
                        clearInterval(timer);
                    } else {
                        metric.textContent = Math.floor(currentValue);
                    }
                }, stepTime);
            });
            
            console.log('✅ Number counters initialized');
        }
        
        // ============================================
        // 4. MOTIVATIONAL TOOLTIPS
        // ============================================
        function initMotivationalTooltips() {
            const motivations = [
                "GET A GRIP! 💪",
                "STAY IN CONTROL 🎯",
                "DOMINATE TODAY 🔥",
                "GRIP LIFE 👊",
                "CRUSH IT! ⚡",
                "TAKE CHARGE 🚀",
                "OWN YOUR DAY 💥",
                "STAY FOCUSED 🎯"
            ];
            
            // Get all buttons, excluding navigation buttons to avoid interference
            const buttons = document.querySelectorAll('button:not([data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"]:first-child button)');
            
            buttons.forEach(btn => {
                btn.addEventListener('mouseenter', function(e) {
                    // Don't add tooltip if already exists
                    if (this.querySelector('.mf-tooltip')) return;
                    
                    const tooltip = document.createElement('div');
                    tooltip.className = 'mf-tooltip';
                    tooltip.textContent = motivations[Math.floor(Math.random() * motivations.length)];
                    tooltip.style.cssText = `
                        position: absolute;
                        bottom: calc(100% + 8px);
                        left: 50%;
                        transform: translateX(-50%) translateY(0);
                        background: #d4ff00;
                        color: #1a2424;
                        padding: 6px 14px;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 800;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        pointer-events: none;
                        white-space: nowrap;
                        z-index: 10000;
                        box-shadow: 0 4px 12px rgba(212, 255, 0, 0.4);
                        animation: tooltipSlideIn 0.3s ease-out;
                    `;
                    
                    // Arrow
                    const arrow = document.createElement('div');
                    arrow.style.cssText = `
                        position: absolute;
                        top: 100%;
                        left: 50%;
                        transform: translateX(-50%);
                        width: 0;
                        height: 0;
                        border-left: 6px solid transparent;
                        border-right: 6px solid transparent;
                        border-top: 6px solid #d4ff00;
                    `;
                    tooltip.appendChild(arrow);
                    
                    this.style.position = 'relative';
                    this.appendChild(tooltip);
                });
                
                btn.addEventListener('mouseleave', function() {
                    const tooltip = this.querySelector('.mf-tooltip');
                    if (tooltip) {
                        tooltip.style.animation = 'tooltipSlideOut 0.2s ease-in';
                        setTimeout(() => tooltip.remove(), 200);
                    }
                });
            });
            
            console.log('✅ Motivational tooltips initialized');
        }
        
        // ============================================
        // 5. CHART HOVER ENHANCEMENTS
        // ============================================
        function initChartEnhancements() {
            const charts = document.querySelectorAll('[data-testid="stPlotlyChart"]');
            
            charts.forEach(chart => {
                chart.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                
                chart.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-4px)';
                    this.style.boxShadow = '0 12px 28px rgba(15, 106, 106, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08)';
                });
                
                chart.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.05)';
                });
            });
            
            console.log('✅ Chart enhancements initialized');
        }
        
        // ============================================
        // 6. TABLE ROW HOVER EFFECTS
        // ============================================
        function initTableEffects() {
            const tables = document.querySelectorAll('.ag-row, table tbody tr');
            
            tables.forEach(row => {
                row.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.002)';
                    this.style.transition = 'all 0.2s ease';
                });
                
                row.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                });
            });
            
            console.log('✅ Table effects initialized');
        }
        
        // ============================================
        // 7. SCROLL ANIMATIONS
        // ============================================
        function initScrollAnimations() {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in-up');
                    }
                });
            }, observerOptions);
            
            // Observe sections and metric cards
            document.querySelectorAll('[data-testid="stVerticalBlock"], [data-testid="metric-container"]').forEach(element => {
                observer.observe(element);
            });
            
            console.log('✅ Scroll animations initialized');
        }
        
        // ============================================
        // 8. SUBTLE PARALLAX EFFECT
        // ============================================
        function initParallaxEffect() {
            window.addEventListener('scroll', function() {
                const scrolled = window.pageYOffset;
                const parallaxElements = document.querySelectorAll('[data-testid="metric-container"]');
                
                parallaxElements.forEach((el, index) => {
                    const speed = 0.05 + (index * 0.01);
                    el.style.transform = `translateY(${scrolled * speed}px)`;
                });
            });
            
            console.log('✅ Parallax effect initialized');
        }
        
        // ============================================
        // 9. GRIP STRENGTH PROGRESS BARS
        // ============================================
        function initGripProgress() {
            const progressBars = document.querySelectorAll('[data-testid="stProgress"], .stProgress');
            
            progressBars.forEach(bar => {
                bar.style.animation = 'gripPulse 2s ease-in-out infinite';
            });
            
            console.log('✅ Grip progress initialized');
        }
        
        // ============================================
        // 10. NAVIGATION ACTIVE STATE TRACKING
        // ============================================
        function initNavTracking() {
            const navButtons = document.querySelectorAll('[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button');
            
            navButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Remove active class from all buttons
                    navButtons.forEach(btn => btn.classList.remove('active-nav'));
                    // Add active class to clicked button
                    this.classList.add('active-nav');
                });
            });
            
            console.log('✅ Nav tracking initialized');
        }
        
        // ============================================
        // 11. INJECT CUSTOM ANIMATIONS CSS
        // ============================================
        function injectAnimations() {
            const style = document.createElement('style');
            style.textContent = `
                /* MetaFlex Animations */
                @keyframes sparkleAnimation {
                    0% {
                        opacity: 0;
                        transform: scale(0) rotate(0deg);
                    }
                    50% {
                        opacity: 1;
                        transform: scale(1.5) rotate(180deg);
                    }
                    100% {
                        opacity: 0;
                        transform: scale(0) rotate(360deg);
                    }
                }
                
                @keyframes tooltipSlideIn {
                    from {
                        opacity: 0;
                        transform: translateX(-50%) translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(-50%) translateY(0);
                    }
                }
                
                @keyframes tooltipSlideOut {
                    from {
                        opacity: 1;
                        transform: translateX(-50%) translateY(0);
                    }
                    to {
                        opacity: 0;
                        transform: translateX(-50%) translateY(10px);
                    }
                }
                
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }
                
                @keyframes gripPulse {
                    0%, 100% {
                        box-shadow: 0 0 10px rgba(212, 255, 0, 0.3);
                    }
                    50% {
                        box-shadow: 0 0 20px rgba(212, 255, 0, 0.6);
                    }
                }
                
                .fade-in-up {
                    animation: fadeInUp 0.6s ease-out;
                }
                
                .active-nav {
                    background: #d4ff00 !important;
                    color: #1a2424 !important;
                    font-weight: 800 !important;
                    box-shadow: 0 4px 16px rgba(212, 255, 0, 0.3), 0 0 30px rgba(212, 255, 0, 0.3) !important;
                }
                
                .grip-texture::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-image: 
                        repeating-linear-gradient(
                            45deg,
                            transparent,
                            transparent 2px,
                            rgba(212, 255, 0, 0.03) 2px,
                            rgba(212, 255, 0, 0.03) 4px
                        );
                    pointer-events: none;
                    border-radius: inherit;
                }
            `;
            document.head.appendChild(style);
            
            console.log('✅ Animations injected');
        }
        
        // ============================================
        // 12. HANDLE STREAMLIT RERUNS
        // ============================================
        function handleStreamlitReruns() {
            // Observe DOM changes to reinitialize effects after Streamlit reruns
            const streamlitObserver = new MutationObserver(function(mutations) {
                // Debounce to avoid too many reinitializations
                clearTimeout(window.metaflexReinitTimer);
                window.metaflexReinitTimer = setTimeout(() => {
                    console.log('🔄 Reinitializing MetaFlex after Streamlit rerun...');
                    initMetricSparkles();
                    initChartEnhancements();
                    initTableEffects();
                    initMotivationalTooltips();
                    initLogoGrip();
                }, 500);
            });
            
            streamlitObserver.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            console.log('✅ Streamlit rerun handler initialized');
        }
        
        // ============================================
        // 13. PERFORMANCE METRICS LOGGER
        // ============================================
        function logPerformanceMetrics() {
            if (window.performance && window.performance.timing) {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                console.log(`⚡ MetaFlex loaded in ${pageLoadTime}ms`);
            }
        }
        
        // ============================================
        // MASTER INITIALIZATION
        // ============================================
        function init() {
            console.log('═══════════════════════════════════════');
            console.log('   METAFLEX OPERATIONS SYSTEM v5.0    ');
            console.log('        "GET A GRIP ON LIFE"          ');
            console.log('═══════════════════════════════════════');
            
            // Inject animations first
            injectAnimations();
            
            // Initialize all features
            initLogoGrip();
            initMetricSparkles();
            initNumberCounters();
            initMotivationalTooltips();
            initChartEnhancements();
            initTableEffects();
            initScrollAnimations();
            // initParallaxEffect(); // Commented out - can be too much
            initGripProgress();
            initNavTracking();
            handleStreamlitReruns();
            
            // Log performance
            logPerformanceMetrics();
            
            console.log('═══════════════════════════════════════');
            console.log('✅ All MetaFlex systems operational!');
            console.log('═══════════════════════════════════════');
        }
        
        // Run initialization
        init();
    }
    
    // Wait for window load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMetaFlexSystem);
    } else {
        initMetaFlexSystem();
    }
    
})();

// Export for debugging
window.MetaFlexSystem = {
    version: '5.0',
    brand: 'GET A GRIP ON LIFE',
    initialized: true
};