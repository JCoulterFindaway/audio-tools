# Audio Tools - FFmpeg Version Management

**True FFmpeg version isolation for audio corruption analysis**

This system provides **actual different FFmpeg versions** (5.1.6, 7.1.0, 8.0.0) running in Docker containers, enabling accurate audio corruption detection that matches your audio service environment.

## Key Features

- **True Version Isolation**: Actual FFmpeg 5.1.6, 7.1.0, and 8.0.0 in Docker containers
- **Audio Service Compatibility**: Default FFmpeg 5.1.6 matches your production environment
- **Corruption Detection**: Different versions detect different corruption patterns
- **Batch Processing**: Process entire directories with comprehensive CSV reports
- **Version Comparison**: Compare results across multiple FFmpeg versions
- **Warning Detection**: Identifies problematic files with format issues or corruption

## Prerequisites

### Required Software

1. **Python 3.9+** (Recommended: Python 3.11)
   ```bash
   python --version
   ```

2. **Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Verify:
   ```bash
   docker --version
   docker info
   ```

3. **Git**
   ```bash
   git --version
   ```

### System Requirements
- **macOS** (tested on macOS 14+)
- **8GB+ RAM** (for Docker containers)
- **5GB+ free disk space** (for Docker images)

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd audio-tools

# Run automated setup (takes 10-15 minutes)
./quick_setup.sh
```

The script will:
- Check prerequisites
- Create Python virtual environment
- Install dependencies
- Build all FFmpeg Docker images
- Verify installation

### Option 2: Manual Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd audio-tools

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Build FFmpeg Docker images (takes 10-15 minutes)
chmod +x build_ffmpeg_docker.sh
./build_ffmpeg_docker.sh

# 5. Verify installation
cd Audio_Inspection
python -c "from ffmpeg_config import FFmpegVersionManager; FFmpegVersionManager().print_status()"
```

## Usage

Navigate to the `Audio_Inspection` directory before running commands:

```bash
cd Audio_Inspection
```

### Basic Commands

```bash
# Process with default FFmpeg 5.1.6
python batch_audio_prober.py

# Use specific version
python batch_audio_prober.py --ffmpeg 7.1.0
python batch_audio_prober.py --ffmpeg 8.0.0

# Compare all versions on test files
python batch_audio_prober.py --compare

# List available versions
python batch_audio_prober.py --list-versions

# Show help
python batch_audio_prober.py --help
```

### Version Comparison

Different FFmpeg versions may detect different issues:
- **FFmpeg 5.1.6** (Docker): Matches your production audio service environment
- **FFmpeg 7.1.0** (Docker): Modern version for comparison
- **FFmpeg 8.0.0** (Docker): Latest features and improvements

## Audio File Placement

Place your audio files in the `Audio_Inspection/Audio/` directory:

### Individual Files
```
Audio_Inspection/Audio/
├── song1.mp3
├── podcast.flac
└── audio_sample.wav
```

### Organized Collections
```
Audio_Inspection/Audio/
├── album_collection/
│   ├── track01.mp3
│   └── track02.mp3
└── podcast_series/
    ├── episode01.mp3
    └── episode02.mp3
```

**Supported formats**: `.mp3`, `.flac`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.wma`

## Output Reports

Reports are saved in `Audio_Inspection/Batch_Probe_Reports/` with version-specific naming:

```
Batch_Probe_Reports/
├── album_collection_ffmpeg5.1.6_probe_report.csv
├── podcast_series_ffmpeg7.1.0_probe_report.csv
└── individual_files_ffmpeg8.0.0_probe_report.csv
```

### CSV Columns

| Column | Description |
|--------|-------------|
| `file_path` | Relative path to audio file |
| `status` | Processing result (Success/Error/File Not Found) |
| `bitrate` | Audio bitrate in kbps |
| `channels` | Number of audio channels (1=mono, 2=stereo) |
| `duration` | Audio duration in seconds |
| `format_name` | Audio format (mp3, flac, etc.) |
| `mime_type` | MIME type |
| `warnings` | Corruption/quality warnings |
| `ffmpeg_version` | Actual FFmpeg version used |
| `ffmpeg_identifier` | Version identifier (5.1.6, 7.1.0, 8.0.0, system, homebrew) |
| `file_size_bytes` | File size |
| `probe_raw_output` | Full FFmpeg output for debugging |

### Warning Indicators

Look for these corruption indicators in the `warnings` column:
- `detected only with low score`
- `misdetection possible`
- `Invalid data found`
- `corrupt`
- `Truncating packet`
- `Header missing`

## Fallback Behavior

This tool prefers Docker-based FFmpeg versions for true version isolation. However, if Docker images are unavailable, it will fall back to the system-installed FFmpeg.

**How to identify fallback usage in reports:**

If your report shows one of these in the `ffmpeg_identifier` column:
- `system` - Using FFmpeg from your system PATH
- `homebrew` - Using Homebrew-installed FFmpeg (macOS)

...instead of `5.1.6`, `7.1.0`, or `8.0.0`, it means Docker images weren't available and the tool fell back to your system FFmpeg.

**To ensure Docker versions are used:**
1. Verify Docker is running: `docker info`
2. Verify images exist: `docker images | grep ffmpeg`
3. Rebuild if needed: `./build_ffmpeg_docker.sh`

## Programmatic Usage

### Single File Analysis

```python
from audio_service_prober import ProbeData

# Analyze a single file with default version
probe = ProbeData.generate('Audio/your_file.mp3')
print(probe.to_json())

# Use specific version
probe = ProbeData.generate('Audio/your_file.mp3', '7.1.0')

# Access specific metadata
print(f"Bitrate: {probe.bitrate} kbps")
print(f"Duration: {probe.duration} seconds")
print(f"Channels: {probe.channels}")
print(f"Format: {probe.format_name}")
```

### Custom Batch Processing

```python
from batch_audio_prober import BatchAudioProber

# Process a specific folder with default version
processor = BatchAudioProber("Audio/my_audio_folder")
processor.process_batch(show_progress=True)
processor.export_to_csv()
processor.print_summary()

# Use specific FFmpeg version
processor = BatchAudioProber("Audio/my_audio_folder", ffmpeg_version="7.1.0")
```

### Version Comparison

```python
from audio_service_prober import ProbeData

# Compare results across all available versions
comparison = ProbeData.compare_versions("Audio/test_file.mp3")
for version, result in comparison.items():
    print(f"{version}: {result['status']}, warnings: {result.get('warnings_count', 0)}")
```

## Project Structure

```
audio-tools/
├── Audio_Inspection/           # Main analysis tools
│   ├── Audio/                  # Place your audio files here
│   ├── Batch_Probe_Reports/    # Generated CSV reports
│   ├── ffmpeg_config.py        # Version management
│   ├── audio_service_prober.py # Core probing logic
│   └── batch_audio_prober.py   # Batch processing
├── docker/                     # Docker configurations
│   ├── ffmpeg-5.1.6/           # System compatibility version
│   ├── ffmpeg-7.1.0/           # Modern version
│   └── ffmpeg-8.0.0/           # Latest version
├── Archive/                    # Reference implementations
├── build_ffmpeg_docker.sh      # Docker build script
├── quick_setup.sh              # Automated setup script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Troubleshooting

### Docker Issues

**Docker not running**
```bash
# Start Docker Desktop, then verify:
docker info
```

**Docker images missing**
```bash
# Check existing images
docker images | grep ffmpeg

# Rebuild images
./build_ffmpeg_docker.sh
```

**Docker build fails**
```bash
# Clean Docker and rebuild
docker system prune -f
./build_ffmpeg_docker.sh
```

### Python Issues

**ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Permission denied on scripts**
```bash
chmod +x quick_setup.sh
chmod +x build_ffmpeg_docker.sh
```

### Audio Processing Issues

**No audio files found**
- Ensure files are in `Audio_Inspection/Audio/` directory
- Check file extensions: `.mp3`, `.flac`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.wma`

**Files with warnings**
- Low detection score warnings may indicate corrupted headers
- "misdetection possible" suggests non-standard encoding
- Check `probe_raw_output` column for detailed FFmpeg output

### Quick Diagnostics

```bash
# Check system status
cd Audio_Inspection
python -c "from ffmpeg_config import FFmpegVersionManager; FFmpegVersionManager().print_status()"

# Test specific Docker version
docker run --rm ffmpeg:5.1.6 -version
```

## Maintenance

### Updating

```bash
# Pull latest changes
git pull origin main

# Rebuild Docker images if needed
./build_ffmpeg_docker.sh

# Update Python dependencies
pip install -r requirements.txt --upgrade
```

### Cleanup

```bash
# Remove Docker images to free space
docker rmi ffmpeg:5.1.6 ffmpeg:7.1.0 ffmpeg:8.0.0

# Clean Docker system
docker system prune -f
```

---

**Ready to analyze audio corruption with true version isolation!**

Start with: `./quick_setup.sh`
