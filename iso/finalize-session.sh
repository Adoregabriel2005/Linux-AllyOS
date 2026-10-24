#!/bin/sh
# Apply the final-hook session correction to the already built chroot.
set -eu
test "$(id -u)" = 0
root=/home/goriga/allyos-trixie-build/chroot
test "$(realpath "$root")" = /home/goriga/allyos-trixie-build/chroot
grep -q '^ID=allyos$' "$root/usr/lib/os-release"
test -x "$root/usr/bin/roseshell-session"
chroot "$root" update-alternatives --install /usr/bin/x-session-manager x-session-manager /usr/bin/roseshell-session 100
chroot "$root" update-alternatives --set x-session-manager /usr/bin/roseshell-session
test "$(chroot "$root" readlink -f /usr/bin/x-session-manager)" = /usr/bin/roseshell-session
echo 'RoseShell selected as default x-session-manager'
