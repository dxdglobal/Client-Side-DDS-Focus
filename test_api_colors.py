#!/usr/bin/env python3
"""
Test script to verify DDS API color fields implementation
Tests all color fields: header-color, footer-color, text_color, background_color, button_color, button-text_color
"""

import requests
import json
from datetime import datetime

def test_dds_api_colors():
    """Test the DDS styling API and verify all color fields are available"""
    
    api_url = "https://dxdtime.ddsolutions.io/api/styling/global/"
    
    print(f"🧪 Testing DDS Styling API at: {api_url}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Make API request
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'success' and 'data' in data:
            styling_data = data['data']
            
            print("✅ API Response Success!")
            print(f"🎨 Theme Name: {styling_data.get('theme_name', 'Unknown')}")
            print(f"📝 Description: {styling_data.get('description', 'N/A')}")
            print()
            
            # Test all requested color fields
            color_fields = [
                ('header-color', 'Header Color'),
                ('footer-color', 'Footer Color'), 
                ('text_color', 'Text Color'),
                ('background_color', 'Background Color'),
                ('button_color', 'Button Color'),
                ('button-text_color', 'Button Text Color')
            ]
            
            print("🎨 API Color Fields Status:")
            print("-" * 40)
            
            all_fields_present = True
            
            for field_key, field_name in color_fields:
                if field_key in styling_data:
                    color_value = styling_data[field_key]
                    print(f"✅ {field_name:18}: {color_value}")
                else:
                    print(f"❌ {field_name:18}: NOT FOUND")
                    all_fields_present = False
            
            print()
            
            # Additional fields for completeness
            additional_fields = [
                ('font_family', 'Font Family'),
                ('border_radius', 'Border Radius'),
                ('heading_font_size', 'Heading Font Size'),
                ('body_font_size', 'Body Font Size')
            ]
            
            print("📝 Additional Style Fields:")
            print("-" * 40)
            
            for field_key, field_name in additional_fields:
                if field_key in styling_data:
                    field_value = styling_data[field_key]
                    print(f"✅ {field_name:18}: {field_value}")
                else:
                    print(f"⚪ {field_name:18}: Not available")
            
            print()
            
            # Implementation status
            if all_fields_present:
                print("🎉 SUCCESS: All requested color fields are available in the API!")
                print("✅ Your JavaScript implementation should be able to retrieve:")
                print("   - header-color")
                print("   - footer-color") 
                print("   - text_color")
                print("   - background_color")
                print("   - button_color")
                print("   - button-text_color")
            else:
                print("⚠️  WARNING: Some color fields are missing from the API")
                print("   Check the API documentation or contact the API provider")
            
            print()
            print("🔧 Implementation Notes:")
            print("   - JavaScript should handle both 'header-color' and 'header_color' formats")
            print("   - Use fallback colors for any missing fields")
            print("   - CSS variables should be set with !important for proper override")
            
            return True
            
        else:
            print(f"❌ API Error: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def generate_css_variables_test():
    """Generate CSS variables for testing"""
    
    print("\n" + "=" * 60)
    print("🎨 CSS Variables Test Code:")
    print("=" * 60)
    
    css_code = """
/* Test CSS Variables for DDS API Color Fields */
:root {
    /* Core Colors */
    --text-color: var(--api-text-color, #000);
    --background-color: var(--api-background-color, #fff);
    --button-color: var(--api-button-color, #007bff);
    
    /* New Color Fields */
    --header-color: var(--api-header-color, #ffffff);
    --footer-color: var(--api-footer-color, #ffffff);
    --button-text-color: var(--api-button-text-color, #ffffff);
}

/* Header Styling */
header, .header, .window-header {
    background-color: var(--header-color) !important;
}

/* Footer Styling */
footer, .footer {
    background-color: var(--footer-color) !important;
}

/* Button Text Styling */
button, .btn {
    color: var(--button-text-color) !important;
}
"""
    
    print(css_code)

def generate_javascript_test():
    """Generate JavaScript test code"""
    
    print("\n" + "=" * 60)
    print("🚀 JavaScript Test Code:")
    print("=" * 60)
    
    js_code = """
// Test function to verify API color implementation
async function testAllAPIColors() {
    try {
        const response = await fetch('https://dxdtime.ddsolutions.io/api/styling/global/');
        const data = await response.json();
        
        if (data.status === 'success' && data.data) {
            const styling = data.data;
            
            console.log('🎨 API Color Fields Test:');
            console.log('Header Color:', styling['header-color'] || 'NOT FOUND');
            console.log('Footer Color:', styling['footer-color'] || 'NOT FOUND');
            console.log('Text Color:', styling.text_color || 'NOT FOUND');
            console.log('Background Color:', styling.background_color || 'NOT FOUND');
            console.log('Button Color:', styling.button_color || 'NOT FOUND');
            console.log('Button Text Color:', styling['button-text_color'] || 'NOT FOUND');
            
            // Apply to CSS variables
            const root = document.documentElement;
            root.style.setProperty('--header-color', styling['header-color'] || '#ffffff', 'important');
            root.style.setProperty('--footer-color', styling['footer-color'] || '#ffffff', 'important');
            root.style.setProperty('--button-text-color', styling['button-text_color'] || '#ffffff', 'important');
            
            console.log('✅ All API colors applied to CSS variables');
        }
    } catch (error) {
        console.error('❌ API Test Error:', error);
    }
}

// Run the test
testAllAPIColors();
"""
    
    print(js_code)

if __name__ == "__main__":
    print("🚀 DDS API Color Fields Test Suite")
    print("Testing implementation for: header-color, footer-color, text_color, background_color, button_color, button-text_color")
    print()
    
    success = test_dds_api_colors()
    
    if success:
        generate_css_variables_test()
        generate_javascript_test()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete!")
    print("   Run this script periodically to verify API availability")
    print("   Copy the generated CSS and JavaScript code for testing")
    print("=" * 60)
