#!/usr/bin/env python

from itertools import cycle
from os import scandir
from pyaudio import PyAudio
import wave


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
    def __init__(self, player, filename):
        with wave.open(filename, 'rb') as wav:
            self.stream = player.open(
                    format=player.get_format_from_width(wav.getsampwidth()),
                    channels=wav.getnchannels(),
                    rate=wav.getframerate(),
                    output=True
                )
            self.loaded = [block for block in self.load_wav(wav)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop_stream()
        self.stream.close()

    @staticmethod
    def load_wav(wav, chunkSize=1024):
        data = wav.readframes(chunkSize)
        while data:
            yield data
            data = wav.readframes(chunkSize)

    def play(self, loop=True):
        for chunk in (cycle(self.loaded) if loop else self.loaded):
            self.stream.write(chunk)

    # def play_lite(self, wav, loop=True):
    #     loading = load_wav(wav)
    #     while True:
    #         chunk = yield loading
    #         if len(chunk) < 1024 and loop:
    #             loading = load_wav(wav)
    #         self.stream.write(chunk)


class Playlist:
    def __init__(self, directory=None, files=None):
        self.player, self.files = Player(), []
        if directory:
            self.scan(directory)
        if files:
            self.files.extend(*files)

    def scan(self, directory):
        for f in scandir(directory):
            if not f.is_dir():
                self.add(f.path)

    def add(self, filepath):
        assert isinstance(filepath, str), 'Must be str'
        self.files.append(filepath)

    def start(self, loop=True):
        if not self.files:
            raise MissingAssetsException('Must add files to play')
        with self.player as player:
            try:
                for f in self.files:
                    with Sound(self.player, f) as sound:
                        sound.play(loop=loop)
            except KeyboardInterrupt:
                return


class Machine:
    def __init__(self):
        pass


if __name__ == '__main__':
    p = Playlist('./Other/audio_files')
    p.start()
