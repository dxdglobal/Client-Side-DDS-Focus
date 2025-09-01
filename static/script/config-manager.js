/**
 * Configuration Manager for Frontend
 * Fetches configuration from API and applies it to the UI
 */

class ConfigManager {
    constructor() {
        this.config = null;
        this.defaultConfig = {
            ui: {
                primary_color: "#006039",
                secondary_color: "#004d2e",
                background_color: "#ffffff",
                text_color: "#333333",
                font_size: {
                    small: "12px",
                    medium: "14px",
                    large: "16px",
                    extra_large: "18px"
                },
                font_family: "Inter, sans-serif"
            },
            screenshot: {
                interval_seconds: 30,
                quality: 85,
                format: "JPEG"
            },
            features: {
                ai_analysis: true,
                auto_categorization: true,
                idle_detection: true,
                program_tracking: true,
                email_notifications: false
            }
        };
    }

    /**
     * Fetch configuration from API
     * @returns {Promise<Object>} Configuration object
     */
    async fetchConfiguration() {
        try {
            console.log('🔄 Fetching configuration from API...');
            
            const response = await fetch('/api/config', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.config = data.config;
                console.log('✅ Configuration loaded from API:', data.source);
                console.log('📋 Config:', this.config);
                return this.config;
            } else {
                throw new Error(data.error || 'Failed to fetch configuration');
            }
        } catch (error) {
            console.warn('⚠️ Failed to fetch configuration from API:', error.message);
            console.log('🔄 Using default configuration');
            this.config = this.defaultConfig;
            return this.config;
        }
    }

    /**
     * Refresh configuration from API
     * @returns {Promise<Object>} Updated configuration
     */
    async refreshConfiguration() {
        try {
            console.log('🔄 Refreshing configuration...');
            
            const response = await fetch('/api/config/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.config = data.config;
                console.log('✅ Configuration refreshed successfully');
                this.applyConfiguration();
                return this.config;
            } else {
                throw new Error(data.error || 'Failed to refresh configuration');
            }
        } catch (error) {
            console.error('❌ Failed to refresh configuration:', error.message);
            throw error;
        }
    }

    /**
     * Get screenshot interval from API
     * @returns {Promise<number>} Interval in seconds
     */
    async getScreenshotInterval() {
        try {
            const response = await fetch('/api/config/screenshot-interval');
            const data = await response.json();
            
            if (data.success) {
                return data.interval_seconds;
            } else {
                return this.defaultConfig.screenshot.interval_seconds;
            }
        } catch (error) {
            console.warn('⚠️ Failed to get screenshot interval:', error.message);
            return this.defaultConfig.screenshot.interval_seconds;
        }
    }

    /**
     * Apply configuration to the UI
     */
    applyConfiguration() {
        if (!this.config) {
            console.warn('⚠️ No configuration to apply');
            return;
        }

        console.log('🎨 Applying configuration to UI...');

        // Apply CSS variables
        this.applyCSSVariables();
        
        // Apply font settings
        this.applyFontSettings();
        
        // Update UI elements
        this.updateUIElements();
        
        console.log('✅ Configuration applied successfully');
    }

    /**
     * Apply CSS custom properties from configuration
     */
    applyCSSVariables() {
        const root = document.documentElement;
        const ui = this.config.ui || {};

        // Apply color variables
        if (ui.primary_color) {
            root.style.setProperty('--primary-color', ui.primary_color);
        }
        if (ui.secondary_color) {
            root.style.setProperty('--secondary-color', ui.secondary_color);
        }
        if (ui.background_color) {
            root.style.setProperty('--background-color', ui.background_color);
        }
        if (ui.text_color) {
            root.style.setProperty('--text-color', ui.text_color);
        }

        // Apply font size variables
        const fontSize = ui.font_size || {};
        if (fontSize.small) {
            root.style.setProperty('--font-size-small', fontSize.small);
        }
        if (fontSize.medium) {
            root.style.setProperty('--font-size-medium', fontSize.medium);
        }
        if (fontSize.large) {
            root.style.setProperty('--font-size-large', fontSize.large);
        }
        if (fontSize.extra_large) {
            root.style.setProperty('--font-size-extra-large', fontSize.extra_large);
        }

        // Apply font family
        if (ui.font_family) {
            root.style.setProperty('--font-family-primary', ui.font_family);
        }

        console.log('🎨 CSS variables applied');
    }

    /**
     * Apply font settings to body
     */
    applyFontSettings() {
        const ui = this.config.ui || {};
        
        if (ui.font_family) {
            document.body.style.fontFamily = ui.font_family;
        }
    }

    /**
     * Update specific UI elements based on configuration
     */
    updateUIElements() {
        // Update screenshot interval display if exists
        const intervalDisplay = document.getElementById('screenshot-interval-display');
        if (intervalDisplay && this.config.screenshot) {
            intervalDisplay.textContent = `${this.config.screenshot.interval_seconds}s`;
        }

        // Update feature toggles
        this.updateFeatureToggles();
    }

    /**
     * Update feature toggle states
     */
    updateFeatureToggles() {
        const features = this.config.features || {};
        
        Object.entries(features).forEach(([feature, enabled]) => {
            const toggle = document.getElementById(`feature-${feature.replace('_', '-')}`);
            if (toggle) {
                toggle.checked = enabled;
                toggle.dispatchEvent(new Event('change'));
            }
        });
    }

    /**
     * Get configuration value by path
     * @param {string} path - Dot notation path (e.g., 'ui.primary_color')
     * @param {*} defaultValue - Default value if path not found
     * @returns {*} Configuration value
     */
    getValue(path, defaultValue = null) {
        if (!this.config) return defaultValue;
        
        return path.split('.').reduce((obj, key) => {
            return obj && obj[key] !== undefined ? obj[key] : defaultValue;
        }, this.config);
    }

    /**
     * Initialize configuration system
     */
    async initialize() {
        console.log('🚀 Initializing Configuration Manager...');
        
        try {
            await this.fetchConfiguration();
            this.applyConfiguration();
            
            // Set up periodic refresh (every 5 minutes)
            setInterval(() => {
                this.refreshConfiguration().catch(console.error);
            }, 5 * 60 * 1000);
            
            console.log('✅ Configuration Manager initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Configuration Manager:', error);
        }
    }
}

// Global instance
window.configManager = new ConfigManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.configManager.initialize();
    });
} else {
    window.configManager.initialize();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConfigManager;
}
