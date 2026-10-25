#!/bin/sh
# Apply the reviewed configuration before the chroot-hook phase has started.
set -eu
test "$(id -u)" = 0
test "$(findmnt -n -o SOURCE /srv/allyos-builder)" = /dev/sdb
build=/srv/allyos-builder/build-0.3.3
sources=/srv/allyos-builder/source-0.3.3
test -f "$build/allyos-build.json"
test ! -e "$build/.build/chroot_hooks"
install -m 755 /mnt/allyos-src/iso/public-firmware-cleanup.sh "$build/config/hooks/normal/0998-public-firmware.hook.chroot"
cp /mnt/allyos-src/iso/prepare.py "$sources/iso/prepare.py"
cp /mnt/allyos-src/iso/public-firmware-cleanup.sh "$sources/iso/public-firmware-cleanup.sh"
cp /mnt/allyos-src/COPYRIGHT.md "$sources/COPYRIGHT.md"
PYTHONPATH="$sources/iso" python3 -c 'from pathlib import Path; from prepare import bundle_sources; bundle_sources(Path("/srv/allyos-builder/build-0.3.3"))'
echo PUBLIC_FIRMWARE_POLICY_SYNCED
