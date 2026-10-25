#!/bin/sh
# Manual test helper for our disposable installed VM; never autostarted.
set -eu
test "$(id -u)" = 0
test "$(cat /sys/class/dmi/id/product_name)" = VirtualBox
test "$(hostname)" = allyos-install-test
test "$(findmnt -n -o FSTYPE /)" != overlay
id allytest >/dev/null
mkdir -p /mnt/allyos-src /mnt/allyos-output /mnt/interface-src
mountpoint -q /mnt/allyos-src || mount -t vboxsf -o ro allyos-src /mnt/allyos-src
mountpoint -q /mnt/allyos-output || mount -t vboxsf -o uid=1000,gid=1000 allyos-output /mnt/allyos-output
mountpoint -q /mnt/interface-src || mount --bind /mnt/allyos-src/shell /mnt/interface-src
runuser -u allytest -- env ALLYOS_TEST_BRIDGE=full-installed python3 /mnt/interface-src/vm-command-bridge.py \
    >/mnt/allyos-output/full-installed-bridge.log 2>&1 </dev/null &
echo INSTALLED_TEST_BRIDGE_READY
