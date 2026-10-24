#!/bin/sh
# Read-only checks inside the booted AllyOS image; no partitioning or passwords.
set -eu
echo '=== AllyOS Live: identity and runtime ==='
cat /etc/os-release
grep -q '^ID=allyos$' /etc/os-release
grep -q '^ID_LIKE=debian$' /etc/os-release
grep -q '^VERSION_CODENAME=trixie$' /etc/os-release
cat /etc/debian_version
test -x /usr/bin/roseshell-session
test -f /usr/share/xsessions/roseshell.desktop
test -f /usr/share/sddm/themes/allyos/Main.qml
test -f /usr/share/allyos/package-versions.txt
python3 -c 'import PySide6.QtWidgets; import shiboken6; print("PySide6", PySide6.__version__)'
for command in openbox thunar fastfetch neofetch nmcli wmctrl sensors inxi lshw; do
    command -v "$command"
done
test -x /usr/games/supertux2
dpkg-query -W allyos-desktop allyos-branding tux-manager neofetch
test "$(find /usr/lib/roseshell/assets/wallpapers/variants -name '*.png' | wc -l)" -eq 24
echo '=== Desktop processes ==='
pgrep -af '/usr/lib/roseshell/(main|session).py'
pgrep -x openbox
echo '=== Display and network ==='
xrandr --current
nmcli -t -f DEVICE,TYPE,STATE device
getent ahostsv4 deb.debian.org
echo '=== Fetch identity ==='
fastfetch --logo none --structure os:kernel:de:wm:memory
neofetch --stdout --disable host kernel uptime packages shell resolution de wm wm_theme theme icons terminal terminal_font cpu gpu memory
echo '=== Failed system units (review each entry) ==='
systemctl --failed --no-pager
echo 'LIVE CHECKS PASSED; installation, authentication and physical GPUs need separate tests.'
