#!/bin/sh
# Experimento somente no Live da VM; a mídia ISO permanece intacta.
set -eu
test "$(id -u)" = 0
test -d /run/live/medium
test "$(cat /sys/class/dmi/id/product_name)" = VirtualBox
grep -qx 0x15ad /sys/bus/pci/devices/0000:00:02.0/vendor
mkdir -p /etc/X11/xorg.conf.d
cat > /etc/X11/xorg.conf.d/20-allyos-vmsvga.conf <<'CONFIG'
Section "OutputClass"
    Identifier "AllyOS VirtualBox VMSVGA"
    MatchDriver "vmwgfx"
    Driver "modesetting"
EndSection
CONFIG
systemctl restart sddm
