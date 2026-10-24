#!/bin/sh
set -eu
export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
apt-get update
apt-get install -y --no-install-recommends ffmpeg
ffmpeg -nostdin -v error -y -i /mnt/allyos-src/iso/local-assets/startup.mp3 -ac 2 -ar 44100 /mnt/allyos-output/startup-local.wav
chmod 644 /mnt/allyos-output/startup-local.wav
