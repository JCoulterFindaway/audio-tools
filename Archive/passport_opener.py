
"""
ARCHIVED: This file is no longer needed.

Duration extraction is now handled by the batch_audio_prober.py and 
audio_service_prober.py tools, which provide:
- Better error handling
- More robust parsing logic  
- Integration with comprehensive metadata extraction
- No dependency on structlog

This tool had flawed parsing logic (looking for 'time=' instead of 'Duration:')
and undocumented dependencies. The functionality is superseded by ProbeData
in audio_service_prober.py.

Archived on: January 2025
Reason: Redundant functionality, flawed implementation, better alternatives available
"""

import subprocess

from util import get_logger


class AudioToAudioServiceHandler(object):
    log = get_logger()

    def __init__(self):
        pass


    def get_track_duration_sec(self, file_path: str) -> float:
        # FFMPEG_STATIC = "./voices/ffmpeg/ffmpeg" #this should be amd64/ x86_64

        """
        Using ffmpeg, get track duration seconds for the given file
        """

        print("----------------------------------------------")
        print(file_path)

        cmd = ["ffmpeg", '-i', file_path, '-f', 'null', '-']

        try:

            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

            lines = output.decode('utf8').split('\n')

            for line in lines:
                if 'time=' in line:
                    inner_items = line.split(' ')
                    for item in inner_items:
                        if 'time=' in item:
                            _t_split = item.split('=')[1].split(':')
                            _h = 3600 * int(_t_split[0])
                            _m = 60 * int(_t_split[1])
                            _s = float(_t_split[2])
                            length = _h+_m+_s

            print("- GOOD")
            print(length)
            return length

        except subprocess.CalledProcessError as e:

            print("- ERROR")
            print(e.stdout.decode('utf8')[:5000])


            # self.log.error(
            #     'Audio probe error',
            #     exit_code=e.returncode,
            #     stderr=e.stderr,
            # )

            # raise e





if __name__ == '__main__':
    probe = AudioToAudioServiceHandler()
    probe.get_track_duration_sec('01 Jack Benny 11-15-36 Buck Benny Rides Again Part 1.mp3')
    probe.get_track_duration_sec('02 Jack Benny 11-22-36 Buck Benny Rides Again Part 2 fix.mp3')
    probe.get_track_duration_sec('03 Fred Allen 10-25-39 The Prairie Predicament.mp3')
    probe.get_track_duration_sec('04 Fibber McGee 06-20-44 Getting Ready for Ranch Vacation.mp3')
    probe.get_track_duration_sec('05 Alan Young 05-23-47 Cowboy Blood.mp3')
    probe.get_track_duration_sec('06 Milton Berle 10-07-47 A Salute to the Old West.mp3')
    probe.get_track_duration_sec('07 Charlie McCarthy 12-07-47 Guest Roy Rogers.mp3')
    # probe.generate('9781094327129_004.mp3')