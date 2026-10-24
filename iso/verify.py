"""Verificação do conteúdo preparado, sem root e sem alterar a identidade do host."""
import ast
import json
from pathlib import Path
import shlex
import sys
import tarfile

output = Path(sys.argv[1]).resolve()
root = Path(__file__).resolve().parents[1]
release = json.loads((root / 'iso/release.json').read_text())
staging = output / 'staging'
branding = staging / 'allyos-branding'
desktop = staging / 'allyos-desktop'
values = {}
for line in (branding / 'usr/lib/os-release').read_text().splitlines():
    key, value = line.split('=', 1)
    values[key] = shlex.split(value)[0]
assert values['ID'] == 'allyos' and values['ID_LIKE'] == 'debian'
assert values['VERSION_ID'] == release['version']
assert 'Debian 13' in values['PRETTY_NAME'] and values['VERSION_CODENAME'] == 'trixie'
assert not (branding / 'etc/debian_version').exists(), 'Não substituir versão da base Debian'
runtime = desktop / 'usr/lib/roseshell'
for path in runtime.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'))
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        module = node.module if isinstance(node, ast.ImportFrom) else None
        if module and (root / 'shell' / (module + '.py')).is_file():
            assert (runtime / (module + '.py')).is_file(), module
assert not (runtime / '.venv').exists()
assert not (desktop / 'home').exists(), 'Não incluir contas nem dados da VM'
assert 'LXQt' not in (desktop / 'usr/share/xsessions/roseshell.desktop').read_text()
assert 'roseshell.desktop' in (desktop / 'DEBIAN/postinst').read_text()
assert 'dpkg-divert' in (branding / 'DEBIAN/preinst').read_text()
assert 'remove|purge' in (branding / 'DEBIAN/postrm').read_text()
assert (runtime / 'LICENSE').read_bytes() == (root / 'LICENSE').read_bytes()
assert (branding / 'usr/share/sddm/themes/allyos/background.png').is_file()
wallpapers = list((runtime / 'assets/wallpapers').glob('*.png'))
assert len(wallpapers) == 8
for wallpaper in wallpapers:
    for ratio in ('5x4', '4x3', '16x9'):
        assert (runtime / 'assets/wallpapers/variants' / ratio / wallpaper.name).is_file()
assert 'InputMethod=\n' in (branding / 'etc/sddm.conf.d/10-allyos.conf').read_text()
assert (runtime / 'assets/sounds/rose-entry.wav').stat().st_size < 100000
assert (staging / 'allyos-apps/DEBIAN/control').is_file()
assert 'wine' not in (desktop / 'DEBIAN/control').read_text().split('Depends: ', 1)[1].split('\n')[0].split(', ')
installer = output / 'config/includes.chroot/etc/calamares'
assert 'packagechooser' in (installer / 'settings.conf').read_text()
assert 'allowManualPartitioning: true' in (installer / 'modules/partition.conf').read_text()
fetch = json.loads((branding / 'etc/xdg/fastfetch/config.jsonc').read_text())
assert any(isinstance(m, dict) and m.get('format') == 'Debian GNU/Linux 13 (trixie)' for m in fetch['modules'])
archive = output / 'config/includes.binary/sources' / f'allyos-source-{release["version"]}.tar.gz'
with tarfile.open(archive) as bundle:
    names = bundle.getnames()
    assert 'iso/build.sh' in names and 'shell/main.py' in names
    assert not any(name.startswith(('vms/', 'iso/build-preview/', 'shell/.venv/')) for name in names)
print('ALLYOS CONTENT OK: versão, base Debian, sessão, login sem teclado virtual, 24 variantes, som, perfis, fontes e ausência de contas da VM')
