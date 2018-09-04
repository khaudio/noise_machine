#!/usr/bin/env python

from itertools import cycle
from os import scandir
from pyaudio import PyAudio
import wave


class Machine(PyAudio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()


class Noise:
    def __init__(self, machine, filename):
        with wave.open(filename, 'rb') as wav:
            self.stream = machine.open(
                    format=machine.get_format_from_width(wav.getsampwidth()),
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

    def play_lite(self, wav, loop=True):
        loading = load_wav(wav)
        while True:
            chunk = yield loading
            if len(chunk) < 1024 and loop:
                loading = load_wav(wav)
            self.stream.write(chunk)


class Playlist:
    def __init__(self, *sounds):
        self.files = [*sounds]
        self.machine, self.sounds = Machine(), []
        self.add(*self.files)

    def scan(self, directory):
        for f in scandir(directory):
            if not f.is_dir()
                self.files.append(f.path)

    def add(self, *sounds):
        for sound in sounds:
            self.sounds.append(Noise(self.machine, sound))

    def start(self):
        with self.machine as machine:
            try:
                self.sounds[0].play(loop=True)
            except KeyboardInterrupt:
                return


if __name__ == '__main__':
    f = 'audio_files/pinkNoise_01.wav'
    p = Playlist(f)
    p.start()
