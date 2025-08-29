#!/bin/bash

# Quick Setup Script for Audio Tools FFmpeg Version Management
# Automates the complete installation process

set -e

echo "🎵 Audio Tools - FFmpeg Version Management Setup"
echo "================================================="
echo "This script will set up true FFmpeg version isolation for audio corruption analysis."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ and try again."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $python_version found"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop and try again."
        print_error "Download from: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
    
    print_success "Docker is running"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git and try again."
        exit 1
    fi
    
    print_success "Git found"
}

# Set up Python environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Build Docker images
build_docker_images() {
    print_status "Building FFmpeg Docker images (this may take 10-15 minutes)..."
    
    if [ ! -f "build_ffmpeg_docker.sh" ]; then
        print_error "build_ffmpeg_docker.sh not found. Are you in the correct directory?"
        exit 1
    fi
    
    chmod +x build_ffmpeg_docker.sh
    
    if ./build_ffmpeg_docker.sh; then
        print_success "All FFmpeg Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    cd Audio_Inspection
    
    # Test Python imports
    if python -c "from ffmpeg_config import FFmpegVersionManager; from audio_service_prober import ProbeData; from batch_audio_prober import BatchAudioProber" 2>/dev/null; then
        print_success "Python modules imported successfully"
    else
        print_error "Failed to import Python modules"
        exit 1
    fi
    
    # Test FFmpeg versions
    print_status "Checking available FFmpeg versions..."
    python -c "from ffmpeg_config import FFmpegVersionManager; FFmpegVersionManager().print_status()"
    
    cd ..
}

# Create sample directory structure
setup_directories() {
    print_status "Setting up directory structure..."
    
    # Ensure Audio directory exists
    mkdir -p Audio_Inspection/Audio
    mkdir -p Audio_Inspection/Batch_Probe_Reports
    
    print_success "Directory structure created"
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "build_ffmpeg_docker.sh" ] || [ ! -d "Audio_Inspection" ]; then
        print_error "Please run this script from the audio-tools root directory"
        print_error "Expected files: build_ffmpeg_docker.sh, Audio_Inspection/"
        exit 1
    fi
    
    check_prerequisites
    echo ""
    
    setup_python_env
    echo ""
    
    build_docker_images
    echo ""
    
    setup_directories
    echo ""
    
    verify_installation
    echo ""
    
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Navigate to Audio_Inspection: cd Audio_Inspection"
    echo "3. Place audio files in Audio_Inspection/Audio/"
    echo "4. Run analysis: python batch_audio_prober.py"
    echo ""
    echo "📖 For detailed usage instructions, see SETUP_GUIDE.md"
    echo ""
    echo "🔧 Available commands:"
    echo "  python batch_audio_prober.py                    # Use default FFmpeg 5.1.6"
    echo "  python batch_audio_prober.py --ffmpeg 7.1.0     # Use specific version"
    echo "  python batch_audio_prober.py --list-versions    # Show available versions"
    echo "  python batch_audio_prober.py --compare          # Compare all versions"
}

# Run main function
main "$@"
