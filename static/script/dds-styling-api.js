/**
 * 🎨 DDS STYLING API INTEGRATION
 * Using Flask proxy endpoint to prevent hanging (external API disabled)
 */

class DDSStylingAPI {
    constructor() {
        this.apiEndpoint = '/api/styling/proxy'; // Use Flask proxy - external API disabled
        this.fallbackColors = {
            // Primary colors (matching API structure)
            'primary-color': '#fff',
            'secondary-color': '#17a2b8',
            'background-color': '#f8f9fa',
            'button-color': '#006039',
            'text-color': '#212529',
            'header-color': '#003366',
            'footer-color': '#003366',
            'button-text-color': '#ffffff',
            
            // Button colors
            'submit-button-bg-color': '#28a745',
            'submit-button-text-color': '#ffffff',
            'primary-button-bg-color': '#007bff',
            'primary-button-text-color': '#ffffff',
            'secondary-button-bg-color': '#6c757d',
            'secondary-button-text-color': '#ffffff',
            
            // Layout colors
            'drawer-background-color': '#f8f9fa',
            'drawer-text-color': '#212529',
            'icon-color': '#6c757d',
            'top-color': '#006039',
            
            // Input colors
            'input-background': '#ffffff',
            'input-border': '#ced4da',
            'input-focus': '#80bdff',
            'input-text': '#495057',
            
            // Navigation colors
            'nav-background': '#003366',
            'nav-text': '#ffffff',
            
            // State colors
            'state-work': '#006039',
            'state-idle': '#6c757d',
            'state-break': '#ffc107'
        };
        this.isLoaded = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        // Initialize immediately
        this.init();
    }

    /**
     * Initialize the styling system
     */
    async init() {
        try {
            console.log('🎨 Initializing DDS Styling API...');
            await this.loadStyling();
            this.setupRetryMechanism();
            console.log('✅ DDS Styling API initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize DDS Styling API:', error);
            this.applyFallbackStyling();
        }
    }

    /**
     * Fetch styling data from DDS API
     */
    async fetchStylingData() {
        const response = await fetch(this.apiEndpoint, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            cache: 'no-cache'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('📡 Received styling data from API:', data);
        return data;
    }

    /**
     * Map API response to CSS variables
     */
    mapApiDataToCSSVariables(apiData) {
        const cssVariables = {};

        // Direct mapping from API response structure
        // Map all color properties directly from API response
        const colorMapping = {
            // Primary colors
            'primary-color': 'primary_color',
            'secondary-color': 'secondary_color',
            'background-color': 'background_color',
            'button-color': 'button_color',
            'text-color': 'text_color',
            'header-color': 'header_color',
            'footer-color': 'footer_color',
            'button-text-color': 'button_text_color',
            
            // Button colors
            'submit-button-bg-color': 'submit_button_bg_color',
            'submit-button-text-color': 'submit_button_text_color',
            'primary-button-bg-color': 'primary_button_bg_color',
            'primary-button-text-color': 'primary_button_text_color',
            'secondary-button-bg-color': 'secondary_button_bg_color',
            'secondary-button-text-color': 'secondary_button_text_color',
            
            // Layout colors
            'drawer-background-color': 'drawer_background_color',
            'drawer-text-color': 'drawer_text_color',
            'icon-color': 'icon_color',
            'top-color': 'top_color',
            
            // Primary variants
            'primary-dark': 'primary_dark',
            'primary-darker': 'primary_darker',
            'primary-light': 'primary_light',
            'primary-hover': 'primary_hover',
            'primary-active': 'primary_active',
            
            // Secondary variants
            'secondary-dark': 'secondary_dark',
            'secondary-light': 'secondary_light',
            
            // State colors
            'success-color': 'success_color',
            'warning-color': 'warning_color',
            'danger-color': 'danger_color',
            'danger-dark': 'danger_dark',
            'info-color': 'info_color',
            
            // Text colors
            'text-light': 'text_light',
            'text-dark': 'text_dark',
            
            // Background colors
            'background-light': 'background_light',
            'background-dark': 'background_dark',
            'border-color': 'border_color',
            
            // Button states
            'button-hover': 'button_hover',
            'button-dark': 'button_dark',
            'button-light': 'button_light',
            
            // Application states
            'state-idle': 'state_idle',
            'state-work': 'state_work',
            'state-break': 'state_break',
            'state-meeting': 'state_meeting',
            
            // Drawer UI
            'drawer-overlay': 'drawer_overlay',
            'drawer-border': 'drawer_border',
            'drawer-shadow': 'drawer_shadow',
            
            // Modal colors
            'modal-background': 'modal_background',
            'modal-overlay': 'modal_overlay',
            'modal-border': 'modal_border',
            
            // Input colors
            'input-background': 'input_background',
            'input-border': 'input_border',
            'input-focus': 'input_focus',
            'input-text': 'input_text',
            
            // Navigation colors
            'nav-background': 'nav_background',
            'nav-text': 'nav_text',
            'nav-hover': 'nav_hover',
            'nav-active': 'nav_active',
            
            // Standard colors
            'white': 'white',
            'black': 'black',
            
            // Gray scale
            'gray-100': 'gray_100',
            'gray-200': 'gray_200',
            'gray-300': 'gray_300',
            'gray-400': 'gray_400',
            'gray-500': 'gray_500',
            'gray-600': 'gray_600',
            'gray-700': 'gray_700',
            'gray-800': 'gray_800',
            'gray-900': 'gray_900'
        };

        // Map all colors from API response
        Object.entries(colorMapping).forEach(([cssVar, apiKey]) => {
            if (apiData[apiKey]) {
                cssVariables[cssVar] = apiData[apiKey];
            }
        });

        // Typography settings
        if (apiData.heading_font_size) cssVariables['heading-font-size'] = apiData.heading_font_size;
        if (apiData.body_font_size) cssVariables['body-font-size'] = apiData.body_font_size;
        if (apiData.font_family) cssVariables['font-family'] = `"${apiData.font_family}", sans-serif`;
        if (apiData.border_radius) cssVariables['border-radius'] = apiData.border_radius;

        console.log('🎨 Mapped CSS variables:', cssVariables);
        return cssVariables;
    }

    /**
     * Apply CSS variables to the document
     */
    applyCSSVariables(variables) {
        const root = document.documentElement;
        
        Object.entries(variables).forEach(([property, value]) => {
            if (value && value !== '') {
                root.style.setProperty(`--${property}`, value);
                console.log(`✅ Applied --${property}: ${value}`);
            }
        });

        // Add visual indicator that API styling is active
        this.addAPIIndicator();
    }

    /**
     * Apply fallback styling if API fails
     */
    applyFallbackStyling() {
        console.log('🔄 Applying fallback styling...');
        this.applyCSSVariables(this.fallbackColors);
        this.addFallbackIndicator();
    }

    /**
     * Load styling from API with error handling
     */
    async loadStyling() {
        try {
            const apiData = await this.fetchStylingData();
            const cssVariables = this.mapApiDataToCSSVariables(apiData);
            
            // Apply variables with fallbacks
            const finalVariables = { ...this.fallbackColors, ...cssVariables };
            this.applyCSSVariables(finalVariables);
            
            this.isLoaded = true;
            this.retryCount = 0;
            
        } catch (error) {
            console.error('❌ Error loading styling from API:', error);
            this.retryCount++;
            
            if (this.retryCount <= this.maxRetries) {
                console.log(`🔄 Retrying API call (${this.retryCount}/${this.maxRetries})...`);
                setTimeout(() => this.loadStyling(), 2000 * this.retryCount);
            } else {
                console.log('❌ Max retries reached, using fallback styling');
                this.applyFallbackStyling();
            }
        }
    }

    /**
     * Setup automatic retry mechanism
     */
    setupRetryMechanism() {
        // Retry every 5 minutes if not loaded
        setInterval(() => {
            if (!this.isLoaded) {
                console.log('🔄 Periodic retry attempt...');
                this.loadStyling();
            }
        }, 300000); // 5 minutes
    }

    /**
     * Add visual indicator for API styling
     */
    addAPIIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'api-styling-indicator';
        indicator.innerHTML = '🎨 DDS API';
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: var(--submit-button-bg-color);
            color: var(--submit-button-text-color);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10px;
            z-index: 9999;
            opacity: 0.7;
            pointer-events: none;
        `;
        document.body.appendChild(indicator);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.style.opacity = '0';
                setTimeout(() => indicator.remove(), 500);
            }
        }, 3000);
    }

    /**
     * Add fallback indicator
     */
    addFallbackIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'fallback-styling-indicator';
        indicator.innerHTML = '⚠️ Fallback';
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #ffc107;
            color: #000;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10px;
            z-index: 9999;
            opacity: 0.8;
            pointer-events: none;
        `;
        document.body.appendChild(indicator);
    }

    /**
     * Force refresh styling from API
     */
    async refresh() {
        console.log('🔄 Force refreshing styling from API...');
        this.isLoaded = false;
        this.retryCount = 0;
        await this.loadStyling();
    }

    /**
     * Get current styling status
     */
    getStatus() {
        return {
            isLoaded: this.isLoaded,
            retryCount: this.retryCount,
            apiEndpoint: this.apiEndpoint
        };
    }
}

// Global instance
window.ddsStyling = new DDSStylingAPI();

// Debug helper
window.refreshStyling = () => window.ddsStyling.refresh();
window.getStylingStatus = () => window.ddsStyling.getStatus();

// Auto-initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🎨 DOM loaded, DDS Styling API already initialized');
    });
} else {
    console.log('🎨 DOM already loaded, DDS Styling API initialized');
}
