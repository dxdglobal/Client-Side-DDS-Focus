#!/usr/bin/env python3
"""
Test DDS Styling API Integration in JavaScript
This script creates a simple test page to verify the API integration
"""

import webbrowser
import os
from pathlib import Path

def create_test_page():
    """Create a simple HTML test page"""
    
    test_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DDS Styling API Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background: var(--background-color, #f5f5f5);
            color: var(--text-color, #333);
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            border-radius: var(--border-radius, 8px);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        button {
            background-color: var(--button-color, #007bff);
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 10px;
            border-radius: var(--border-radius, 5px);
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        button:hover {
            background-color: var(--button-hover, #0056b3);
            transform: translateY(-2px);
        }
        
        .login-button {
            background: linear-gradient(145deg, var(--button-color, #28a745), var(--button-hover, #218838));
            font-weight: bold;
            min-width: 150px;
        }
        
        .primary-btn {
            background-color: var(--primary-color, #007bff);
        }
        
        .secondary-btn {
            background-color: var(--secondary-color, #6c757d);
        }
        
        .test-result {
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid var(--primary-color, #007bff);
            background: var(--background-color, #f8f9fa);
        }
        
        .log-container {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 DDS Styling API Integration Test</h1>
        
        <div class="test-result" id="status">
            <strong>Status:</strong> <span id="statusText">Initializing...</span>
        </div>
        
        <h2>Button Tests</h2>
        <p>These buttons should automatically receive colors from the DDS API:</p>
        
        <button class="login-button" onclick="testAPI()">LOGIN BUTTON TEST</button>
        <button class="primary-btn" onclick="refreshStyling()">PRIMARY BUTTON</button>
        <button class="secondary-btn" onclick="debugColors()">SECONDARY BUTTON</button>
        <button onclick="forceRefresh()">FORCE REFRESH</button>
        
        <h2>API Response Log</h2>
        <div class="log-container" id="logContainer">
            <div>Waiting for API response...</div>
        </div>
        
        <h2>Color Variables</h2>
        <div id="colorVariables">
            <p>Loading color variables...</p>
        </div>
        
        <h2>Debug Functions</h2>
        <p>Open browser console and try these functions:</p>
        <ul>
            <li><code>testButtonColor()</code> - Test API color loading</li>
            <li><code>refreshStyling()</code> - Refresh all styling</li>
            <li><code>debugColors()</code> - Show current color variables</li>
            <li><code>testAllAPIColors()</code> - Test complete API integration</li>
        </ul>
    </div>

    <!-- Include the styling API integration -->
    <script>
        // Simple API integration for testing
        class TestStylingAPI {
            constructor() {
                this.apiUrl = 'https://dxdtime.ddsolutions.io/api/styling/global/';
                this.logContainer = document.getElementById('logContainer');
                this.statusElement = document.getElementById('statusText');
                this.colorVariablesElement = document.getElementById('colorVariables');
            }
            
            log(message, type = 'info') {
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.style.color = type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#333';
                logEntry.innerHTML = `[${timestamp}] ${message}`;
                this.logContainer.appendChild(logEntry);
                this.logContainer.scrollTop = this.logContainer.scrollHeight;
                console.log(message);
            }
            
            updateStatus(message, type = 'info') {
                this.statusElement.textContent = message;
                this.statusElement.style.color = type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#333';
            }
            
            async testAPI() {
                try {
                    this.log('🔍 Testing DDS Styling API...');
                    this.updateStatus('Loading API data...');
                    
                    const response = await fetch(this.apiUrl, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    this.log(`✅ API Response received: ${JSON.stringify(data, null, 2)}`, 'success');
                    
                    if (data.status === 'success' && data.data) {
                        this.applyColors(data.data);
                        this.updateStatus('API colors applied successfully!', 'success');
                        this.displayColorVariables(data.data);
                        return data.data;
                    } else {
                        throw new Error('Invalid API response format');
                    }
                    
                } catch (error) {
                    this.log(`❌ API Error: ${error.message}`, 'error');
                    this.updateStatus(`API Error: ${error.message}`, 'error');
                    throw error;
                }
            }
            
            applyColors(stylingData) {
                const root = document.documentElement;
                
                if (stylingData.primary_color) {
                    root.style.setProperty('--primary-color', stylingData.primary_color);
                    this.log(`🔵 Primary color: ${stylingData.primary_color}`);
                }
                
                if (stylingData.secondary_color) {
                    root.style.setProperty('--secondary-color', stylingData.secondary_color);
                    this.log(`🟢 Secondary color: ${stylingData.secondary_color}`);
                }
                
                if (stylingData.background_color) {
                    root.style.setProperty('--background-color', stylingData.background_color);
                    document.body.style.backgroundColor = stylingData.background_color;
                    this.log(`⚪ Background color: ${stylingData.background_color}`);
                }
                
                if (stylingData.button_color) {
                    root.style.setProperty('--button-color', stylingData.button_color);
                    root.style.setProperty('--button-hover', this.darkenColor(stylingData.button_color, 10));
                    this.log(`🔴 Button color: ${stylingData.button_color}`);
                }
                
                if (stylingData.text_color) {
                    root.style.setProperty('--text-color', stylingData.text_color);
                    document.body.style.color = stylingData.text_color;
                    this.log(`⚫ Text color: ${stylingData.text_color}`);
                }
                
                if (stylingData.font_family) {
                    root.style.setProperty('--font-family', stylingData.font_family);
                    document.body.style.fontFamily = stylingData.font_family;
                    this.log(`📝 Font family: ${stylingData.font_family}`);
                }
                
                if (stylingData.border_radius) {
                    root.style.setProperty('--border-radius', stylingData.border_radius);
                    this.log(`📐 Border radius: ${stylingData.border_radius}`);
                }
            }
            
            displayColorVariables(stylingData) {
                const variables = [
                    ['Primary Color', stylingData.primary_color],
                    ['Secondary Color', stylingData.secondary_color],
                    ['Background Color', stylingData.background_color],
                    ['Button Color', stylingData.button_color],
                    ['Text Color', stylingData.text_color],
                    ['Font Family', stylingData.font_family],
                    ['Border Radius', stylingData.border_radius]
                ];
                
                let html = '<table style="width: 100%; border-collapse: collapse;">';
                variables.forEach(([name, value]) => {
                    if (value) {
                        html += `<tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 8px; font-weight: bold;">${name}:</td>
                            <td style="padding: 8px;">${value}</td>
                            <td style="padding: 8px; width: 30px;">`;
                        
                        if (value.startsWith('#')) {
                            html += `<div style="width: 20px; height: 20px; background: ${value}; border: 1px solid #ccc; border-radius: 3px;"></div>`;
                        }
                        
                        html += `</td></tr>`;
                    }
                });
                html += '</table>';
                
                this.colorVariablesElement.innerHTML = html;
            }
            
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
        }
        
        // Initialize the test
        const testAPI = new TestStylingAPI();
        
        // Auto-run test when page loads
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                testAPI.testAPI();
            }, 1000);
        });
        
        // Global functions for manual testing
        window.testAPI = () => testAPI.testAPI();
        window.refreshStyling = () => testAPI.testAPI();
        window.forceRefresh = () => {
            testAPI.log('🔄 Force refresh triggered...');
            testAPI.testAPI();
        };
        window.debugColors = () => {
            const root = document.documentElement;
            const style = getComputedStyle(root);
            
            console.log('🎨 Current CSS Variables:');
            console.log('--primary-color:', style.getPropertyValue('--primary-color'));
            console.log('--secondary-color:', style.getPropertyValue('--secondary-color'));
            console.log('--background-color:', style.getPropertyValue('--background-color'));
            console.log('--button-color:', style.getPropertyValue('--button-color'));
            console.log('--text-color:', style.getPropertyValue('--text-color'));
            
            testAPI.log('🎨 Color variables logged to console');
        };
    </script>
</body>
</html>
"""
    
    # Write test file
    test_file = Path(__file__).parent / "api_styling_test.html"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print(f"✅ Test page created: {test_file}")
    return test_file

def main():
    print("🧪 Creating DDS Styling API test page...")
    
    try:
        test_file = create_test_page()
        
        print("\n🎨 DDS Styling API Integration Test")
        print("=" * 50)
        print(f"📄 Test file: {test_file}")
        print(f"🌐 Open in browser to test API integration")
        print("\n🔍 The test page will:")
        print("  • Load colors from https://dxdtime.ddsolutions.io/api/styling/global/")
        print("  • Apply colors to buttons and elements")
        print("  • Show API response in real-time")
        print("  • Display color variables")
        print("  • Provide debug functions")
        
        # Ask user if they want to open the test page
        if input("\n🌐 Open test page in browser? (y/n): ").lower().startswith('y'):
            webbrowser.open(f"file://{test_file.absolute()}")
            print("🚀 Test page opened in browser!")
        
        print("\n🧪 Manual Tests:")
        print("  1. Check if buttons change color automatically")
        print("  2. Open browser console and try debug functions")
        print("  3. Verify API response is displayed correctly")
        print("  4. Test manual refresh functionality")
        
    except Exception as e:
        print(f"❌ Error creating test page: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
