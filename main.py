#!/usr/bin/env python

from gpiozero import Button
from pyplayer import Playlist


class NoiseMachine(Playlist):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button = Button(23)
        self.button.when_pressed = super().skip


if __name__ == '__main__':
    with NoiseMachine('./Other/audio_files') as machine:
        machine.start()
