#!/usr/bin/env python

from itertools import cycle
from os import scandir, path
from pyaudio import PyAudio
import wave

"""A simple audio playlist with selectable looping sounds"""


class MissingAssetsException(BaseException):
    pass


class Player(PyAudio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()


class Sound:
    def __init__(self, player, filename, loop=True):
        self.loop = loop
        with wave.open(filename, 'rb') as wav:
            self.stream = player.open(
                    format=player.get_format_from_width(wav.getsampwidth()),
                    channels=wav.getnchannels(),
                    rate=wav.getframerate(),
                    output=True
                )
            self.buffer = [chunk for chunk in self.load_wav(wav)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop_stream()
        self.stream.close()

    @staticmethod
    def load_wav(wav, chunkSize=1024):
        chunk = wav.readframes(chunkSize)
        while chunk:
            yield chunk
            chunk = wav.readframes(chunkSize)

    def play(self):
        for chunk in (cycle(self.buffer) if self.loop else self.buffer):
            self.stream.write(chunk)


class Playlist:
    def __init__(self, directory=None, files=None, repeat=True, verbose=True):
        self.alive = True
        self.player, self.files = Player(), []
        self.current, self.index = None, 0
        self.repeat, self.repeated = repeat, 0
        self.verbose = verbose
        if directory:
            self.scan(directory)
        if files:
            for f in files:
                self.add(f)
            self.current = self.files[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def __iter__(self):
        self.index = 0
        self.current = self.sounds[self.index]
        return self

    def __next__(self):
        try:
            self.current = self.sounds[self.index]
        except IndexError:
            if self.repeat is True:
                pass
            elif self.repeated < self.repeat:
                self.repeated += 1
            else:
                raise StopIteration()
            self.index = 0
            return next(self)
        else:
            self.index += 1
            return self.current

    def __len__(self):
        return len(self.sounds)

    def __gt__(self, other):
        return self.sounds > other.sounds

    def __ge__(self, other):
        return self.sounds >= other.sounds

    def __lt__(self, other):
        return self.sounds < other.sounds

    def __le__(self, other):
        return self.sounds <= other.sounds

    @property
    def sounds(self):
        return sorted(self.files, key=lambda f: path.basename(f))

    @property
    def repeat(self):
        return self._repeat

    @repeat.setter
    def repeat(self, val):
        if val is True:
            self._repeat = True
        elif not val:
            self._repeat = 0
        elif isinstance(val, int):
            self._repeat = val
        elif isinstance(val, float):
            self._repeat = int(val)
        else:
            raise IndexError('Must be bool, int, or float')

    def scan(self, directory, recursive=True):
        assert isinstance(directory, str), 'Must be str'
        for f in scandir(directory):
            if not f.is_dir():
                self.add(f.path)
            elif recursive:
                self.scan(f.paths)

    def add(self, filepath):
        assert isinstance(filepath, str), 'Must be str'
        self.files.append(filepath)

    def play(self, filepath, **kwargs):
        try:
            with Sound(self.player, filepath, **kwargs) as sound:
                if self.verbose:
                    print(f'Playing {path.basename(filepath)}')
                sound.play()
        except KeyboardInterrupt:
            return

    def stop(self):
        self.player.terminate()
        self.alive = False

    def start(self, loop=True):
        if not self.sounds:
            raise MissingAssetsException('Must add files to play')
        for sound in iter(self):
            if self.alive:
                self.play(sound, loop=loop)
