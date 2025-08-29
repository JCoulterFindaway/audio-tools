#!/usr/bin/env python3
"""
Batch Audio Prober

A tool for batch processing audio files using the advanced probing capabilities
from audio_service_prober.py. Processes directories of audio files and exports
detailed metadata to CSV format.

Features:
- Recursive directory traversal
- Advanced metadata extraction (bitrate, channels, duration, format, etc.)
- Robust error handling with multiple probing strategies
- CSV export with comprehensive results
- Progress tracking during batch operations
"""

import os
import pandas as pd
from typing import List, Dict
from pathlib import Path

from audio_service_prober import ProbeData


class BatchAudioProber:
    """
    Batch processor for audio files using the ProbeData class.
    
    Handles directory traversal, batch processing, and CSV export
    of audio metadata while maintaining separation of concerns.
    """
    
    # Supported audio file extensions
    SUPPORTED_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.ogg', '.wav'}

    def __init__(self, data_folder: str, output_file: str = None):
        """
        Initialize the batch prober.

        Args:
            data_folder: Path to the folder containing audio files
            output_file: Output CSV file path. If None, auto-generates based 
                        on input folder name in Batch_Probe_Reports directory
        """
        self.data_folder = Path(data_folder)
        
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
        Generate output filename based on input folder name.
        
        Returns:
            String path to output CSV file in Batch_Probe_Reports directory
        """
        # Get the name of the input folder
        folder_name = self.data_folder.name
        
        # Create filename with the specified format
        csv_filename = f"{folder_name}_ffmpeg_probe_report.csv"
        
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
        Process a single audio file and extract metadata.

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
            'probe_raw_output': None
        }

        try:
            # Get file size
            result['file_size_bytes'] = file_path.stat().st_size

            # Probe the file using the existing ProbeData class
            probe = ProbeData.generate(str(file_path))

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

        # Reorder columns for better readability
        column_order = [
            'file_path', 'status', 'bitrate', 'channels', 'duration',
            'format_name', 'mime_type', 'warnings', 'file_size_bytes',
            'error_message', 'absolute_path', 'probe_raw_output'
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
        }

        # Calculate additional statistics for successful files
        successful_files = df[df['status'] == 'Success']

        if not successful_files.empty:
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
        print(f"Total files processed: {summary['total_files']}")
        print(f"Successful: {summary['successful']}")
        print(f"Errors: {summary['errors']}")
        print(f"File not found: {summary['file_not_found']}")

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
    Main execution function that handles both folders and individual files.
    
    Supports two workflows:
    1. Folders: Audio/folder_name/*.{mp3,flac,wav,m4a,aac,ogg,wma} → folder_name_ffmpeg_probe_report.csv
    2. Individual files: Audio/*.{mp3,flac,wav,m4a,aac,ogg,wma} → individual_files_ffmpeg_probe_report.csv
    """
    audio_base_dir = Path(os.getcwd()) / "Audio"
    
    if not audio_base_dir.exists():
        print(f"Error: Audio directory not found at {audio_base_dir}")
        print("Please create an 'Audio' directory and add your audio "
              "files or folders there.")
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
            processor = BatchAudioProber(str(folder))
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
            processor = BatchAudioProber(str(audio_base_dir))
            
            # Override the output filename for individual files
            reports_dir = Path(os.getcwd()) / 'Batch_Probe_Reports'
            processor.output_file = str(reports_dir / 'individual_files_ffmpeg_probe_report.csv')
            
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
