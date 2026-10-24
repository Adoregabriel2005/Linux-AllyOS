#!/bin/sh
set -eu
preview="$HOME/allyos-login-preview"
if [ -f /mnt/allyos-output/login-preview.pid ]; then
    old_pid=$(cat /mnt/allyos-output/login-preview.pid)
    case "$old_pid" in ''|*[!0-9]*) ;; *)
        if [ -r "/proc/$old_pid/cmdline" ] && grep -qa 'sddm-greeter-qt6' "/proc/$old_pid/cmdline"; then
            kill "$old_pid"
        fi
    esac
fi
mkdir -p "$preview"
version=$(python3 -c 'import json; print(json.load(open("/mnt/allyos-src/iso/release.json"))["version"])')
builder=${ALLYOS_BUILD_DIR:-"$HOME/allyos-build"}
dpkg-deb -x "$builder/config/packages.chroot/allyos-branding_${version}-1_all.deb" "$preview"
cp /mnt/allyos-src/iso/sddm/Main.qml "$preview/usr/share/sddm/themes/allyos/Main.qml"
printf '\nPreviewMode=true\n' >> "$preview/usr/share/sddm/themes/allyos/theme.conf"
QT_QUICK_BACKEND=software DISPLAY=:1 sddm-greeter-qt6 --test-mode --theme "$preview/usr/share/sddm/themes/allyos" > /mnt/allyos-output/login-preview.log 2>&1 &
echo "$!" > /mnt/allyos-output/login-preview.pid
echo 'ALLYOS LOGIN TEST STARTED'
