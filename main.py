#!/usr/bin/env python

from gpiozero import Button, DigitalInputDevice
from pyplayer import Playlist
from threading import Thread
from time import sleep
import json


class QuadratureEncoder:
    def __init__(self, clockPin, dataPin):
        for pin in (clockPin, dataPin):
            assert isinstance(pin, int), 'Must be int'
        self.alive = True
        self.clock = DigitalInputDevice(clockPin)
        self.data = DigitalInputDevice(dataPin)
        self.last = None

    def close(self):
        self.alive = False
        for device in (self.clock, self.data):
            device.close()

    def read(self):
        try:
            clock, data = self.clock.value, self.data.value
            if clock != self.last:
                if clock ^ data:
                    yield -.05
                else:
                    yield .05
                self.last = clock
        except Exception as e:
            print(e)
            raise e

    def monitor(self):
        while self.alive:
            yield from self.read()

class NoiseMachine(Playlist):
    def __init__(
            self, filepath,
            clockPin=17, dataPin=27, muteButton=22, skipButton=23,
            *args, **kwargs
        ):
        super().__init__(filepath, *args, **kwargs)
        self.load()
        self.volumeRotary = QuadratureEncoder(clockPin, dataPin)
        self.volumeMonitor = Thread(target=self.monitor_volume)
        self.volumeMonitor.start()
        self.skipButton = Button(skipButton, bounce_time=.005)
        self.skipButton.when_pressed = super().skip
        self.muteButton = Button(muteButton, bounce_time=.005)
        self.muteButton.when_pressed = super().toggle_mute
        self.devices = (self.volumeRotary, self.skipButton, self.muteButton)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for device in self.devices:
            device.close()
        self.volumeMonitor.join()
        self.save()
        super().__exit__(exc_type, exc_value, traceback)

    def save(self):
        with open('meta.json', 'wb') as meta:
            metadata = {'scale': self.scale}
            meta.write(json.dumps(metadata, indent=4).encode('utf-8'))

    def load(self):
        try:
            with open('meta.json', 'rb') as meta:
                metadata = json.load(meta)
                self.scale = metadata['scale']
        except:
            self.scale = .5

    def monitor_volume(self):
        for increment in self.volumeRotary.monitor():
            super().increment_scale(increment)


if __name__ == '__main__':
    with NoiseMachine('./Other/audio_files') as machine:
        machine.start(loop=True)
