#!/usr/bin/env python

from collections import deque
from itertools import cycle
from multiprocessing import Lock
from os import scandir, path
from pyaudio import PyAudio
import numpy as np
import wave

"""A simple audio playlist with selectable looping sounds"""


class MissingAssetsException(Exception):
    pass


class SkipTrack(Exception):
    pass


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
            self.buffer = [chunk for chunk in self.load(wav)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop_stream()
        self.stream.close()

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, val):
        assert isinstance(val, PyAudio), 'Must be PyAudio obj'
        self._player = val

    @staticmethod
    def load(wav, chunkSize=1024, array=True):
        chunk = wav.readframes(chunkSize)
        if array:
            data = np.frombuffer(chunk, dtype=np.int16)
        while chunk:
            if array:
                yield data
                data = np.frombuffer(chunk, dtype=np.int16)
            else:
                yield chunk
            chunk = wav.readframes(chunkSize)

    def play(self, skipper=(False,), scaler=(1.0,)):
        for chunk in (cycle(self.buffer) if self.loop else self.buffer):
            if skipper[0]:
                raise SkipTrack()
            self.stream.write((chunk * scaler[0]).astype(np.int16).tostring())


class Playlist:
    def __init__(self, filepath, repeat=True, verbose=True):
        self.alive, self.lock = True, Lock()
        self.player, self.files = PyAudio(), []
        self.current, self.index = None, 0
        self.repeat, self.repeated = repeat, 0
        self.verbose = verbose
        self._skipper = deque((False,), maxlen=1)
        self._scaler = deque((0.5,), maxlen=1)
        self.scan(filepath)
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

    @property
    def scale(self):
        with self.lock:
            return self._scaler[0]

    @scale.setter
    def scale(self, val):
        assert isinstance(val, (int, float)), 'Must be int or float'
        if val <= 0:
            scaled = 0
        elif val >= 1:
            scaled = 1
        else:
            scaled = round(val, 2)
            if scaled > 0:
                self.lastScaled = scaled
        with self.lock:
            self._scaler.append(scaled)
        if self.verbose:
            print('Scale: {}'.format(self._scaler[0]))

    @property
    def skipTrack(self):
        return self._skipper[0]

    @skipTrack.setter
    def skipTrack(self, val):
        self._skipper.append(bool(val))

    def increment_scale(self, increment=.1):
        self.scale += increment

    def scan(self, filepath, recursive=True):
        assert isinstance(filepath, str), 'Must be str'
        try:
            for f in scandir(filepath):
                if not f.is_dir():
                    self.add(f.path)
                elif recursive:
                    self.scan(f.path)
        except NotADirectoryError:
            if path.exists:
                self.add(filepath)

    def add(self, filepath):
        assert isinstance(filepath, str), 'Must be str'
        self.files.append(filepath)

    def play(self, filepath, **kwargs):
        assert self.alive
        try:
            self.skip = False
            with Sound(self.player, filepath, **kwargs) as sound:
                if self.verbose:
                    print('Playing {}'.format(path.basename(filepath)))
                sound.play(self._skipper, scaler=self._scaler)
        except SkipTrack:
            return

    def skip(self):
        if self.verbose:
            print('Skipping')
        self.skipTrack = True

    def mute(self):
        print('Muting')
        self.lastScale = self.scale
        self.scale = 0

    def unmute(self):
        print('Unmuting')
        self.scale = self.lastScale

    def toggle_mute(self):
        if self.scale > 0:
            self.mute()
        else:
            self.unmute()

    def stop(self):
        self.alive = False
        self.player.terminate()

    def start(self, loop=True):
        if not self.sounds:
            raise MissingAssetsException('Must add files to play')
        for sound in self:
            try:
                self.play(self.current, loop=loop)
            except KeyboardInterrupt:
                return
