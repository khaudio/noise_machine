#!/usr/bin/env python3

from subprocess import Popen, PIPE
from glob import glob


"""
Plays selectable audio files in a loop for use as ambient noise
"""


class Playlist:
    def __init__(self, dir):
        assert isinstance(dir, str), 'Must be str'
        self.dir, self.files, self.alive = dir, [], True
        self.scan()
        self.__selected__ = None if self.files is None else self.files[0]

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.alive = False

    @property
    def selected(self):
        if not self.__selected__:
            return self.files[0] if self.files else None
        else:
            return self.__selected__

    @selected.setter
    def selected(self, new):
        assert isinstance(new, str), 'Must be str'
        self.__selected__ = new

    def scan(self):
        self.files = [audioFile for audioFile in glob(self.dir + '/**')]

    def play(self):
        playing = Popen(
                ['omxplayer', self.selected],
                stdin=PIPE, stdout=PIPE, stderr=PIPE
            )
        for message in playing.communicate():
            print('message is ', message)
            if b'have a nice day' in message:
                return

    def loop(self):
        while self.alive:
            self.play()


if __name__ == '__main__':
    with Playlist('audio_files') as p:
        p.loop()
