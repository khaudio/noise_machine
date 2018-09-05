#!/usr/bin/env python

from gpiozero import Button
from pyplayer import Playlist


class NoiseMachine(Playlist):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button = Button(26)
        self.button.when_pressed = super().skip


if __name__ == '__main__':
    with NoiseMachine('./Other/audio_files', repeat=2) as machine:
        machine.start(loop=False)
