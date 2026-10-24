#!/bin/sh
set -eu
sudo -v
sudo mkdir -p /mnt/interface-src /mnt/allyos-src /mnt/allyos-output
mountpoint -q /mnt/interface-src || sudo mount -t vboxsf -o ro interface-src /mnt/interface-src
mountpoint -q /mnt/allyos-src || sudo mount -t vboxsf -o ro allyos-src /mnt/allyos-src
mountpoint -q /mnt/allyos-output || sudo mount -t vboxsf -o uid="$(id -u)",gid="$(id -g)" allyos-output /mnt/allyos-output
nohup python3 /mnt/interface-src/vm-command-bridge.py > /mnt/allyos-output/bridge.log 2>&1 < /dev/null &
echo 'Ponte temporaria iniciada. Aguardando diagnostico do build.'
setxkbmap br
