#!/bin/sh
# Recovery for this development VM after interruption in lb installer.
set -eu
test "$(id -u)" = 0
build=/home/goriga/allyos-trixie-build
cd "$build"
test "$(pwd -P)" = /home/goriga/allyos-trixie-build
test -f allyos-build.json
test -f .build/chroot_hooks
export DEBIAN_FRONTEND=noninteractive
python3 - <<'PY'
from pathlib import Path
import subprocess
rows = subprocess.check_output(['ps', '-eo', 'args'], text=True).splitlines()
if any('/usr/lib/live/build/' in row for row in rows):
    raise SystemExit('Outro processo live-build está ativo; recuperação cancelada.')
lock = Path('.lock')
if lock.is_symlink():
    raise SystemExit('Lock inesperado; recuperação cancelada.')
lock.unlink(missing_ok=True)
PY
if [ -f .build/installer_chroot ]; then
    grep -q '^ID=allyos$' chroot/chroot/usr/lib/os-release
    test -s chroot/chroot/usr/share/allyos/package-versions.txt
    python3 - <<'PY'
from pathlib import Path
import shutil
import time
base = Path.cwd().resolve()
indices = base / 'chroot/localArchive/aptdir/state/lists'
if indices.is_dir():
    assert indices.resolve().is_relative_to(base / 'chroot')
    saved = base / 'cache' / ('interrupted-udeb-lists-' + str(time.time_ns()))
    indices.rename(saved)
    indices.mkdir()
    (indices / 'partial').mkdir()
    print('Renewing installer package indices; old metadata preserved:', saved, flush=True)
for name in ('pkgcache.bin', 'srcpkgcache.bin'):
    cached = base / 'chroot/localArchive/aptdir/cache' / name
    if cached.is_file():
        cached.rename(base / 'cache' / (str(time.time_ns()) + '-' + name))
old = base / 'binary.deb'
downloads = base / 'chroot/binary.deb/archives'
if old.is_dir():
    assert old.resolve().parent == base and not old.is_symlink()
    downloads.mkdir(parents=True, exist_ok=True)
    for package in (old / 'archives').glob('*.deb'):
        target = downloads / package.name
        if not target.exists():
            shutil.copy2(package, target)
    saved = base / 'cache' / ('interrupted-binary-deb-' + str(time.time_ns()))
    old.rename(saved)
    print('Preserved interrupted installer download cache:', saved, flush=True)
PY
    # Restore helper mounts/config after reboot using the native operations.
    lb chroot_prep remove all mode-archives-chroot
    lb chroot_prep install all mode-archives-chroot
    chroot chroot /usr/bin/env DEBIAN_FRONTEND=noninteractive dpkg --configure -a
    lb installer
else
    grep -q '^ID=allyos$' chroot/usr/lib/os-release
    test -s chroot/usr/share/allyos/package-versions.txt
    lb installer
fi
python3 - <<'PY'
from pathlib import Path
import subprocess
result = subprocess.run(['chroot', 'chroot', 'dpkg', '--verify'], text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
Path('/mnt/allyos-output/image-integrity.log').write_text(result.stdout)
unexpected = [line for line in result.stdout.splitlines() if line.strip() and ' c ' not in line]
if result.returncode or unexpected:
    print(result.stdout, flush=True)
    raise SystemExit('Falha na integridade dos pacotes; ISO não será compactada.')
print('Package integrity verified; configuration differences recorded separately.', flush=True)
PY
sh /mnt/allyos-src/iso/finalize-session.sh
python3 - <<'PY'
from pathlib import Path
import runpy
runpy.run_path('/mnt/allyos-src/iso/prepare.py')['bundle_sources'](Path.cwd())
PY
lb binary
lb source
version=$(python3 -c 'import json; print(json.load(open("allyos-build.json"))["version"])')
image="AllyOS-$version-dev-amd64.iso"
test -f live-image-amd64.hybrid.iso
mv live-image-amd64.hybrid.iso "$image"
sha256sum "$image" > "$image.sha256"
cp "$image" "$image.sha256" /mnt/allyos-output/
echo "ISO gerada e exportada: $image"
