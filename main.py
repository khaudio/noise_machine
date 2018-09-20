#!/usr/bin/env python

from gpiozero import Button
from pyplayer import Playlist


class NoiseMachine(Playlist):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.skipButton = Button(23)
        # self.skipButton.when_pressed = super().skip
        # self.mute = Button(26)
        # self.volumeIncrement = None
        # self.volumeDecrement = None
        self.volumeCycle = Button(23)
        self.volumeCycle.when_pressed = self.scale_output

    def scale_output(self):
        scale = self.scaler[0] + .1
        if scale >= 1.0:
            self.scaler.append(0)
        else:
            self.scaler.append(scale)


if __name__ == '__main__':
    with NoiseMachine('./Other/audio_files') as machine:
        machine.start(loop=True)
