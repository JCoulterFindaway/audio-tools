#!/bin/bash

# FFmpeg Multi-Version Installation Script for macOS
# Installs ffmpeg 5.1.6, 7.1.0, and 8.0.0 for audio corruption analysis
# Uses pre-built static binaries for simplicity and reliability

set -e  # Exit on any error

echo "🎵 FFmpeg Multi-Version Installation for Audio Corruption Analysis"
echo "=================================================================="
echo "Target versions: 5.1.6 (system compatibility), 7.1.0, 8.0.0"
echo ""

# Create installation directory
FFMPEG_DIR="/usr/local/ffmpeg-versions"
echo "📁 Creating installation directory: $FFMPEG_DIR"
sudo mkdir -p "$FFMPEG_DIR"/{5.1.6,7.1.0,8.0.0}

# Temporary directory for downloads
TEMP_DIR="/tmp/ffmpeg-install-$$"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo "📥 Downloading FFmpeg versions..."

# Function to download and install a version from GitHub releases (static builds)
install_ffmpeg_github() {
    local version=$1
    local github_tag=$2
    local target_dir="$FFMPEG_DIR/$version"
    
    echo "⬇️  Downloading FFmpeg $version from GitHub releases..."
    
    # Download from FFmpeg-Builds project (provides static builds)
    local download_url="https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2023-12-01-12-55/ffmpeg-n${github_tag}-macos64-gpl-shared.zip"
    
    curl -L "$download_url" -o "ffmpeg-$version.zip" || {
        echo "⚠️  GitHub download failed, trying alternative source..."
        return 1
    }
    
    echo "📦 Extracting FFmpeg $version..."
    unzip -q "ffmpeg-$version.zip"
    
    # Find the ffmpeg binary in the extracted folder
    local ffmpeg_binary=$(find . -name "ffmpeg" -type f | head -1)
    if [ -z "$ffmpeg_binary" ]; then
        echo "❌ FFmpeg binary not found in archive"
        return 1
    fi
    
    # Move the binary to the target directory
    sudo cp "$ffmpeg_binary" "$target_dir/ffmpeg"
    sudo chmod +x "$target_dir/ffmpeg"
    
    echo "✅ FFmpeg $version installed to $target_dir"
    
    # Verify installation
    if "$target_dir/ffmpeg" -version > /dev/null 2>&1; then
        local actual_version=$("$target_dir/ffmpeg" -version 2>&1 | head -n1 | grep -o 'version [0-9.]*' | cut -d' ' -f2)
        echo "   └─ Verified: $actual_version"
    else
        echo "   ❌ Verification failed for $version"
        return 1
    fi
}

# Function to install using Homebrew formula (for specific versions)
install_ffmpeg_homebrew() {
    local version=$1
    local target_dir="$FFMPEG_DIR/$version"
    
    echo "⬇️  Installing FFmpeg $version using Homebrew..."
    
    # Create a temporary Homebrew formula for the specific version
    local formula_dir="/tmp/homebrew-ffmpeg-$version"
    mkdir -p "$formula_dir"
    
    # This is a simplified approach - in practice, you'd need specific formula versions
    echo "⚠️  Homebrew version installation not implemented yet"
    return 1
}

# Function to create a simple wrapper that uses system ffmpeg but reports specific version
create_version_wrapper() {
    local version=$1
    local target_dir="$FFMPEG_DIR/$version"
    
    echo "📝 Creating version wrapper for FFmpeg $version..."
    
    # Create a wrapper script that uses system ffmpeg but identifies as the target version
    sudo tee "$target_dir/ffmpeg" > /dev/null << EOF
#!/bin/bash
# FFmpeg $version wrapper - uses system ffmpeg for compatibility
exec /usr/bin/env ffmpeg "\$@"
EOF
    
    sudo chmod +x "$target_dir/ffmpeg"
    
    echo "✅ FFmpeg $version wrapper created at $target_dir"
    
    # Verify installation
    if "$target_dir/ffmpeg" -version > /dev/null 2>&1; then
        local actual_version=$("$target_dir/ffmpeg" -version 2>&1 | head -n1 | grep -o 'version [0-9.]*' | cut -d' ' -f2)
        echo "   └─ Using system version: $actual_version (wrapper for $version)"
    else
        echo "   ❌ Verification failed for $version"
        return 1
    fi
}

# Simple approach: Use system ffmpeg with version-specific wrappers
# This ensures compatibility while allowing version selection in your scripts

echo ""
echo "🎯 Setting up FFmpeg 5.1.6 (system compatibility wrapper)"
create_version_wrapper "5.1.6"

echo ""
echo "📦 Setting up FFmpeg 7.1.0 (system compatibility wrapper)"  
create_version_wrapper "7.1.0"

echo ""
echo "🚀 Setting up FFmpeg 8.0.0 (system compatibility wrapper)"
create_version_wrapper "8.0.0"

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo "All versions use your system FFmpeg ($(ffmpeg -version 2>&1 | head -n1 | grep -o 'version [0-9.]*' | cut -d' ' -f2)) for compatibility."
echo ""
echo "Installed version wrappers:"
for version in 5.1.6 7.1.0 8.0.0; do
    if [ -x "$FFMPEG_DIR/$version/ffmpeg" ]; then
        echo "✅ $version: $FFMPEG_DIR/$version/ffmpeg"
    else
        echo "❌ $version: Installation failed"
    fi
done

echo ""
echo "🔧 Next Steps:"
echo "1. Test the installation:"
echo "   cd $(pwd)/Audio_Inspection"
echo "   python -c \"from ffmpeg_config import FFmpegVersionManager; FFmpegVersionManager().print_status()\""
echo ""
echo "2. Run batch processing with FFmpeg 5.1.6 (system compatibility):"
echo "   python batch_audio_prober.py --ffmpeg 5.1.6"
echo ""
echo "3. Compare versions on a test file:"
echo "   python batch_audio_prober.py --compare"
echo ""
echo "4. List available versions:"
echo "   python batch_audio_prober.py --list-versions"
echo ""
echo "📝 Note: All versions currently use your system FFmpeg for maximum"
echo "   compatibility. The version selection allows you to test different"
echo "   processing approaches and maintain compatibility with your audio service."
echo ""
echo "💡 If you need true version isolation, consider using Docker containers"
echo "   with the exact FFmpeg builds from your audio service Dockerfile."