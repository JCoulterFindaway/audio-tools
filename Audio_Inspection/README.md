# Audio Inspection Tools

A comprehensive toolkit for audio file analysis and metadata extraction using ffmpeg. This module provides both single-file and batch processing capabilities with detailed metadata extraction and CSV reporting.

## Features

🎵 **Advanced Audio Probing** - Extract detailed metadata from audio files  
📊 **Batch Processing** - Process entire directories of audio files automatically  
📈 **CSV Reporting** - Export comprehensive analysis results to structured CSV files  
🔧 **Multi-format Support** - Works with MP3, FLAC, WAV, M4A, AAC, OGG, and WMA files  
⚡ **Robust Error Handling** - Multiple probing strategies with fallback mechanisms  
⚠️ **Warning Detection** - Identifies problematic files with format issues or corruption  
📁 **Organized Workflow** - Clean folder structure for input and output management

## Project Structure

```
Audio_Inspection/
├── Audio/                          # Input: Place your audio folders here
│   ├── podcast_collection/         # Example audio folder
│   └── music_album/                # Another example folder
├── Batch_Probe_Reports/            # Output: Generated CSV reports
├── audio_service_prober.py         # Core single-file probing engine
├── batch_audio_prober.py           # Batch processing tool
└── README.md                       # This file
```

## Prerequisites

### System Requirements

- **Python 3.9+** (Recommended: Python 3.11)
- **ffmpeg** - Required for audio analysis

### Install ffmpeg

```bash
# macOS (using Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

## Installation & Setup

### 1. Navigate to Audio_Inspection

```bash
# If you cloned the full audio-tools repository
cd audio-tools/Audio_Inspection

# Or if you're working directly with the Audio_Inspection module
cd Audio_Inspection
```

### 2. Create Virtual Environment

```bash
# Create virtual environment in the parent directory (use latest Python version)
python -m venv ../venv

# Activate virtual environment
# On macOS/Linux:
source ../venv/bin/activate

# On Windows:
..\\venv\\Scripts\\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r ../requirements.txt
```

### 4. Verify Directory Structure

The Audio_Inspection directory should already contain:
```bash
# These directories should already exist:
# Audio/                 - Place your audio files here
# Batch_Probe_Reports/   - CSV reports will be generated here
```

## Usage

### Running the Scripts

You can run the audio inspection tools in several ways:

```bash
# Method 1: Direct script execution (from Audio_Inspection directory)
python batch_audio_prober.py

# Method 2: As Python module (works from any directory)
python -m batch_audio_prober

# Note: audio_service_prober.py is a library, not a command-line tool
# Use it programmatically in your Python code (see examples below)
```

### Batch Processing (Recommended)

The batch processor works with both **multiple files** and **single files**:

#### For Multiple Files (Folders)
Place audio folders in the `Audio/` directory:

```
Audio/
├── my_podcast_episodes/
│   ├── episode001.mp3
│   ├── episode002.mp3
│   └── ...
└── music_collection/
    ├── track01.flac
    ├── track02.flac
    └── ...
```

#### For Single Files
Place individual audio files directly in the `Audio/` directory:

```
Audio/
├── my_song.mp3
├── podcast_episode.flac
└── audio_sample.wav
```

#### Running the Processor

```bash
# From Audio_Inspection directory (recommended)
python batch_audio_prober.py

# Or as a module (from any directory)
python -m batch_audio_prober
```
These commands will process any file or folder in the `Audio` folder and a report(s) will be generated.
Reports are named based on a folder name if audio is in a folder. 
Multiple folders of audio can be processed at once.
Single or individual files will generate a report named "individual_files_ffmpeg_probe_report.csv"

#### Output Reports

**Folders** → Named CSV files:
```
Batch_Probe_Reports/
├── my_podcast_episodes_ffmpeg_probe_report.csv
└── music_collection_ffmpeg_probe_report.csv
```

**Individual files** → Combined CSV file:
```
Batch_Probe_Reports/
└── individual_files_ffmpeg_probe_report.csv
```

### Single File Analysis

For analyzing individual files (run from Audio_Inspection directory):

```python
from audio_service_prober import ProbeData

# Analyze a single file
probe = ProbeData.generate('Audio/your_file.mp3')
print(probe.to_json())

# Access specific metadata
print(f"Bitrate: {probe.bitrate} kbps")
print(f"Duration: {probe.duration} seconds")
print(f"Channels: {probe.channels}")
print(f"Format: {probe.format_name}")
```

### Custom Batch Processing

For programmatic batch processing (run from Audio_Inspection directory):

```python
from batch_audio_prober import BatchAudioProber

# Process a specific folder
processor = BatchAudioProber("Audio/my_audio_folder")
processor.process_batch(show_progress=True)
processor.export_to_csv()
processor.print_summary()

# Custom output location
processor = BatchAudioProber(
    "Audio/my_audio_folder", 
    "Batch_Probe_Reports/my_custom_report.csv"
)
```

## Metadata Extracted

The tools extract comprehensive metadata for each audio file:

| Field | Description |
|-------|-------------|
| **file_path** | Relative path to the audio file |
| **status** | Processing status (Success/Error/File Not Found) |
| **bitrate** | Audio bitrate in kbps |
| **channels** | Number of audio channels (1=mono, 2=stereo) |
| **duration** | Audio duration in seconds |
| **format_name** | Audio format (mp3, flac, m4a, etc.) |
| **mime_type** | MIME type (audio/mp3, audio/flac, etc.) |
| **warnings** | ⚠️ **NEW** - Detection warnings (low quality, corruption, format issues) |
| **file_size_bytes** | File size in bytes |
| **error_message** | Error details if processing failed |
| **absolute_path** | Full system path to the file |
| **probe_raw_output** | Raw ffmpeg output for troubleshooting |

## Advanced Features

### Error Handling & Quality Detection
- **Multi-stage probing**: Falls back through different strategies if initial probe fails
- **Format detection**: Automatically detects and handles different audio formats
- **Warning detection**: Identifies files with low detection scores, corruption, or format issues
- **Graceful degradation**: Continues processing other files even if some fail

### Processing Statistics
- **Summary reports**: Total files, success rate, error analysis
- **Duration totals**: Sum of all processed audio duration
- **Format breakdown**: List of audio formats found
- **Average metrics**: Mean bitrate across successful files

### Output Customization
- **Auto-naming**: Output files automatically named based on input folder
- **Organized structure**: Reports saved in dedicated `Batch_Probe_Reports/` directory
- **CSV format**: Easy to import into Excel, Google Sheets, or data analysis tools

## Examples

### Example Output CSV

```csv
file_path,status,bitrate,channels,duration,format_name,mime_type,warnings,file_size_bytes
episode001.mp3,Success,128,2,1854.32,mp3,audio/mp3,,29669120
episode002.mp3,Success,128,2,2145.67,mp3,audio/mp3,,34330752
problematic.mp3,Success,192,1,11.39,mp3,audio/mp3,"Format mp3 detected only with low score of 24, misdetection possible!",1322828
damaged_file.mp3,Error,,,,,,,"Input/output error"
```

### Example Summary Output

```
==================================================
BATCH PROCESSING SUMMARY
==================================================
Total files processed: 50
Successful: 48
Errors: 2
File not found: 0
Total audio duration: 05:23:45
Average bitrate: 156.3 kbps
Audio formats found: flac, mp3, m4a
==================================================
```

## Troubleshooting

### Common Issues

**"ffmpeg not found"**
- Install ffmpeg using the instructions in the Prerequisites section
- Ensure ffmpeg is in your system PATH

**"ModuleNotFoundError: No module named 'pandas'"**
- Activate your virtual environment: `source ../venv/bin/activate`
- Install dependencies: `pip install -r ../requirements.txt`

**"No audio files found"**
- Ensure your audio folders are placed in the `Audio/` directory (within Audio_Inspection)
- Check that files have supported extensions (.mp3, .flac, .wav, .m4a, .aac, .ogg, .wma)
- Make sure you're running the command from the Audio_Inspection directory
- If using `python -m batch_audio_prober`, ensure you're in the parent directory of Audio_Inspection

**Files with warnings**
- ⚠️ **Low detection score warnings**: May indicate corrupted headers or non-standard encoding
- **"misdetection possible!"**: Consider re-encoding from original source if available
- **Multiple warnings**: Files with warnings may cause issues in downstream processing
- **Quality assessment**: Use warnings column to identify files that need manual review

**Permission errors**
- Check file permissions on audio files
- Ensure write permissions for the `Batch_Probe_Reports/` directory

### Debug Mode

For detailed error information, you can examine the `probe_raw_output` column in the CSV reports, which contains the full ffmpeg output for troubleshooting.

## Dependencies

- **pandas** - Data manipulation and CSV export
- **pathlib** - Modern path handling (included in Python 3.4+)

## Development

### Project Architecture

- **`audio_service_prober.py`** - Core audio probing logic with multiple fallback strategies
- **`batch_audio_prober.py`** - Batch processing orchestration and CSV export
- **Single Responsibility Principle** - Each module has a focused purpose
- **Open/Closed Principle** - Extensible without modifying existing code

### Adding New Features

1. **New audio formats**: Add to `SUPPORTED_EXTENSIONS` in `BatchAudioProber`
2. **Additional metadata**: Extend regex patterns in `BaseProbe.rexes`
3. **Custom output formats**: Inherit from `BatchAudioProber` and override export methods

## License

[Add your license information here]

## Contributing

[Add contributing guidelines here]

---

**Happy audio analyzing! 🎵**