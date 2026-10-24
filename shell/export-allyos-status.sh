#!/bin/sh
set -eu
sudo mkdir -p /mnt/allyos-output
mountpoint -q /mnt/allyos-output || sudo mount -t vboxsf -o "uid=$(id -u),gid=$(id -g)" allyos-output /mnt/allyos-output
{
    date -u
    echo '--- builder log ---'
    tail -n 100 "$HOME/allyos-build.log" 2>/dev/null || true
    echo '--- stages ---'
    ls -la "$HOME/allyos-build/.build" "$HOME/allyos-build/config" 2>/dev/null || true
    echo '--- greeter ---'
    ls /usr/bin/sddm* 2>/dev/null || true
    echo '--- running builder ---'
    pgrep -af 'lb build|lb bootstrap|iso/build.sh' || true
} > /mnt/allyos-output/status.log
lb config --help > /mnt/allyos-output/live-build-help.txt 2>&1 || true
echo 'ALLYOS STATUS EXPORTED'
