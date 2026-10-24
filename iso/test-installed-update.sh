#!/bin/sh
# Somente a VM descartável criada para validação; não toca a VM de desenvolvimento.
set -eu
test "$(hostname)" = allyos-test
test "$(id -u)" = 0
test -f /mnt/allyos-src/iso/release.json
python3 /mnt/allyos-src/iso/verify-image-packages.py / /mnt/allyos-output/installed-integrity
python3 - <<'PY'
from pathlib import Path
p = Path('/etc/sddm.conf.d/10-allyos.conf')
s = p.read_text()
if 'InputMethod=' not in s:
    s = s.replace('[General]\n', '[General]\nInputMethod=\n')
p.write_text(s)
p = Path('/usr/share/sddm/themes/allyos/theme.conf')
p.write_text(p.read_text().replace('Language=auto', 'Language=pt_BR'))
PY
printf '\nLOGIN_FIX_APPLIED\n' > /mnt/allyos-output/login-fix-applied.txt
systemctl restart sddm
