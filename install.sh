#!/bin/sh

pip install --user pyglet pydub
apt install omxplayer ffmpeg libavcodec-extra-53 python3-pyaudio
echo 'options snd-card-usb-caiaq index=0' > /etc/modprobe.d/alsa-base.conf
chown root:root /etc/modprobe.d/alsa-base.conf
chmod 644 /etc/modprobe.d/alsa-base.conf

# darwin only
# brew install portaudio
# otherwise make sure portaudio is installed if pip won't install pyaudio
# any OS other than raspi
# pip install --user pyaudio
