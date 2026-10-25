#!/bin/sh
# Disposable Live VM only. Manual invocation, never part of the desktop.
set -eu
test "$(id -u)" = 0
test "$(findmnt -n -o FSTYPE /)" = overlay
test "$(cat /sys/class/dmi/id/product_name)" = VirtualBox
id ally >/dev/null
mkdir -p /mnt/allyos-src /mnt/allyos-output /mnt/interface-src
mountpoint -q /mnt/allyos-src || mount -t vboxsf -o ro allyos-src /mnt/allyos-src
mountpoint -q /mnt/allyos-output || mount -t vboxsf -o uid=1000,gid=1000 allyos-output /mnt/allyos-output
mountpoint -q /mnt/interface-src || mount --bind /mnt/allyos-src/shell /mnt/interface-src
runuser -u ally -- env ALLYOS_TEST_BRIDGE=full-live python3 /mnt/interface-src/vm-command-bridge.py \
    >/mnt/allyos-output/full-live-bridge.log 2>&1 </dev/null &
echo TEST_BRIDGE_READY
