#!/usr/bin/env python

import scipy.io.wavfile as swav
import numpy as np

"""Spectral manipulation sandbox using scipy and numpy"""


def process(filepath):
    f = swav.read(filepath)
    for chunk in f[1]:
        print(chunk)

if __name__ == '__main__':
    process('./Other/audio_files/pinkNoise_01.wav')
