#!/usr/bin/env python

import scipy.io.wavfile as swav
import numpy as np
import wave
import thinkdsp
import thinkplot
import os

"""Spectral manipulation sandbox using scipy and numpy"""


def process(filepath):
    f = swav.read(filepath)
    for chunk in f[1]:
        print(chunk)


def analyze(filepath, room):
    wav = thinkdsp.read_wave(filepath).make_spectrum()
    room = thinkdsp.read_wave(room).make_spectrum()

    wav.plot()
    room.plot()
    thinkplot.show()


if __name__ == '__main__':
    directory = './Other/audio_files/'
    signal = os.path.join(directory, 'pinkNoise_01.wav')
    room = os.path.join(directory, 'pinkNoise_01_smallRoom.wav')
    try:
        analyze(signal, room)
    except KeyboardInterrupt:
        pass
