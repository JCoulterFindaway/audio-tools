
import subprocess
from dataclasses import dataclass


@dataclass
class ScratchProbe:
    def probe(self, audio_filename: str) -> None:

        try:
            # only a -i command
            info_command = [
                'ffmpeg',
                '-i', f'{audio_filename}',
            ]

            print(subprocess.check_output(' '.join(info_command), shell=True))

        except subprocess.CalledProcessError as exc:
            print(exc)


if __name__ == '__main__':
    encoder = ScratchProbe()
    encoder.probe(audio_filename="001_JackGirlzMAR.mp3")