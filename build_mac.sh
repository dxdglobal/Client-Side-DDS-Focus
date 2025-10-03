#!/bin/bash
# Build script for DDS Focus Pro Mac Application

echo "🚀 DDS Focus Pro - Mac Build Script"
echo "===================================="

# Function to clean previous builds
clean_build() {
    echo "🧹 Cleaning previous builds..."
    rm -rf build/
    rm -rf dist/
    echo "✅ Cleaned previous builds"
}

# Function to build the application
build_app() {
    local spec_file=$1
    local build_name=$2
    
    echo ""
    echo "🔨 Building $build_name..."
    echo "Using spec file: $spec_file"
    
    if [ ! -f "$spec_file" ]; then
        echo "❌ Spec file not found: $spec_file"
        return 1
    fi
    
    pyinstaller --clean "$spec_file"
    
    if [ $? -eq 0 ]; then
        echo "✅ $build_name built successfully!"
        echo "📍 Location: $(pwd)/dist/"
        ls -la dist/
    else
        echo "❌ Build failed for $build_name"
        return 1
    fi
}

# Function to create a DMG (disk image)
create_dmg() {
    local app_name=$1
    echo ""
    echo "📦 Creating DMG installer for $app_name..."
    
    if [ -d "dist/$app_name.app" ]; then
        # Create a temporary directory for DMG contents
        mkdir -p "dmg_temp"
        cp -R "dist/$app_name.app" "dmg_temp/"
        
        # Create symbolic link to Applications folder
        ln -s /Applications "dmg_temp/Applications"
        
        # Create the DMG
        hdiutil create -srcfolder "dmg_temp" -format UDZO -imagekey zlib-level=9 -volname "$app_name" "dist/$app_name.dmg"
        
        # Clean up
        rm -rf "dmg_temp"
        
        echo "✅ DMG created: dist/$app_name.dmg"
    else
        echo "⚠️ App bundle not found, skipping DMG creation"
    fi
}

# Main menu
echo ""
echo "Choose build type:"
echo "1) Full build with all features (app_mac.spec)"
echo "2) Simple build with essential features (app_mac_simple.spec)"
echo "3) Production build with launcher (mac_launcher.spec)"
echo "4) Build all versions"
echo "5) Clean builds only"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        clean_build
        build_app "app_mac.spec" "Full Feature Build"
        create_dmg "DDSFocusPro"
        ;;
    2)
        clean_build
        build_app "app_mac_simple.spec" "Simple Build"
        create_dmg "DDSFocusPro-Simple"
        ;;
    3)
        clean_build
        build_app "mac_launcher.spec" "Production Build"
        create_dmg "DDSFocusPro"
        ;;
    4)
        clean_build
        echo "🔄 Building all versions..."
        build_app "app_mac_simple.spec" "Simple Build"
        mv dist dist_simple
        
        build_app "mac_launcher.spec" "Production Build"
        mv dist dist_production
        
        build_app "app_mac.spec" "Full Feature Build"
        mv dist dist_full
        
        echo ""
        echo "✅ All builds completed!"
        echo "📁 Simple build: dist_simple/"
        echo "📁 Production build: dist_production/"
        echo "📁 Full build: dist_full/"
        ;;
    5)
        clean_build
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Build process completed!"
echo "💡 To run the application:"
echo "   - Double-click the .app file in Finder"
echo "   - Or run from terminal: ./dist/DDSFocusPro.app/Contents/MacOS/DDSFocusPro"
echo ""
echo "📦 DMG files can be distributed to other Mac users"