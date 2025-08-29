# Legacy Files

This directory contains files that are no longer actively used in the current FFmpeg version management system but are preserved for reference and potential future use.

## 📁 Contents

### Audio Service Scripts
- **`audio_service_client.py`** - Client for interacting with audio services
- **`audio_service_get_metadata.py`** - Metadata retrieval from audio services  
- **`audio_service_remove_playlist.py`** - Playlist management functionality
- **`get_audio_service_status.py`** - Audio service status checking

### Analysis & Processing
- **`check_audio_cohort.py`** - Audio cohort analysis and validation
- **`simple_ffmpeg_probe.py`** - Basic FFmpeg probing (superseded by `audio_service_prober.py`)
- **`onix_opener.py`** - ONIX file format handling

### Installation & Setup
- **`install_ffmpeg_versions.sh`** - Legacy FFmpeg installation script (replaced by Docker-based approach)
- **`TESTING_PLAN.md`** - Original testing documentation

### Test Data & Results
- **`test_output_1.txt`** - Sample test output from earlier development
- **`Testing/`** - Directory containing older test files and audio normalizer tests

## 🔄 Migration Notes

These files were moved to legacy as part of the FFmpeg version management system implementation. The current system uses:

- **Docker-based FFmpeg versions** instead of direct system installations
- **`Audio_Inspection/`** directory for all active analysis tools
- **True version isolation** through containerization

## 🚀 Current System

For active audio analysis, use the files in the main project directory:
- `Audio_Inspection/batch_audio_prober.py` - Main batch processing tool
- `Audio_Inspection/audio_service_prober.py` - Core probing engine  
- `Audio_Inspection/ffmpeg_config.py` - Version management system

## 📋 Restoration

If any of these files are needed again:
1. Copy the file back to the main directory
2. Update imports and dependencies as needed
3. Test compatibility with the current FFmpeg version management system

---

**Note**: These files are preserved for historical reference and potential future integration. They may require updates to work with the current Docker-based FFmpeg system.
