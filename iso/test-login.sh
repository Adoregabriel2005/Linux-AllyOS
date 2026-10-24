#!/bin/sh
set -eu
test ! -e /tmp/.X2-lock || { echo 'Display :2 já está em uso; teste cancelado.'; exit 1; }
theme="$HOME/allyos-login-preview/usr/share/sddm/themes/allyos"
cp /mnt/allyos-src/iso/sddm/Main.qml "$theme/Main.qml"
printf '\nPreviewMode=true\n' >> "$theme/theme.conf"
Xephyr :2 -screen 640x480 -nolisten tcp > /mnt/allyos-output/greeter-x.log 2>&1 &
test_xpid=$!
test_gpid=''
cleanup() {
    [ -z "$test_gpid" ] || kill "$test_gpid" 2>/dev/null || true
    kill "$test_xpid" 2>/dev/null || true
}
trap cleanup EXIT
sleep 2
for language in pt_BR.UTF-8 C.UTF-8; do
    if [ "$language" = C.UTF-8 ]; then name=en; else name=pt; fi
    sed -i '/^Language=/d' "$theme/theme.conf"
    if [ "$name" = en ]; then printf '\nLanguage=en\n' >> "$theme/theme.conf"; else printf '\nLanguage=pt_BR\n' >> "$theme/theme.conf"; fi
    LC_ALL="$language" DISPLAY=:2 QT_QUICK_BACKEND=software sddm-greeter-qt6 --test-mode --theme "$theme" > "/mnt/allyos-output/greeter-$name.log" 2>&1 &
    test_gpid=$!
    sleep 3
    DISPLAY=:2 python3 - "$name" <<'PY'
import sys
from PySide6.QtWidgets import QApplication
app = QApplication([])
screen = app.primaryScreen()
assert screen.size().width() == 640 and screen.size().height() == 480
assert screen.grabWindow(0).save('/mnt/allyos-output/allyos-login-' + sys.argv[1] + '-640.png')
PY
    kill "$test_gpid"
    wait "$test_gpid" 2>/dev/null || true
    test_gpid=''
    if grep -E 'Unexpected token|is not installed|Fallback to embedded theme|ReferenceError|Binding loop' "/mnt/allyos-output/greeter-$name.log"; then exit 1; fi
done
echo 'GREETER TEST OK: PT/EN 640x480, software backend'
