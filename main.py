#!/usr/bin/env python

from gpiozero import Button
from pyplayer import Playlist


class NoiseMachine(Playlist):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skipButton = Button(23)
        self.skipButton.when_pressed = super().skip
        self.mute = Button(26)
        self.volumeIncrement = None
        self.volumeDecrement = None


if __name__ == '__main__':
    with NoiseMachine('./Other/audio_files') as machine:
        machine.start(loop=True)
