#!/bin/sh
# Extracted b43 firmware is not redistributable; retain Debian's packaged firmware.
# https://wireless.docs.kernel.org/en/latest/en/users/drivers/b43/firmware.html
set -eu
dpkg --purge firmware-b43-installer firmware-b43legacy-installer
test ! -d /usr/lib/firmware/b43
test ! -d /usr/lib/firmware/b43legacy
