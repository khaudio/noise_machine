#!/bin/sh

pip install --user pyglet pydub
apt install omxplayer ffmpeg libavcodec-extra-53 python3-pyaudio
echo 'options snd-card-usb-caiaq index=0' > /etc/modprobe.d/alsa-base.conf
chown root:root /etc/modprobe.d/alsa-base.conf
chmod 644 /etc/modprobe.d/alsa-base.conf