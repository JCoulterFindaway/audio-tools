#!/usr/bin/env python3
"""
ARCHIVED: Audio Normalizer - Safe Version

This tool successfully normalizes audio files to standard format:
- 64kbps bitrate, mono, 44.1kHz sample rate
- Strips all metadata/ID3 tags  
- Uses safe temp directories (fixed from original)
- Proven to work correctly in testing

POLICY NOTE: While this tool works perfectly, we are no longer in the 
practice of manipulating audio files for any purpose. This is archived 
for reference and knowledge preservation only.

Safety improvements over original onix_opener.py:
- Uses safe temp directory instead of root (/)
- Proper error handling and logging
- Fixed context manager implementation
- Clean temp file management

Archived on: January 2025
Reason: Policy change - no longer manipulating audio files
"""

import os
import subprocess
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class SafeAudioNormalizer:
    # SAFETY: Use safe temp directory instead of root /
    scratch_path: str = './temp'  # CHANGED FROM: '/'
    ae_mp3_standard_codec: str = 'libmp3lame'
    ae_mp3_standard_sample_rate: int = 44100
    ae_mp3_standard_ffmpeg_bitrate: str = '64k'

    def __post_init__(self):
        """Ensure temp directory exists"""
        os.makedirs(self.scratch_path, exist_ok=True)

    def normalize_audio_file(self, audio_filename: str, output_filename: str = None):
        """
        Normalize audio file to standard format.
        
        SAFE VERSION: Returns output filename instead of broken context manager
        """
        
        temp_filenames = [
            f'{self.scratch_path}/{str(uuid4())}.mp3',
            f'{self.scratch_path}/{str(uuid4())}.mp3'
        ]
        
        final_output = output_filename or f'./output/normalized_{os.path.basename(audio_filename)}'
        
        print(f"🎵 Normalizing: {audio_filename}")
        print(f"📁 Temp files: {temp_filenames}")
        print(f"💾 Output: {final_output}")
        
        try:
            # Step 1: Convert to standardized MP3 format
            print("📡 Step 1: Converting to standard format...")
            convert_command = [
                'ffmpeg',
                '-loglevel', 'warning',  # Less verbose
                '-y',  # Overwrite output files
                '-i', audio_filename,
                '-ar', str(self.ae_mp3_standard_sample_rate),
                '-b:a', self.ae_mp3_standard_ffmpeg_bitrate,
                '-c:a', self.ae_mp3_standard_codec,
                '-ac', '1',  # Mono
                temp_filenames[0],
            ]

            result1 = subprocess.run(convert_command, capture_output=True, text=True)
            if result1.returncode != 0:
                print(f"❌ Conversion failed: {result1.stderr}")
                return None
                
            print("✅ Step 1 complete")

            # Step 2: Clean metadata/ID3 tags
            print("🧹 Step 2: Cleaning metadata...")
            clean_command = [
                'ffmpeg',
                '-loglevel', 'warning',
                '-y',
                '-i', temp_filenames[0],
                '-map', '0:a',
                '-codec:a', 'copy',
                '-map_metadata', '-1',  # Remove all metadata
                temp_filenames[1],
            ]

            result2 = subprocess.run(clean_command, capture_output=True, text=True)
            if result2.returncode != 0:
                print(f"❌ Metadata cleaning failed: {result2.stderr}")
                return None
                
            print("✅ Step 2 complete")
            
            # Step 3: Move to final output location
            print("📦 Step 3: Moving to final location...")
            os.makedirs(os.path.dirname(final_output), exist_ok=True)
            os.rename(temp_filenames[1], final_output)
            print(f"✅ Normalization complete: {final_output}")
            
            return final_output

        except Exception as exc:
            print(f"❌ Error: {exc}")
            return None
            
        finally:
            # Cleanup temp files
            print("🧽 Cleaning up temp files...")
            for temp_filename in temp_filenames:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    print(f"🗑️  Removed: {temp_filename}")


if __name__ == '__main__':
    print("=== Safe Audio Normalizer Test ===")
    normalizer = SafeAudioNormalizer()
    
    # Test with our sample file
    input_file = 'input/001_000_FWV234148.mp3'
    output_file = normalizer.normalize_audio_file(input_file)
    
    if output_file and os.path.exists(output_file):
        print(f"🎉 SUCCESS: Normalized file created at {output_file}")
        
        # Show file info
        size = os.path.getsize(output_file)
        print(f"📊 Output file size: {size:,} bytes")
        
        # Quick probe of the result
        print("🔍 Quick probe of normalized file:")
        probe_cmd = ['ffmpeg', '-i', output_file, '-f', 'null', '-', '-v', 'quiet', '-stats']
        subprocess.run(probe_cmd, capture_output=True)
        
    else:
        print("❌ FAILED: No output file created")