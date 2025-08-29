#!/bin/bash

# Build Docker images for different FFmpeg versions
# This provides TRUE version isolation for audio corruption analysis

set -e

echo "🐳 Building FFmpeg Docker Images for Version Isolation"
echo "======================================================"
echo "This will build actual different FFmpeg versions in Docker containers"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Build FFmpeg 5.1.6 (system compatibility)
echo "🔨 Building FFmpeg 5.1.6 (system compatibility)..."
docker build -t ffmpeg:5.1.6 docker/ffmpeg-5.1.6/ || {
    echo "❌ Failed to build FFmpeg 5.1.6"
    exit 1
}

# Build FFmpeg 7.1.0
echo "🔨 Building FFmpeg 7.1.0..."
docker build -t ffmpeg:7.1.0 docker/ffmpeg-7.1.0/ || {
    echo "❌ Failed to build FFmpeg 7.1.0"
    exit 1
}

# Build FFmpeg 8.0.0
echo "🔨 Building FFmpeg 8.0.0..."
docker build -t ffmpeg:8.0.0 docker/ffmpeg-8.0.0/ || {
    echo "❌ Failed to build FFmpeg 8.0.0"
    exit 1
}

echo ""
echo "✅ All FFmpeg Docker images built successfully!"
echo ""
echo "Available images:"
docker images | grep "ffmpeg"

echo ""
echo "🧪 Testing versions:"
echo "FFmpeg 5.1.6:"
docker run --rm ffmpeg:5.1.6 -version | head -1

echo "FFmpeg 7.1.0:"
docker run --rm ffmpeg:7.1.0 -version | head -1

echo "FFmpeg 8.0.0:"
docker run --rm ffmpeg:8.0.0 -version | head -1

echo ""
echo "🎉 Setup complete! You now have TRUE FFmpeg version isolation."
echo ""
echo "Next steps:"
echo "1. Update your Python scripts to use Docker-based FFmpeg execution"
echo "2. Test audio corruption detection with actual different versions"
