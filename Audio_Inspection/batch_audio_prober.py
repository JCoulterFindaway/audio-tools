#!/usr/bin/env python3
"""
Batch Audio Prober with FFmpeg Version Management

Enhanced batch processing tool that supports multiple ffmpeg versions
for comprehensive corruption diagnosis and analysis.
"""

import os
import pandas as pd
from typing import List, Dict
from pathlib import Path
import argparse

from audio_service_prober import ProbeData
from ffmpeg_config import FFmpegConfig, FFmpegVersionManager


class BatchAudioProber:
    """
    Batch processor for audio files with ffmpeg version management.
    
    Supports processing with specific ffmpeg versions for enhanced
    corruption detection and analysis.
    """
    
    # Supported audio file extensions
    SUPPORTED_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.ogg', '.wav', '.aac', '.wma'}

    def __init__(self, data_folder: str, output_file: str = None, 
                 ffmpeg_version: str = None):
        """
        Initialize the batch prober with optional ffmpeg version.

        Args:
            data_folder: Path to the folder containing audio files
            output_file: Output CSV file path. If None, auto-generates based 
                        on input folder name in Batch_Probe_Reports directory
            ffmpeg_version: Specific ffmpeg version to use. Uses default if None.
        """
        self.data_folder = Path(data_folder)
        
        # Initialize ffmpeg configuration
        if ffmpeg_version:
            self.ffmpeg_config = FFmpegConfig.for_version(ffmpeg_version)
        else:
            self.ffmpeg_config = FFmpegConfig.default()
        
        print(f"Using {self.ffmpeg_config}")
        
        # Auto-generate output filename if not provided
        if output_file is None:
            self.output_file = self._generate_output_filename()
        else:
            self.output_file = output_file
            
        self.results: List[Dict] = []

        # Validate input folder
        if not self.data_folder.exists():
            raise FileNotFoundError(
                f"Data folder does not exist: {self.data_folder}")

        if not self.data_folder.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {self.data_folder}")
                
        # Ensure output directory exists
        self._ensure_output_directory()
    
    def _generate_output_filename(self) -> str:
        """
        Generate output filename based on input folder name and ffmpeg version.
        
        Returns:
            String path to output CSV file in Batch_Probe_Reports directory
        """
        # Get the name of the input folder
        folder_name = self.data_folder.name
        
        # Include ffmpeg version in filename for clarity
        version_suffix = f"_ffmpeg{self.ffmpeg_config.version}"
        csv_filename = f"{folder_name}{version_suffix}_probe_report.csv"
        
        # Create full path in Batch_Probe_Reports directory
        output_dir = Path(os.getcwd()) / "Batch_Probe_Reports"
        return str(output_dir / csv_filename)
    
    def _ensure_output_directory(self) -> None:
        """
        Ensure the output directory exists, create if it doesn't.
        """
        output_path = Path(self.output_file)
        output_dir = output_path.parent
        
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created output directory: {output_dir}")
    
    def find_audio_files(self) -> List[Path]:
        """
        Recursively find all audio files in the data folder.

        Returns:
            List of Path objects for audio files
        """
        audio_files = []

        for root, _, files in os.walk(self.data_folder):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    audio_files.append(file_path)

        return sorted(audio_files)
    
    def process_file(self, file_path: Path) -> Dict:
        """
        Process a single audio file and extract metadata using configured ffmpeg version.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary containing file metadata and processing results
        """
        relative_path = file_path.relative_to(self.data_folder)

        result = {
            'file_path': str(relative_path),
            'absolute_path': str(file_path),
            'file_size_bytes': None,
            'status': None,
            'error_message': None,
            'bitrate': None,
            'channels': None,
            'duration': None,
            'format_name': None,
            'mime_type': None,
            'warnings': None,
            'ffmpeg_version': None,
            'ffmpeg_identifier': None,
            'probe_raw_output': None
        }

        try:
            # Get file size
            result['file_size_bytes'] = file_path.stat().st_size

            # Probe the file using the configured ffmpeg version
            probe = ProbeData.generate(str(file_path), self.ffmpeg_config.version)

            # Extract metadata
            probe_dict = probe.to_dict()
            
            # Format warnings as a readable string
            warnings = probe_dict.get('warnings', [])
            warnings_str = "; ".join(warnings) if warnings else None
            
            result.update({
                'status': 'Success',
                'bitrate': probe_dict.get('bitrate'),
                'channels': probe_dict.get('channels'),
                'duration': probe_dict.get('duration'),
                'format_name': probe_dict.get('format_name'),
                'mime_type': probe_dict.get('mime_type'),
                'warnings': warnings_str,
                'ffmpeg_version': probe_dict.get('ffmpeg_version'),
                'ffmpeg_identifier': probe_dict.get('ffmpeg_identifier'),
                'probe_raw_output': probe_dict.get('raw')
            })

        except FileNotFoundError:
            result['status'] = 'File Not Found'
            result['error_message'] = 'File does not exist'

        except Exception as e:
            result['status'] = 'Error'
            result['error_message'] = str(e)

        return result
    
    def process_batch(self, show_progress: bool = True) -> None:
        """
        Process all audio files in the data folder.

        Args:
            show_progress: Whether to display progress information
        """
        audio_files = self.find_audio_files()

        if not audio_files:
            print(f"No audio files found in {self.data_folder}")
            return

        if show_progress:
            print(f"Found {len(audio_files)} audio files to process")
            print(f"Processing files in: {self.data_folder}")
            print(f"Using FFmpeg: {self.ffmpeg_config}")
            print("-" * 60)

        self.results = []

        for i, file_path in enumerate(audio_files, 1):
            if show_progress:
                rel_path = file_path.relative_to(self.data_folder)
                print(f"[{i:3d}/{len(audio_files)}] Processing: {rel_path}")

            result = self.process_file(file_path)
            self.results.append(result)

        if show_progress:
            print("-" * 60)
            files_processed = len(self.results)
            print(f"Batch processing complete. "
                  f"Processed {files_processed} files.")
    
    def export_to_csv(self) -> None:
        """
        Export the processing results to a CSV file.
        """
        if not self.results:
            print("No results to export. Run process_batch() first.")
            return

        # Create DataFrame
        df = pd.DataFrame(self.results)

        # Reorder columns for better readability (including new ffmpeg columns)
        column_order = [
            'file_path', 'status', 'bitrate', 'channels', 'duration',
            'format_name', 'mime_type', 'warnings', 'file_size_bytes',
            'ffmpeg_version', 'ffmpeg_identifier', 'error_message', 
            'absolute_path', 'probe_raw_output'
        ]

        # Only include columns that exist in the DataFrame
        available_columns = [col for col in column_order
                             if col in df.columns]
        df = df[available_columns]

        # Export to CSV
        df.to_csv(self.output_file, index=False)
        print(f"Results exported to: {self.output_file}")
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the batch processing results.

        Returns:
            Dictionary containing processing statistics
        """
        if not self.results:
            return {"error": "No results available. "
                             "Run process_batch() first."}

        df = pd.DataFrame(self.results)

        summary = {
            'total_files': len(self.results),
            'successful': len(df[df['status'] == 'Success']),
            'errors': len(df[df['status'] == 'Error']),
            'file_not_found': len(df[df['status'] == 'File Not Found']),
            'total_duration_seconds': None,
            'avg_bitrate': None,
            'formats_found': [],
            'ffmpeg_version': self.ffmpeg_config.get_version_info().get('version', 'unknown'),
            'ffmpeg_identifier': self.ffmpeg_config.version,
            'warnings_detected': 0,
        }

        # Calculate additional statistics for successful files
        successful_files = df[df['status'] == 'Success']

        if not successful_files.empty:
            # Count files with warnings
            files_with_warnings = successful_files[successful_files['warnings'].notna()]
            summary['warnings_detected'] = len(files_with_warnings)
            
            # Total duration (convert string durations to float)
            durations = successful_files['duration'].dropna()
            if not durations.empty:
                try:
                    duration_values = [float(d) for d in durations
                                       if d is not None]
                    summary['total_duration_seconds'] = sum(duration_values)
                except (ValueError, TypeError):
                    pass

            # Average bitrate
            bitrates = successful_files['bitrate'].dropna()
            if not bitrates.empty:
                summary['avg_bitrate'] = bitrates.mean()

            # Unique formats found
            formats = successful_files['format_name'].dropna().unique()
            summary['formats_found'] = sorted(formats.tolist())

        return summary
    
    def print_summary(self) -> None:
        """
        Print a formatted summary of the batch processing results.
        """
        summary = self.get_summary()

        if 'error' in summary:
            print(summary['error'])
            return

        print("\n" + "=" * 50)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 50)
        print(f"FFmpeg Version: {summary['ffmpeg_version']} ({summary['ffmpeg_identifier']})")
        print(f"Total files processed: {summary['total_files']}")
        print(f"Successful: {summary['successful']}")
        print(f"Errors: {summary['errors']}")
        print(f"File not found: {summary['file_not_found']}")
        print(f"Files with warnings: {summary['warnings_detected']}")

        if summary['total_duration_seconds']:
            hours = int(summary['total_duration_seconds'] // 3600)
            minutes = int((summary['total_duration_seconds'] % 3600) // 60)
            seconds = int(summary['total_duration_seconds'] % 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"Total audio duration: {duration_str}")

        if summary['avg_bitrate']:
            print(f"Average bitrate: {summary['avg_bitrate']:.1f} kbps")

        if summary['formats_found']:
            formats_str = ', '.join(summary['formats_found'])
            print(f"Audio formats found: {formats_str}")

        print("=" * 50)


def main():
    """
    Enhanced main function with command-line argument support for ffmpeg version selection.
    """
    parser = argparse.ArgumentParser(
        description="Batch Audio Prober with FFmpeg Version Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_audio_prober.py                    # Use default ffmpeg version
  python batch_audio_prober.py --ffmpeg 5.1.6    # Use specific version
  python batch_audio_prober.py --list-versions    # Show available versions
  python batch_audio_prober.py --compare          # Compare all versions (first file only)
        """
    )
    
    parser.add_argument(
        '--ffmpeg', '--ffmpeg-version',
        dest='ffmpeg_version',
        help='FFmpeg version to use (e.g., 5.1.6, 7.1.0, 8.0.0, system)'
    )
    
    parser.add_argument(
        '--list-versions',
        action='store_true',
        help='List available FFmpeg versions and exit'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare results across all available FFmpeg versions (uses first audio file found)'
    )
    
    args = parser.parse_args()
    
    # Handle version listing
    if args.list_versions:
        manager = FFmpegVersionManager()
        manager.print_status()
        return
    audio_base_dir = Path(os.getcwd()) / "Audio"
    
    if not audio_base_dir.exists():
        print(f"Error: Audio directory not found at {audio_base_dir}")
        print("Please create an 'Audio' directory and add your audio "
              "files or folders there.")
        return
    
    # Handle comparison mode
    if args.compare:
        # Find first audio file for comparison
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}
        test_file = None
        
        for item in audio_base_dir.rglob('*'):
            if item.is_file() and item.suffix.lower() in audio_extensions:
                test_file = item
                break
        
        if not test_file:
            print("No audio files found for comparison.")
            return
        
        print(f"Comparing FFmpeg versions using: {test_file.name}")
        print("=" * 60)
        
        comparison = ProbeData.compare_versions(str(test_file))
        
        for version, result in comparison.items():
            status = "✅" if result['status'] == 'success' else "❌"
            warnings = result.get('warnings_count', 0)
            print(f"{status} {version:10} | Status: {result['status']:8} | Warnings: {warnings}")
            
            if result['status'] == 'error':
                print(f"   └─ Error: {result.get('error', 'Unknown error')}")
        
        return
    
    # Find both subdirectories and individual audio files
    audio_folders = [d for d in audio_base_dir.iterdir()
                     if d.is_dir() and not d.name.startswith('.')]
    
    # Common audio file extensions
    audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}
    individual_files = [f for f in audio_base_dir.iterdir()
                       if f.is_file() and f.suffix.lower() in audio_extensions]
    
    if not audio_folders and not individual_files:
        print(f"No audio folders or files found in {audio_base_dir}")
        print("Please add folders or audio files to the Audio directory.")
        return
    
    total_items = len(audio_folders) + (1 if individual_files else 0)
    
    # Show ffmpeg version being used
    try:
        if args.ffmpeg_version:
            config = FFmpegConfig.for_version(args.ffmpeg_version)
        else:
            config = FFmpegConfig.default()
        
        print(f"Using {config}")
        version_info = config.get_version_info()
        print(f"FFmpeg Version: {version_info.get('version', 'unknown')}")
        print()
    except Exception as e:
        print(f"Error with FFmpeg configuration: {e}")
        return
    
    print(f"Found {total_items} item(s) to process:")
    
    # Show what we found
    for folder in audio_folders:
        print(f"  📁 {folder.name}/ (folder)")
    
    if individual_files:
        print(f"  🎵 {len(individual_files)} individual file(s)")
        for file in individual_files[:3]:  # Show first 3
            print(f"     - {file.name}")
        if len(individual_files) > 3:
            print(f"     ... and {len(individual_files) - 3} more")
    
    print("-" * 60)
    
    # Process folders first
    for folder in audio_folders:
        print(f"\n📁 Processing folder: {folder.name}")
        print("=" * 50)
        
        try:
            processor = BatchAudioProber(str(folder), ffmpeg_version=args.ffmpeg_version)
            print(f"Output will be saved to: {processor.output_file}")
            
            processor.process_batch(show_progress=True)
            processor.export_to_csv()
            processor.print_summary()

        except (FileNotFoundError, NotADirectoryError) as e:
            print(f"Error processing {folder.name}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {folder.name}: {e}")
    
    # Process individual files if any exist
    if individual_files:
        print(f"\n🎵 Processing {len(individual_files)} individual file(s)")
        print("=" * 50)
        
        try:
            # Create a temporary "virtual folder" for individual files
            processor = BatchAudioProber(str(audio_base_dir), ffmpeg_version=args.ffmpeg_version)
            
            # Override the output filename for individual files
            reports_dir = Path(os.getcwd()) / 'Batch_Probe_Reports'
            version_suffix = f"_ffmpeg{processor.ffmpeg_config.version}"
            processor.output_file = str(reports_dir / f'individual_files{version_suffix}_probe_report.csv')
            
            print(f"Output will be saved to: {processor.output_file}")
            
            # Process only the individual files (not subdirectories)
            results = []
            print(f"Found {len(individual_files)} audio file(s) to process")
            print(f"Processing files in: {audio_base_dir}")
            print("-" * 60)
            
            for i, file_path in enumerate(individual_files, 1):
                print(f"[{i:3d}/{len(individual_files):3d}] Processing: {file_path.name}")
                try:
                    result = processor.process_file(file_path)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")
            
            # Store results and export
            processor.results = results
            processor.export_to_csv()
            processor.print_summary()

        except Exception as e:
            print(f"Unexpected error processing individual files: {e}")
    
    print("\n✅ Batch processing complete!")
    reports_dir = Path(os.getcwd()) / 'Batch_Probe_Reports'
    print(f"📁 Reports saved in: {reports_dir}")


if __name__ == '__main__':
    main()
