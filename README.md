# Audio Tools - FFmpeg Version Management

🎵 **True FFmpeg version isolation for audio corruption analysis**

This system provides **actual different FFmpeg versions** (5.1.6, 7.1.0, 8.0.0) running in Docker containers, enabling accurate audio corruption detection that matches your audio service environment.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd audio-tools

# Run automated setup (takes 10-15 minutes)
./quick_setup.sh
```

### Option 2: Manual Setup
Follow the detailed instructions in [`SETUP_GUIDE.md`](SETUP_GUIDE.md)

## 🎯 Key Features

- ✅ **True Version Isolation**: Actual FFmpeg 5.1.6, 7.1.0, and 8.0.0 in Docker containers
- ✅ **Audio Service Compatibility**: Default FFmpeg 5.1.6 matches your production environment  
- ✅ **Corruption Detection**: Different versions detect different corruption patterns
- ✅ **Batch Processing**: Process entire directories with comprehensive CSV reports
- ✅ **Version Comparison**: Compare results across multiple FFmpeg versions

## 📊 Usage Examples

```bash
# Navigate to the analysis tools
cd Audio_Inspection

# Process with default FFmpeg 5.1.6 (system compatibility)
python batch_audio_prober.py

# Use specific version
python batch_audio_prober.py --ffmpeg 7.1.0

# Compare all versions on test files
python batch_audio_prober.py --compare

# List available versions
python batch_audio_prober.py --list-versions
```

## 📁 Project Structure

```
audio-tools/
├── Audio_Inspection/           # 🎵 Main analysis tools
│   ├── Audio/                  # 📂 Place your audio files here
│   ├── Batch_Probe_Reports/    # 📊 Generated CSV reports
│   ├── ffmpeg_config.py        # ⚙️  Version management
│   ├── audio_service_prober.py # 🔍 Core probing logic
│   └── batch_audio_prober.py   # 📦 Batch processing
├── docker/                     # 🐳 Docker configurations
│   ├── ffmpeg-5.1.6/          # 🎯 System compatibility version
│   ├── ffmpeg-7.1.0/          # 🔄 Modern version
│   └── ffmpeg-8.0.0/          # 🚀 Latest version
├── legacy/                     # 📦 Archived files (unused)
│   ├── audio_service_*.py      # 🔗 Audio service clients
│   ├── simple_ffmpeg_probe.py # 📊 Basic probe (superseded)
│   ├── Testing/                # 🧪 Old test files
│   └── README.md               # 📋 Legacy documentation
├── Archive/                    # 🗄️  Reference implementations
├── quick_setup.sh              # ⚡ Automated setup script
├── SETUP_GUIDE.md             # 📖 Detailed setup instructions
└── README.md                  # 📋 This file
```

## 🔍 What Makes This Different

**Before**: All "versions" were just wrappers calling the same FFmpeg  
**Now**: Each version runs in its own Docker container with the actual FFmpeg version

### Version Comparison
- **FFmpeg 5.1.6** (Docker): `built with gcc 11.2.1 (Alpine)` - Your target version
- **FFmpeg 7.1.0** (Docker): `built with gcc 12.2.1 (Alpine)` - Modern comparison
- **FFmpeg 8.0.0** (Docker): `built with gcc 13.2.1 (Alpine)` - Latest features
- **System FFmpeg** (Native): `built with Apple clang` - Fallback option

## 🐛 Troubleshooting

### Quick Fixes
```bash
# Check system status
cd Audio_Inspection
python -c "from ffmpeg_config import FFmpegVersionManager; FFmpegVersionManager().print_status()"

# Verify Docker images
docker images | grep ffmpeg

# Test specific version
docker run --rm ffmpeg:5.1.6 -version
```

### Common Issues
- **Docker not running**: Start Docker Desktop
- **Permission denied**: Run `chmod +x quick_setup.sh`
- **No audio files found**: Place files in `Audio_Inspection/Audio/`

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete installation and usage guide
- **[Audio_Inspection/README.md](Audio_Inspection/README.md)** - Detailed tool documentation

## 🎯 Use Cases

### Audio Corruption Analysis
Different FFmpeg versions may detect:
- Format-specific corruption patterns
- Header inconsistencies  
- Encoding anomalies
- Bitstream errors
- Metadata corruption

### Production Compatibility
- **FFmpeg 5.1.6**: Matches your audio service environment
- **Version comparison**: Identify version-dependent behavior
- **Reproducible results**: Consistent analysis across machines

## 🔄 Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild Docker images if needed
./build_ffmpeg_docker.sh
```

---

**Ready to analyze audio corruption with true version isolation!** 🎵

Start with: `./quick_setup.sh`
