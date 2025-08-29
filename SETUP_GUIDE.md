# Audio Tools Setup Guide

Complete setup guide for the FFmpeg Version Management system for audio corruption analysis.

## 🎯 Overview

This system provides **true FFmpeg version isolation** using Docker containers, allowing you to:
- Use **actual FFmpeg 5.1.6** (for audio service compatibility)
- Compare corruption detection across **different FFmpeg versions** (5.1.6, 7.1.0, 8.0.0)
- Process audio files with **version-specific behavior**

## 📋 Prerequisites

### Required Software

1. **Python 3.9+** (Recommended: Python 3.11)
   ```bash
   # Check your Python version
   python3 --version
   ```

2. **Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Verify installation:
   ```bash
   docker --version
   docker info
   ```

3. **Git** (for cloning the repository)
   ```bash
   # Check if git is installed
   git --version
   ```

### System Requirements
- **macOS** (tested on macOS 14+)
- **8GB+ RAM** (for Docker containers)
- **5GB+ free disk space** (for Docker images)

## 🚀 Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd audio-tools

# Switch to the FFmpeg version management branch
git checkout feature/ffmpeg-version-management
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Build FFmpeg Docker Images

This step creates **actual different FFmpeg versions** in isolated Docker containers:

```bash
# Make the build script executable
chmod +x build_ffmpeg_docker.sh

# Build all FFmpeg versions (this takes 10-15 minutes)
./build_ffmpeg_docker.sh
```

**Expected output:**
```
🐳 Building FFmpeg Docker Images for Version Isolation
======================================================
🔨 Building FFmpeg 5.1.6 (system compatibility)...
🔨 Building FFmpeg 7.1.0...
🔨 Building FFmpeg 8.0.0...
✅ All FFmpeg Docker images built successfully!

FFmpeg 5.1.6:
ffmpeg version 5.1.6 Copyright (c) 2000-2024 the FFmpeg developers
FFmpeg 7.1.0:
ffmpeg version 7.1 Copyright (c) 2000-2024 the FFmpeg developers
FFmpeg 8.0.0:
ffmpeg version 8.0 Copyright (c) 2000-2025 the FFmpeg developers
```

### Step 4: Verify Installation

```bash
# Navigate to Audio_Inspection directory
cd Audio_Inspection

# Check available FFmpeg versions
python -c "from ffmpeg_config import FFmpegVersionManager; FFmpegVersionManager().print_status()"
```

**Expected output:**
```
============================================================
FFMPEG VERSION MANAGER STATUS
============================================================
Preferred Version: 5.1.6
Default Version: 5.1.6

Available Versions: 5
----------------------------------------
✅ 5.1.6      | 5.1.6           | docker_ffmpeg_5.1.6 (Docker)
✅ 7.1.0      | 7.1             | docker_ffmpeg_7.1.0 (Docker)
✅ 8.0.0      | 8.0             | docker_ffmpeg_8.0.0 (Docker)
✅ system     | 7.1             | ffmpeg (Native)
✅ homebrew   | 7.1             | /opt/homebrew/bin/ffmpeg (Native)
----------------------------------------
🎯 Best Available: 5.1.6
============================================================
```

### Step 5: Test with Sample Audio

```bash
# List available command options
python batch_audio_prober.py --help

# Test with default version (FFmpeg 5.1.6)
python batch_audio_prober.py

# Test with specific version
python batch_audio_prober.py --ffmpeg 7.1.0

# Compare all versions on test files
python batch_audio_prober.py --compare
```

## 📁 Directory Structure

After setup, your directory structure should look like:

```
audio-tools/
├── Audio_Inspection/           # Main analysis tools
│   ├── Audio/                  # Place your audio files here
│   ├── Batch_Probe_Reports/    # Generated CSV reports
│   ├── ffmpeg_config.py        # Version management
│   ├── audio_service_prober.py # Core probing logic
│   ├── batch_audio_prober.py   # Batch processing
│   └── README.md               # Tool documentation
├── docker/                     # Docker configurations
│   ├── ffmpeg-5.1.6/
│   ├── ffmpeg-7.1.0/
│   └── ffmpeg-8.0.0/
├── build_ffmpeg_docker.sh      # Docker build script
├── requirements.txt            # Python dependencies
└── SETUP_GUIDE.md             # This file
```

## 🎵 Usage Examples

### Basic Usage

```bash
# Process audio files with default FFmpeg 5.1.6
python batch_audio_prober.py

# Use specific FFmpeg version
python batch_audio_prober.py --ffmpeg 8.0.0

# List all available versions
python batch_audio_prober.py --list-versions
```

### Audio File Placement

1. **For individual files:**
   ```
   Audio_Inspection/Audio/
   ├── song1.mp3
   ├── podcast.flac
   └── audio_sample.wav
   ```

2. **For organized collections:**
   ```
   Audio_Inspection/Audio/
   ├── album_collection/
   │   ├── track01.mp3
   │   └── track02.mp3
   └── podcast_series/
       ├── episode01.mp3
       └── episode02.mp3
   ```

### Output Reports

Reports are saved in `Batch_Probe_Reports/` with version-specific naming:

```
Batch_Probe_Reports/
├── album_collection_ffmpeg5.1.6_probe_report.csv
├── podcast_series_ffmpeg7.1.0_probe_report.csv
└── individual_files_ffmpeg8.0.0_probe_report.csv
```

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Disable Docker and use native FFmpeg only
export FFMPEG_USE_DOCKER=false

# Set preferred version
export FFMPEG_PREFERRED_VERSION=7.1.0
```

### Programmatic Usage

```python
from ffmpeg_config import FFmpegConfig
from audio_service_prober import ProbeData

# Use specific version
config = FFmpegConfig.for_version("5.1.6")
probe = ProbeData.generate("audio_file.mp3", "5.1.6")

# Compare versions
results = ProbeData.compare_versions("audio_file.mp3")
```

## 🐛 Troubleshooting

### Common Issues

**1. Docker not running**
```
Error: Docker is not running
Solution: Start Docker Desktop application
```

**2. Permission denied**
```bash
# Fix permissions for scripts
chmod +x build_ffmpeg_docker.sh
chmod +x install_ffmpeg_versions.sh
```

**3. Python module not found**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**4. Docker build fails**
```bash
# Clean Docker and rebuild
docker system prune -f
./build_ffmpeg_docker.sh
```

**5. No audio files found**
- Ensure audio files are in `Audio_Inspection/Audio/` directory
- Check file extensions: `.mp3`, `.flac`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.wma`

### Getting Help

```bash
# Check system status
python -c "from ffmpeg_config import FFmpegVersionManager; FFmpegVersionManager().print_status()"

# Validate Docker images
docker images | grep ffmpeg

# Test specific version
docker run --rm ffmpeg:5.1.6 -version
```

## 🎯 Key Benefits

### True Version Isolation
- **FFmpeg 5.1.6**: Matches your audio service environment
- **FFmpeg 7.1.0**: Modern version for comparison
- **FFmpeg 8.0.0**: Latest features and improvements

### Corruption Analysis
Different FFmpeg versions may:
- Detect different corruption patterns
- Handle malformed files differently
- Provide varying levels of diagnostic detail
- Have different error tolerance thresholds

### Reproducible Results
- Consistent behavior across different machines
- Version-locked processing for reliable analysis
- Docker isolation prevents system dependency conflicts

## 📊 Output Analysis

### CSV Report Columns

| Column | Description |
|--------|-------------|
| `file_path` | Relative path to audio file |
| `status` | Processing result (Success/Error/File Not Found) |
| `bitrate` | Audio bitrate in kbps |
| `channels` | Number of audio channels |
| `duration` | Audio duration in seconds |
| `format_name` | Audio format (mp3, flac, etc.) |
| `mime_type` | MIME type |
| `warnings` | Corruption/quality warnings |
| `ffmpeg_version` | Actual FFmpeg version used |
| `ffmpeg_identifier` | Version identifier (5.1.6, 7.1.0, 8.0.0) |
| `file_size_bytes` | File size |
| `probe_raw_output` | Full FFmpeg output for debugging |

### Warning Analysis

Look for these corruption indicators:
- `detected only with low score`
- `misdetection possible`
- `Invalid data found`
- `corrupt`
- `Truncating packet`
- `Header missing`

## 🔄 Updates and Maintenance

### Updating the System

```bash
# Pull latest changes
git pull origin feature/ffmpeg-version-management

# Rebuild Docker images if needed
./build_ffmpeg_docker.sh

# Update Python dependencies
pip install -r requirements.txt --upgrade
```

### Cleaning Up

```bash
# Remove Docker images to free space
docker rmi ffmpeg:5.1.6 ffmpeg:7.1.0 ffmpeg:8.0.0

# Clean Docker system
docker system prune -f
```

---

## 🎉 You're Ready!

Your system now provides **true FFmpeg version isolation** for accurate audio corruption analysis. The default configuration uses FFmpeg 5.1.6 for maximum compatibility with your audio service environment.

**Next Steps:**
1. Place audio files in `Audio_Inspection/Audio/`
2. Run `python batch_audio_prober.py`
3. Analyze the generated CSV reports
4. Compare results across different FFmpeg versions for comprehensive corruption detection
