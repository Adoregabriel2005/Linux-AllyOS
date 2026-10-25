"""Seed only immutable .deb downloads; never copy stage flags or a root filesystem."""
import json
import os
from pathlib import Path
import subprocess

assert os.geteuid() == 0
assert subprocess.check_output(['hostname'], text=True).strip() == 'allyos-test'
base = Path('/srv/allyos-builder')
assert subprocess.check_output(['findmnt', '-n', '-o', 'SOURCE', str(base)], text=True).strip() == '/dev/sdb'
release = json.loads(Path('/mnt/allyos-src/iso/release.json').read_text())
target = base / ('build-' + release['version'])
assert not target.exists(), 'A fresh build directory is required'
target.mkdir()
(target / 'allyos-build.json').write_text(json.dumps(release))
count = 0
for previous in ('build-0.2.1', 'build-0.3.2'):
    for kind in ('packages.bootstrap', 'packages.chroot'):
        source = base / previous / 'cache' / kind
        destination = target / 'cache' / kind
        destination.mkdir(parents=True, exist_ok=True)
        for package in source.glob('*.deb'):
            if package.name.startswith('allyos-') or package.is_symlink():
                continue
            saved = destination / package.name
            if not saved.exists():
                os.link(package, saved)
                count += 1
assert not (target / '.build').exists() and not (target / 'chroot').exists()
print('Fresh build directory; cached Debian packages:', count)
