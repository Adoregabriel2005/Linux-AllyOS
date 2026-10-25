#!/bin/sh
# Copyright 2026 gorigamia. GPL-3.0-or-later.
# O driver VMware DDX sem aceleração deixou o primeiro quadro preto no Live.
# Selecionar o driver Xorg modesetting apenas no VirtualBox com VMSVGA.
set -eu
configuration=/etc/X11/xorg.conf.d/20-allyos-vmsvga.conf
matched=no
if [ "$(cat /sys/class/dmi/id/product_name 2>/dev/null || true)" = VirtualBox ]; then
    for device in /sys/bus/pci/devices/*; do
        if [ "$(cat "$device/vendor" 2>/dev/null || true)" = 0x15ad ] &&
           [ "$(cat "$device/device" 2>/dev/null || true)" = 0x0405 ]; then
            matched=yes
            break
        fi
    done
fi
if [ "$matched" = yes ]; then
    if [ -f "$configuration" ] && ! grep -q '^# AllyOS-managed:' "$configuration"; then
        exit 0 # Respeitar uma configuração que o usuário criou nesse caminho.
    fi
    install -d -m 755 /etc/X11/xorg.conf.d
    cat > "$configuration" <<'CONFIG'
# AllyOS-managed: VirtualBox VMSVGA only
Section "OutputClass"
    Identifier "AllyOS VirtualBox VMSVGA"
    MatchDriver "vmwgfx"
    Driver "modesetting"
    Option "AccelMethod" "none"
    Option "SWcursor" "true"
EndSection
CONFIG
elif [ -f "$configuration" ] && grep -q '^# AllyOS-managed:' "$configuration"; then
    rm -f "$configuration"
fi
