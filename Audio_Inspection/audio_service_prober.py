
import json
import re
import subprocess
from decimal import Decimal

# from util import get_logger

# log = get_logger()


class BaseProbe(object):
    """
    Starting "basic" prober that handles most cases.  Makes a
    "best effort" to grab as much metadata as possible before
    failing so as to inform later probes.
    """

    formats = ['flac', 'mp3', 'm4a', 'ogg', 'wav']

    subprocess_opts = {
        'check': True,
        'stdout': subprocess.DEVNULL,
        'stderr': subprocess.PIPE,
    }

    metadata_encodings = [
        'utf-8',
        'latin-1',
    ]

    error_rexes = list(map(lambda x: re.compile(x, re.MULTILINE), [
        r'Input/output error',
    ]))

    warning_rexes = list(map(lambda x: re.compile(x, re.MULTILINE), [
        r'detected only with low score',
        r'misdetection possible',
        r'Invalid data found',
        r'corrupt',
        r'Truncating packet',
        r'Header missing',
        r'Estimating duration',
        r'unknown/unknown',  # Malformed colorspace metadata
        r'start: [^0]',      # Non-zero start time (may indicate timing issues)
        r'\\x[0-9a-f]{2}',   # Byte sequences in metadata (encoding issues)
    ]))

    def __init__(self, probe_args):
        self.exception = None
        self._probe_data = None
        self._decoded_data = None
        self._parsed_data = {}

        self.probe_args = probe_args

        self.probe_command = [
            'ffmpeg',
            '-xerror',
            '-loglevel', 'info',
            '-vn',
            '-i', '{source_url}',
            '-codec', 'copy',
            '-f', 'null',
            '-'
        ]

        self.rexes = list(map(lambda x: re.compile(x, re.MULTILINE), [
            r'^Input #0, (?P<formats>[\w,]+)',
            r'^\s+Duration:.*bitrate: (?P<file_br>[0-9]+) kb/s',
            r'^\s+Stream.*(?P<channels>mono|stereo)',
            r'^\s+Stream.*, (?P<stream_br>[0-9]+) kb/s',
            r'(?s)size=.*time=(?P<duration>\d+:\d{2}:\d{2}\.\d{2}) ',
        ]))

    @property
    def probe_data(self):
        """
        Run probe_command with subprocess_opts and return the stderr
        """
        if not self._probe_data:
            try:
                command = [
                    x.format(**self.probe_args)
                    for x in self.probe_command
                ]
                print(command)
                proc = subprocess.run(command, **self.subprocess_opts)
                print(proc.stderr)
                self._probe_data = proc.stderr

            except subprocess.CalledProcessError as e:
                print(e.stderr)
                # log.error(
                #     'Audio probe error',
                #     exit_code=e.returncode,
                #     stderr=e.stderr,
                # )
                # self.exception = e

        return self._probe_data

    def extract_warnings(self):
        """
        Extract warning messages from stderr output.
        
        Returns:
            list: List of warning messages found in stderr
        """
        warnings = []
        if self._probe_data:
            for encoding in self.metadata_encodings:
                try:
                    decoded = self._probe_data.decode(encoding)
                    for warning_regex in self.warning_rexes:
                        matches = warning_regex.findall(decoded)
                        for match in matches:
                            # Find the full line containing the warning
                            lines = decoded.split('\n')
                            for line in lines:
                                if match in line:
                                    warnings.append(line.strip())
                    break
                except UnicodeDecodeError:
                    continue
        return list(set(warnings))  # Remove duplicates

    @property
    def decoded_data(self):
        """
        Try the encodings in metadata_encodings to decipher probe_output
        """
        if not self._decoded_data:
            if self.probe_data:
                self._decoded_data = None
                for encoding in self.metadata_encodings:
                    # log.debug(encoding=encoding)
                    try:
                        self._decoded_data = self.probe_data.decode(encoding)
                        break
                    except UnicodeDecodeError as e:
                        print(e)
                        # log.debug(exception=e)

        return self._decoded_data

    @property
    def parsed_data(self):
        """
        Apply the regular expressions in rexes to decoded_output,
        ignoring failed matches, and return a dict of the superset
        of named match groups.
        """
        if not self._parsed_data:
            if self.decoded_data:
                self._parsed_data = {}
                for rex in self.rexes:
                    match = rex.search(self.decoded_data)
                    # log.debug(rex=rex, match=match)
                    if match:
                        self._parsed_data.update(match.groupdict())

                for rex in self.error_rexes:
                    match = rex.search(self.decoded_data)
                    # log.debug(rex=rex, match=match)
                    if match:
                        msg = f'Failed error regex {rex.pattern}'
                        self.exception = Exception(msg)

        return self._parsed_data

    @property
    def bitrate(self):
        if self.parsed_data.get('stream_br'):
            return int(self.parsed_data['stream_br'])

        if self.parsed_data.get('file_br'):
            return int(self.parsed_data['file_br'])

    @property
    def channels(self):
        channels = {'mono': 1, 'stereo': 2}
        return channels.get(self.parsed_data.get('channels'))

    @property
    def duration(self):
        if self.parsed_data.get('duration'):
            duration = self.parsed_data['duration']
            (h, m, s) = duration.split(':')
            duration = (int(h) * 3600)
            duration += (int(m) * 60)
            duration += Decimal(s).quantize(Decimal('0.01'))
            return duration

    @property
    def format_name(self):
        for ft in self.parsed_data.get('formats', '').split(','):
            if ft in self.formats:
                return ft

    @property
    def mime_type(self):
        if self.format_name:
            return f'audio/{self.format_name}'

    @property
    def raw(self):
        return self.decoded_data

    @property
    def complete(self):
        return(
            self.bitrate is not None and
            self.channels is not None and
            self.duration is not None and
            self.format_name is not None and
            self.mime_type is not None and
            self.raw is not None and
            not self.exception
        )

    def to_dict(self):
        return {
            'bitrate': self.bitrate,
            'channels': self.channels,
            'duration': str(self.duration),
            'format_name': self.format_name,
            'mime_type': self.mime_type,
            'raw': self.raw,
            'warnings': self.extract_warnings(),
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)


class FormatProbe(BaseProbe):
    """
    Secondary prober that uses a file type to try and get complete
    probe data.
    """

    def __init__(self, probe_args):

        super().__init__(probe_args)

        self.probe_command = [
            'ffmpeg',
            '-xerror',
            '-loglevel', 'info',
            '-vn',
            '-f', '{file_type}',
            '-i', '{source_url}',
            '-codec', 'copy',
            '-f', 'null',
            '-'
        ]


class FormatWriteProbe(BaseProbe):
    """
    Secondary prober that uses a file type and forces output of the same
    type (not null handler) to try and get complete probe data.  This
    is slower and should be a late choice for probing.
    """

    def __init__(self, probe_args):

        super().__init__(probe_args)

        self.probe_command = [
            'ffmpeg',
            '-xerror',
            '-loglevel', 'info',
            '-vn',
            '-f', '{file_type}',
            '-i', '{source_url}',
            '-codec', 'copy',
            '-f', '{file_type}',
            '-'
        ]

        self.rexes[1] = re.compile(
            r'(?s)size.*bitrate= (?P<file_br>[0-9]+)\.[0-9]kbits',
            re.MULTILINE
        )


class ProbeData(object):
    """
    Factory object generating probe objects.
    """
    @classmethod
    def generate(cls, source_url):
        probe = BaseProbe({'source_url': source_url})

        if not probe.complete and probe.format_name:
            probe = FormatWriteProbe({
                'source_url': source_url,
                'file_type': probe.format_name,
            })

        if not probe.complete:
            probe = FormatProbe({
                'source_url': source_url,
                'file_type': 'mp3',
            })

        if probe.exception:
            raise Exception('Unable to probe file') from probe.exception
        else:
            print(probe.to_json())

        if probe.complete:
            return probe

        print(probe.to_json())
        # log.info(probe=probe.to_json())

        raise Exception('Unable to probe file')


if __name__ == '__main__':
    probe = ProbeData()
    # update this to use the actual file path
    probe.generate('9782073130808_01.mp3')
