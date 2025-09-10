/**
 * Login Page - DDS Styling API Integration
 * Dedicated JavaScript for login page styling management
 */

class LoginStylingManager {
    constructor() {
        this.apiUrl = 'https://dxdtime.ddsolutions.io/api/styling/global/';
        this.proxyUrl = '/api/styling/proxy';
        this.retryAttempts = 3;
        this.retryDelay = 1500;
        this.currentStyling = null;
    }

    async initializeLoginStyling() {
        console.log('🔑 Login.js: Initializing DDS styling for login page...');
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const styling = await this.loadStylingFromAPI();
                if (styling) {
                    this.currentStyling = styling;
                    this.applyLoginStyling(styling);
                    this.setupLoginButtonEffects(styling);
                    console.log('✅ Login.js: Styling applied successfully');
                    return styling;
                }
            } catch (error) {
                console.warn(`⚠️ Login.js: Styling attempt ${attempt}/${this.retryAttempts} failed:`, error);
                
                if (attempt < this.retryAttempts) {
                    await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                } else {
                    console.error('❌ Login.js: All styling attempts failed');
                    this.applyMinimalStyling();
                }
            }
        }
    }

    async loadStylingFromAPI() {
        try {
            // Try proxy first to avoid CORS
            const response = await fetch(this.proxyUrl, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`Proxy failed: ${response.status}`);
            }

            const proxyData = await response.json();
            if (!proxyData.success) {
                throw new Error(`Proxy error: ${proxyData.error}`);
            }

            const apiData = proxyData.data;
            let stylingData = null;

            // Handle different API response structures
            if (apiData.status === 'success' && apiData.data) {
                stylingData = apiData.data;
            } else if (apiData.button_color !== undefined) {
                stylingData = apiData;
            } else {
                throw new Error('Invalid API response structure');
            }

            console.log('✅ Login.js: API styling data loaded:', stylingData);
            return stylingData;

        } catch (error) {
            console.warn('⚠️ Login.js: Failed to load from proxy, trying direct API...');
            
            // Fallback to direct API
            try {
                const directResponse = await fetch(this.apiUrl, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (directResponse.ok) {
                    const directData = await directResponse.json();
                    if (directData.status === 'success' && directData.data) {
                        console.log('✅ Login.js: Direct API styling loaded');
                        return directData.data;
                    }
                }
            } catch (directError) {
                console.error('❌ Login.js: Direct API also failed:', directError);
            }
            
            throw error;
        }
    }

    applyLoginStyling(stylingData) {
        const root = document.documentElement;
        console.log('🎨 Login.js: Applying comprehensive styling...');

        // Apply all color systems with !important for login page
        if (stylingData.primary_color) {
            root.style.setProperty('--primary-color', stylingData.primary_color, 'important');
            root.style.setProperty('--primary-hover', this.darkenColor(stylingData.primary_color, 10), 'important');
            console.log('🔵 Login: Primary color applied:', stylingData.primary_color);
        }

        if (stylingData.secondary_color) {
            root.style.setProperty('--secondary-color', stylingData.secondary_color, 'important');
            root.style.setProperty('--success-color', stylingData.secondary_color, 'important');
            console.log('🟢 Login: Secondary color applied:', stylingData.secondary_color);
        }

        if (stylingData.background_color) {
            root.style.setProperty('--background-color', stylingData.background_color, 'important');
            // Apply to body with slight transparency for login page
            const bgWithAlpha = this.hexToRgba(stylingData.background_color, 0.95);
            document.body.style.setProperty('background-color', bgWithAlpha, 'important');
            console.log('⚪ Login: Background color applied:', stylingData.background_color);
        }

        if (stylingData.button_color) {
            root.style.setProperty('--button-color', stylingData.button_color, 'important');
            root.style.setProperty('--button-hover', this.darkenColor(stylingData.button_color, 10), 'important');
            root.style.setProperty('--button-active', this.darkenColor(stylingData.button_color, 20), 'important');
            
            // Apply to all login buttons immediately
            this.applyLoginButtonColors(stylingData.button_color);
            console.log('🔴 Login: Button color applied:', stylingData.button_color);
        }

        if (stylingData.text_color) {
            root.style.setProperty('--text-color', stylingData.text_color, 'important');
            console.log('⚫ Login: Text color applied:', stylingData.text_color);
            
            // Apply text color to specific login page elements
            const textElements = document.querySelectorAll('#rememberMeLabel, .forgot-password, .title, .subtitle');
            textElements.forEach(element => {
                element.style.setProperty('color', stylingData.text_color, 'important');
            });
            
            console.log('🔤 Login: Applied text color to labels and text elements');
        }

        // 🎨 NEW: Apply header color
        if (stylingData['header-color'] || stylingData.header_color) {
            const headerColor = stylingData['header-color'] || stylingData.header_color;
            root.style.setProperty('--header-color', headerColor, 'important');
            
            // Apply to header elements in login page
            const headerElements = document.querySelectorAll('header, .header, .window-header, .login-header');
            headerElements.forEach(element => {
                element.style.setProperty('background-color', headerColor, 'important');
            });
            console.log('🎯 Login: Header color applied:', headerColor);
        }

        // 🎨 NEW: Apply footer color
        if (stylingData['footer-color'] || stylingData.footer_color) {
            const footerColor = stylingData['footer-color'] || stylingData.footer_color;
            root.style.setProperty('--footer-color', footerColor, 'important');
            
            // Apply to footer elements in login page
            const footerElements = document.querySelectorAll('footer, .footer, .login-footer');
            footerElements.forEach(element => {
                element.style.setProperty('background-color', footerColor, 'important');
            });
            console.log('🎯 Login: Footer color applied:', footerColor);
        }

        // 🎨 NEW: Apply button text color
        if (stylingData['button-text_color'] || stylingData.button_text_color) {
            const buttonTextColor = stylingData['button-text_color'] || stylingData.button_text_color;
            root.style.setProperty('--button-text-color', buttonTextColor, 'important');
            
            // Apply to all login buttons
            const loginButtons = document.querySelectorAll('.login-button, #loginBtn, .guest-button, button[type="submit"]');
            loginButtons.forEach(button => {
                button.style.setProperty('color', buttonTextColor, 'important');
            });
            console.log('🔤 Login: Button text color applied:', buttonTextColor);
        }

        // Apply font settings
        if (stylingData.font_family) {
            root.style.setProperty('--font-family', stylingData.font_family, 'important');
            document.body.style.setProperty('font-family', stylingData.font_family, 'important');
            console.log('📝 Login: Font family applied:', stylingData.font_family);
        }

        // 🎨 NEW: Submit Button Styling (highest priority for login)
        if (stylingData.submit_button_bg_color) {
            root.style.setProperty('--submit-button-bg-color', stylingData.submit_button_bg_color, 'important');
            
            const submitButtons = document.querySelectorAll('button[type="submit"], .submit-btn, .login-button');
            submitButtons.forEach(button => {
                button.style.setProperty('background-color', stylingData.submit_button_bg_color, 'important');
                button.style.setProperty('border-color', stylingData.submit_button_bg_color, 'important');
            });
            console.log('🟢 Login: Submit button background applied:', stylingData.submit_button_bg_color);
        }

        if (stylingData.submit_button_text_color) {
            root.style.setProperty('--submit-button-text-color', stylingData.submit_button_text_color, 'important');
            
            const submitButtons = document.querySelectorAll('button[type="submit"], .submit-btn, .login-button');
            submitButtons.forEach(button => {
                button.style.setProperty('color', stylingData.submit_button_text_color, 'important');
            });
            console.log('🔤 Login: Submit button text color applied:', stylingData.submit_button_text_color);
        }

        // 🎨 NEW: Primary Button Styling
        if (stylingData.primary_button_bg_color) {
            root.style.setProperty('--primary-button-bg-color', stylingData.primary_button_bg_color, 'important');
            
            const primaryButtons = document.querySelectorAll('.btn-primary, .primary-btn');
            primaryButtons.forEach(button => {
                button.style.setProperty('background-color', stylingData.primary_button_bg_color, 'important');
                button.style.setProperty('border-color', stylingData.primary_button_bg_color, 'important');
            });
            console.log('🔵 Login: Primary button background applied:', stylingData.primary_button_bg_color);
        }

        if (stylingData.primary_button_text_color) {
            root.style.setProperty('--primary-button-text-color', stylingData.primary_button_text_color, 'important');
            
            const primaryButtons = document.querySelectorAll('.btn-primary, .primary-btn');
            primaryButtons.forEach(button => {
                button.style.setProperty('color', stylingData.primary_button_text_color, 'important');
            });
            console.log('🔤 Login: Primary button text color applied:', stylingData.primary_button_text_color);
        }

        // 🎨 NEW: Secondary Button Styling
        if (stylingData.secondary_button_bg_color) {
            root.style.setProperty('--secondary-button-bg-color', stylingData.secondary_button_bg_color, 'important');
            
            const secondaryButtons = document.querySelectorAll('.btn-secondary, .secondary-btn, .guest-button');
            secondaryButtons.forEach(button => {
                button.style.setProperty('background-color', stylingData.secondary_button_bg_color, 'important');
                button.style.setProperty('border-color', stylingData.secondary_button_bg_color, 'important');
            });
            console.log('🟤 Login: Secondary button background applied:', stylingData.secondary_button_bg_color);
        }

        if (stylingData.secondary_button_text_color) {
            root.style.setProperty('--secondary-button-text-color', stylingData.secondary_button_text_color, 'important');
            
            const secondaryButtons = document.querySelectorAll('.btn-secondary, .secondary-btn, .guest-button');
            secondaryButtons.forEach(button => {
                button.style.setProperty('color', stylingData.secondary_button_text_color, 'important');
            });
            console.log('🔤 Login: Secondary button text color applied:', stylingData.secondary_button_text_color);
        }

        // 🎨 NEW: Drawer Styling
        if (stylingData.drawer_background_color) {
            root.style.setProperty('--drawer-background-color', stylingData.drawer_background_color, 'important');
            
            const drawerElements = document.querySelectorAll('.drawer, .sidebar, .nav-drawer');
            drawerElements.forEach(element => {
                element.style.setProperty('background-color', stylingData.drawer_background_color, 'important');
            });
            console.log('📦 Login: Drawer background color applied:', stylingData.drawer_background_color);
        }

        if (stylingData.drawer_text_color) {
            root.style.setProperty('--drawer-text-color', stylingData.drawer_text_color, 'important');
            
            const drawerTextElements = document.querySelectorAll('.drawer *, .sidebar *, .nav-drawer *');
            drawerTextElements.forEach(element => {
                element.style.setProperty('color', stylingData.drawer_text_color, 'important');
            });
            console.log('🔤 Login: Drawer text color applied:', stylingData.drawer_text_color);
        }

        // 🎨 NEW: Icon Color
        if (stylingData.icon_color) {
            root.style.setProperty('--icon-color', stylingData.icon_color, 'important');
            
            const iconElements = document.querySelectorAll('.icon, i, .fa, [class*="icon-"]');
            iconElements.forEach(icon => {
                icon.style.setProperty('color', stylingData.icon_color, 'important');
                icon.style.setProperty('fill', stylingData.icon_color, 'important');
            });
            console.log('🎯 Login: Icon color applied:', stylingData.icon_color);
        }

        // 🎨 NEW: Top Color (header/top bar)
        if (stylingData.top_color) {
            root.style.setProperty('--top-color', stylingData.top_color, 'important');
            
            const topElements = document.querySelectorAll('.top-bar, .header, .navbar, .window-header');
            topElements.forEach(element => {
                element.style.setProperty('background-color', stylingData.top_color, 'important');
            });
            console.log('⬆️ Login: Top color applied:', stylingData.top_color);
        }

        // 🎨 NEW: Enhanced Font Settings
        if (stylingData.heading_font_size) {
            root.style.setProperty('--heading-font-size', stylingData.heading_font_size, 'important');
            
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, .title, .heading');
            headings.forEach(heading => {
                heading.style.setProperty('font-size', stylingData.heading_font_size, 'important');
            });
            console.log('📏 Login: Heading font size applied:', stylingData.heading_font_size);
        }

        if (stylingData.body_font_size) {
            root.style.setProperty('--body-font-size', stylingData.body_font_size, 'important');
            document.body.style.setProperty('font-size', stylingData.body_font_size, 'important');
            console.log('📏 Login: Body font size applied:', stylingData.body_font_size);
        }

        if (stylingData.border_radius) {
            root.style.setProperty('--border-radius', stylingData.border_radius, 'important');
            
            const roundedElements = document.querySelectorAll('button, .btn, input, .form-control, .card, .modal');
            roundedElements.forEach(element => {
                element.style.setProperty('border-radius', stylingData.border_radius, 'important');
            });
            console.log('📐 Login: Border radius applied:', stylingData.border_radius);
        }

        // Apply specific login page elements
        this.applyLoginSpecificStyling(stylingData);
    }

    applyLoginButtonColors(buttonColor) {
        // Comprehensive login button selectors
        const loginButtonSelectors = [
            '.login-button', '#loginBtn', '.guest-button',
            'button[type="submit"]', '.btn-primary',
            'input[type="submit"]', '.submit-btn'
        ];

        let appliedCount = 0;
        loginButtonSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.style.setProperty('background-color', buttonColor, 'important');
                element.style.setProperty('border-color', buttonColor, 'important');
                element.style.setProperty('background', `linear-gradient(145deg, ${buttonColor}, ${this.darkenColor(buttonColor, 15)})`, 'important');
                appliedCount++;
            });
        });

        console.log(`🔴 Login: Applied button color to ${appliedCount} elements`);
    }

    applyLoginSpecificStyling(stylingData) {
        // Header styling - use header_color if available, fallback to primary_color
        const headerColor = stylingData['header-color'] || stylingData.header_color || stylingData.primary_color;
        if (headerColor) {
            const header = document.querySelector('.window-header');
            if (header) {
                header.style.setProperty('background-color', headerColor, 'important');
                header.style.setProperty('color', stylingData.background_color || 'inherit', 'important');
            }
        }

        // Apply text color to specific login elements
        if (stylingData.text_color) {
            const textElements = [
                '#rememberMeLabel',
                '.forgot-password', 
                '.title', 
                '.subtitle',
                '.version',
                '.staff-data h3'
            ];
            
            textElements.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.style.setProperty('color', stylingData.text_color, 'important');
                }
            });
            
            console.log('🔤 Login: Applied text color to specific elements including Remember Me label');
        }

        // 🎨 NEW: Apply footer color to footer elements
        const footerColor = stylingData['footer-color'] || stylingData.footer_color;
        if (footerColor) {
            const footerElements = document.querySelectorAll('footer, .footer, .login-footer, .bottom-section');
            footerElements.forEach(element => {
                element.style.setProperty('background-color', footerColor, 'important');
            });
            console.log('🎯 Login: Applied footer color to footer elements');
        }

        // 🎨 NEW: Apply button text color with higher specificity
        const buttonTextColor = stylingData['button-text_color'] || stylingData.button_text_color;
        if (buttonTextColor) {
            const allLoginButtons = document.querySelectorAll('.login-button, #loginBtn, .guest-button, button[type="submit"], .btn-primary');
            allLoginButtons.forEach(button => {
                button.style.setProperty('color', buttonTextColor, 'important');
                // Also set text-related properties
                button.style.setProperty('--button-text-color', buttonTextColor, 'important');
            });
            console.log('🔤 Login: Applied button text color with high specificity');
        }

        // Form input styling
        if (stylingData.primary_color && stylingData.background_color) {
            const inputs = document.querySelectorAll('.input-field, input[type="text"], input[type="password"]');
            inputs.forEach(input => {
                input.style.setProperty('border-color', this.lightenColor(stylingData.primary_color, 30), 'important');
                input.style.setProperty('background-color', stylingData.background_color, 'important');
                
                // Focus styling
                input.addEventListener('focus', () => {
                    input.style.setProperty('border-color', stylingData.primary_color, 'important');
                    input.style.setProperty('box-shadow', `0 0 0 2px ${this.hexToRgba(stylingData.primary_color, 0.25)}`, 'important');
                });
                
                input.addEventListener('blur', () => {
                    input.style.setProperty('border-color', this.lightenColor(stylingData.primary_color, 30), 'important');
                    input.style.setProperty('box-shadow', 'none', 'important');
                });
            });
        }

        // Language selector styling
        if (stylingData.secondary_color) {
            const langSelector = document.getElementById('languageSelector');
            if (langSelector) {
                langSelector.style.setProperty('border-color', stylingData.secondary_color, 'important');
                langSelector.style.setProperty('background-color', stylingData.background_color, 'important');
            }
        }
    }

    setupLoginButtonEffects(stylingData) {
        if (!stylingData.button_color) return;

        const hoverColor = this.darkenColor(stylingData.button_color, 15);
        const activeColor = this.darkenColor(stylingData.button_color, 25);

        // Add hover effects to all login buttons
        const loginButtons = document.querySelectorAll('.login-button, #loginBtn, .guest-button');
        loginButtons.forEach(button => {
            // Remove existing listeners
            button.removeEventListener('mouseenter', button._loginHoverIn);
            button.removeEventListener('mouseleave', button._loginHoverOut);
            button.removeEventListener('mousedown', button._loginMouseDown);
            button.removeEventListener('mouseup', button._loginMouseUp);
            
            // Add new API-based effects
            button._loginHoverIn = () => {
                button.style.setProperty('background-color', hoverColor, 'important');
                button.style.setProperty('transform', 'translateY(-2px)', 'important');
                button.style.setProperty('box-shadow', `0 4px 8px ${this.hexToRgba(stylingData.button_color, 0.3)}`, 'important');
            };
            
            button._loginHoverOut = () => {
                button.style.setProperty('background-color', stylingData.button_color, 'important');
                button.style.setProperty('transform', 'translateY(0)', 'important');
                button.style.setProperty('box-shadow', `0 2px 4px ${this.hexToRgba(stylingData.button_color, 0.2)}`, 'important');
            };

            button._loginMouseDown = () => {
                button.style.setProperty('background-color', activeColor, 'important');
                button.style.setProperty('transform', 'translateY(1px)', 'important');
            };

            button._loginMouseUp = () => {
                button.style.setProperty('background-color', hoverColor, 'important');
                button.style.setProperty('transform', 'translateY(-2px)', 'important');
            };
            
            button.addEventListener('mouseenter', button._loginHoverIn);
            button.addEventListener('mouseleave', button._loginHoverOut);
            button.addEventListener('mousedown', button._loginMouseDown);
            button.addEventListener('mouseup', button._loginMouseUp);
        });

        console.log('✨ Login: Dynamic button effects applied');
    }

    applyMinimalStyling() {
        console.log('🔄 Login.js: Minimal styling - using API-only colors (no fallbacks)');
        // API-only color system - no hardcoded fallbacks
    }

    // Utility functions
    darkenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) - amt;
        const G = (num >> 8 & 0x00FF) - amt;
        const B = (num & 0x0000FF) - amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    lightenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    hexToRgba(hex, alpha = 1) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (result) {
            const r = parseInt(result[1], 16);
            const g = parseInt(result[2], 16);
            const b = parseInt(result[3], 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }
        // Return transparent for invalid hex values (API-only system)
        return `rgba(0, 0, 0, 0)`;
    }

    // Public methods for debugging
    refreshStyling() {
        console.log('🔄 Login.js: Manual styling refresh...');
        return this.initializeLoginStyling();
    }

    getCurrentStyling() {
        return this.currentStyling;
    }
}

// Initialize login styling manager
const loginStyling = new LoginStylingManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loginStyling.initializeLoginStyling();
    });
} else {
    loginStyling.initializeLoginStyling();
}

// Additional initialization after short delay
setTimeout(() => {
    console.log('🔄 Login.js: Delayed styling initialization...');
    loginStyling.initializeLoginStyling();
}, 1000);

// Periodic refresh every 3 minutes
setInterval(() => {
    console.log('🔄 Login.js: Periodic styling refresh...');
    loginStyling.initializeLoginStyling();
}, 3 * 60 * 1000);

// Debug functions for browser console
window.refreshLoginStyling = () => loginStyling.refreshStyling();
window.getLoginStyling = () => loginStyling.getCurrentStyling();
window.testLoginColors = () => {
    console.log('🧪 Testing login color application...');
    const buttons = document.querySelectorAll('.login-button, #loginBtn');
    console.log(`Found ${buttons.length} login buttons`);
    buttons.forEach((btn, index) => {
        const style = getComputedStyle(btn);
        console.log(`Button ${index + 1}:`, {
            backgroundColor: style.backgroundColor,
            borderColor: style.borderColor,
            color: style.color,
            element: btn
        });
    });

    // Test Remember Me label color
    const rememberMeLabel = document.getElementById('rememberMeLabel');
    if (rememberMeLabel) {
        const labelStyle = getComputedStyle(rememberMeLabel);
        console.log('🔤 Remember Me Label:', {
            color: labelStyle.color,
            textColor: labelStyle.getPropertyValue('color'),
            element: rememberMeLabel
        });
    }

    // Test other text elements
    const textElements = ['.title', '.subtitle', '.forgot-password', '.version'];
    textElements.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
            const style = getComputedStyle(element);
            console.log(`🔤 ${selector}:`, {
                color: style.color,
                element: element
            });
        }
    });

    // 🎨 NEW: Test header and footer colors
    console.log('🎯 Testing Header & Footer Colors:');
    const root = document.documentElement;
    const rootStyle = getComputedStyle(root);
    console.log('--header-color:', rootStyle.getPropertyValue('--header-color').trim());
    console.log('--footer-color:', rootStyle.getPropertyValue('--footer-color').trim());
    console.log('--button-text-color:', rootStyle.getPropertyValue('--button-text-color').trim());

    // Test actual header elements
    const headerElements = document.querySelectorAll('header, .header, .window-header');
    headerElements.forEach((header, index) => {
        const headerStyle = getComputedStyle(header);
        console.log(`🎯 Header ${index + 1}:`, {
            backgroundColor: headerStyle.backgroundColor,
            element: header
        });
    });

    // Test actual footer elements
    const footerElements = document.querySelectorAll('footer, .footer');
    footerElements.forEach((footer, index) => {
        const footerStyle = getComputedStyle(footer);
        console.log(`🎯 Footer ${index + 1}:`, {
            backgroundColor: footerStyle.backgroundColor,
            element: footer
        });
    });
    
    return loginStyling.refreshStyling();
};

console.log('✅ Login.js: DDS Styling API integration loaded');
console.log('🧪 Debug functions: refreshLoginStyling(), getLoginStyling(), testLoginColors()');

// � Production-ready: API-only color system initialized

// 🎨 NEW: Function to apply any custom theme
window.applyCustomLoginTheme = function(themeObject) {
    console.log('🎨 Applying custom login theme:', themeObject.theme_name || 'Unnamed Theme');
    
    loginStyling.currentStyling = themeObject;
    loginStyling.applyLoginStyling(themeObject);
    
    console.log('✅ Custom theme applied successfully!');
    return themeObject;
};

// 🎨 NEW: Test function to verify all new color fields
window.testAllNewColorFields = function() {
    console.log('🔍 Testing ALL NEW Color Fields Implementation...');
    
    const expectedFields = [
        'submit_button_bg_color', 'submit_button_text_color',
        'primary_button_bg_color', 'primary_button_text_color',
        'secondary_button_bg_color', 'secondary_button_text_color',
        'drawer_background_color', 'drawer_text_color',
        'icon_color', 'top_color', 'heading_font_size',
        'body_font_size', 'border_radius'
    ];
    
    const currentStyling = loginStyling.getCurrentStyling();
    
    console.log('\n📊 New Color Fields Status:');
    console.log('===========================');
    
    expectedFields.forEach(field => {
        const hasField = currentStyling && currentStyling[field];
        const status = hasField ? '✅' : '❌';
        const value = hasField ? currentStyling[field] : 'NOT SET';
        console.log(`${status} ${field}: ${value}`);
    });
    
    // Test CSS variables
    const root = document.documentElement;
    const style = getComputedStyle(root);
    
    console.log('\n🎨 CSS Variables Status:');
    console.log('========================');
    console.log('--submit-button-bg-color:', style.getPropertyValue('--submit-button-bg-color').trim() || 'NOT SET');
    console.log('--primary-button-bg-color:', style.getPropertyValue('--primary-button-bg-color').trim() || 'NOT SET');
    console.log('--secondary-button-bg-color:', style.getPropertyValue('--secondary-button-bg-color').trim() || 'NOT SET');
    console.log('--drawer-background-color:', style.getPropertyValue('--drawer-background-color').trim() || 'NOT SET');
    console.log('--icon-color:', style.getPropertyValue('--icon-color').trim() || 'NOT SET');
    console.log('--top-color:', style.getPropertyValue('--top-color').trim() || 'NOT SET');
    
    return expectedFields;
};

console.log('🆕 Theme functions: testPostmanTheme(), applyCustomLoginTheme(themeObject), testAllNewColorFields()');

// 🎨 NEW: Comprehensive login API color testing
window.testAllLoginAPIColors = async function() {
    console.log('🔑 Testing ALL Login API Color Fields...');
    
    try {
        const styling = await loginStyling.loadStylingFromAPI();
        
        if (styling) {
            console.log('🎨 Login API Color Fields Test Results:');
            console.log('========================================');
            console.log('✅ Header Color:', styling['header-color'] || 'NOT FOUND');
            console.log('✅ Footer Color:', styling['footer-color'] || 'NOT FOUND');
            console.log('✅ Text Color:', styling.text_color || 'NOT FOUND');
            console.log('✅ Background Color:', styling.background_color || 'NOT FOUND');
            console.log('✅ Button Color:', styling.button_color || 'NOT FOUND');
            console.log('✅ Button Text Color:', styling['button-text_color'] || 'NOT FOUND');
            
            // Apply fresh styling
            console.log('\n🔄 Applying fresh login styling...');
            loginStyling.applyLoginStyling(styling);
            
            // Test specific login elements
            console.log('\n🔍 Testing Login Elements:');
            
            // Test Remember Me label
            const rememberMeLabel = document.getElementById('rememberMeLabel');
            if (rememberMeLabel) {
                const labelStyle = getComputedStyle(rememberMeLabel);
                console.log('🔤 Remember Me Label Color:', labelStyle.color);
            }
            
            // Test login buttons
            const loginButtons = document.querySelectorAll('.login-button, #loginBtn');
            console.log(`🔴 Found ${loginButtons.length} login buttons`);
            loginButtons.forEach((btn, index) => {
                const btnStyle = getComputedStyle(btn);
                console.log(`  Button ${index + 1}:`, {
                    backgroundColor: btnStyle.backgroundColor,
                    color: btnStyle.color,
                    borderColor: btnStyle.borderColor
                });
            });
            
            console.log('✅ Login API Color Fields Test Complete!');
            return styling;
        }
    } catch (error) {
        console.error('❌ Login API Color Fields Test Error:', error);
    }
};

// 🎨 Function to verify login-specific implementation
window.verifyLoginImplementation = function() {
    console.log('🔍 Verifying Login Color Implementation...');
    
    const loginColorTests = [
        {
            name: 'Login Header Elements',
            selectors: ['header', '.header', '.window-header', '.login-header'],
            property: 'background-color'
        },
        {
            name: 'Login Footer Elements',
            selectors: ['footer', '.footer', '.login-footer'],
            property: 'background-color'
        },
        {
            name: 'Login Button Text',
            selectors: ['.login-button', '#loginBtn', '.guest-button'],
            property: 'color'
        },
        {
            name: 'Login Text Elements',
            selectors: ['#rememberMeLabel', '.title', '.subtitle', '.forgot-password'],
            property: 'color'
        }
    ];
    
    loginColorTests.forEach(test => {
        console.log(`\n🧪 Testing ${test.name}:`);
        test.selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            console.log(`  ${selector}: Found ${elements.length} elements`);
            
            elements.forEach((element, index) => {
                if (element) {
                    const style = getComputedStyle(element);
                    const value = style.getPropertyValue(test.property);
                    console.log(`    Element ${index + 1}: ${test.property} = ${value}`);
                }
            });
        });
    });
    
    console.log('\n✅ Login Color Implementation Verification Complete!');
};

console.log('🆕 New functions: testAllLoginAPIColors(), verifyLoginImplementation()');
