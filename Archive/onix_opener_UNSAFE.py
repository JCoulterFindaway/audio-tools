
"""
ARCHIVED: Do NOT use this audio normalizer - UNSAFE implementation

CRITICAL SAFETY ISSUES:
- Creates temporary files in ROOT directory (/) which is dangerous
- Could fill up system disk or cause permission errors
- No proper error handling for temp file cleanup
- Broken context manager implementation

This tool DOES work for audio normalization but has serious safety flaws.
A corrected safe version exists in the Archive as reference.

RECOMMENDATION: Do not use this tool. If audio normalization is needed,
use the safe version or modern alternatives.

Archived on: January 2025  
Reason: Unsafe temp file handling, dangerous implementation
"""

import os
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from typing import ContextManager
from uuid import uuid4


@dataclass
class AudioEngineAudioEncoder:
    # ae_mp3_standard_sample_rate = 44100
    # ae_mp3_standard_ffmpeg_bitrate_string = '64k'
    # ae_mp3_standard_codec = 'libmp3lame'

    scratch_path: str = '/'
    ae_mp3_standard_codec: str = 'libmp3lame'
    ae_mp3_standard_sample_rate: int = 44100
    ae_mp3_standard_ffmpeg_bitrate: str = '64k'

    def normalize_audio_file(self, audio_filename: str) -> ContextManager[str]:

        temp_filenames = [
            f'{self.scratch_path}/{str(uuid4())}.mp3',
            f'{self.scratch_path}/{str(uuid4())}.mp3'
        ]

        try:
            # convert to an mp3 file with the standardized
            #   codec, bit rate, etc.
            convert_command = [
                'ffmpeg',
                '-loglevel', 'repeat+level+verbose',
                '-y',
                '-i', f'"{audio_filename}"',
                '-ar', f'{self.ae_mp3_standard_sample_rate}',
                '-b:a', f'{self.ae_mp3_standard_ffmpeg_bitrate}',
                '-c:a', f'{self.ae_mp3_standard_codec}',
                '-ac', '1',
                f'"{temp_filenames[0]}"',
            ]

            print(subprocess.check_output(' '.join(convert_command), shell=True, stderr=subprocess.STDOUT))

            # clean the id3 tags out of the file
            clean_command = [
                'ffmpeg',
                '-loglevel', 'repeat+level+verbose',
                '-y',
                '-i', f'"{temp_filenames[0]}"',
                '-map', '0:a',
                '-codec:a', 'copy',
                '-map_metadata', '-1',
                f'"{temp_filenames[1]}"',
            ]

            print(subprocess.check_output(' '.join(clean_command), shell=True, stderr=subprocess.STDOUT))

        except subprocess.CalledProcessError as exc:
            print(exc)

        finally:
            for temp_filename in temp_filenames:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)


if __name__ == '__main__':
    encoder = AudioEngineAudioEncoder()
    encoder.normalize_audio_file(audio_filename="4066339840768_preview.mp3")