#!/bin/sh
set -eu
test "$(id -u)" = 0
test -d /run/live/medium
output=/mnt/allyos-output/full-live
mkdir -p "$output"
journalctl -b -u sddm --no-pager > "$output/sddm-boot.log"
dmesg > "$output/kernel-boot.log"
if [ -f /var/log/Xorg.0.log ]; then cp /var/log/Xorg.0.log "$output/Xorg.0.log"; fi
if [ -f /home/ally/.local/share/sddm/xorg-session.log ]; then
    cp /home/ally/.local/share/sddm/xorg-session.log "$output/roseshell-session.log"
fi
{
    cat /sys/class/tty/tty0/active
    ps -C Xorg -o args
    loginctl list-sessions
    loginctl seat-status seat0
    ps -eo pid,user,etimes,args | grep -E 'roseshell|openbox|sddm|Xorg'
} > "$output/seat-state.log"
