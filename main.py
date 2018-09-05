#!/usr/bin/env python

from pyplayer import Playlist


class NoiseMachine(Playlist):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    with NoiseMachine('./Other/audio_files', repeat=0) as machine:
        machine.start(loop=False)
