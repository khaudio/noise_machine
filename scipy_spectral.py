#!/usr/bin/env python

import scipy.io.wavfile as swav
import numpy as np
import wave
import pyaudio
# from psutil import virtual_memory
# import thinkdsp
# import thinkplot
import os
from collections import deque
import sounddevice as sd

"""Spectral manipulation sandbox using scipy and numpy"""


def load(filepath):
    # memory = virtual_memory()
    # if os.stat(filepath).st_size < memory.available:
    sampleRate, data = swav.read(filepath)
    return data
#     else:
#         print('File too big; reading in chunks')


def progressive_load(filepath, chunkSize=1024):
    with wave.open(filepath, 'rb') as wav:
        chunk = np.frombuffer(wav.readframes(chunkSize), dtype=np.int16)
        while len(chunk) > 0:
            yield chunk
            chunk = np.frombuffer(wav.readframes(chunkSize), dtype=np.int16)

def make_arr(filepath):
    for chunk in progressive_load(filepath):
        arr = np.fromstring(chunk, dtype=np.int16)


# def analyze(filepath, room):
#     wav = thinkdsp.read_wave(filepath).make_spectrum()
#     room = thinkdsp.read_wave(room).make_spectrum()
#
#     wav.plot()
#     room.plot()
#     thinkplot.show()


if __name__ == '__main__':
    directory = './Other/audio_files/'
    signal = os.path.join(directory, 'pinkNoise_01.wav')
    room = os.path.join(directory, 'pinkNoise_01_smallRoom.wav')
    output = pyaudio.PyAudio()
    stream = output.open(channels=1, format=pyaudio.paInt16, rate=48000, output=True)
    try:
        loaded = [chunk for chunk in progressive_load(signal)]
        sampleRate, data = swav.read(signal)
    except Exception as e:
        raise e
    else:
        for chunk in loaded:
            scaled = chunk * .05
            linearized = scaled.astype(np.int16).tostring()
            stream.write(linearized)
    finally:
        stream.stop_stream()
        stream.close()
        output.terminate()
