"""Read-only audit of the actual ISO filesystem before any public upload."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('image', type=Path)
parser.add_argument('report', type=Path)
args = parser.parse_args()
image = args.image.resolve()
version = json.loads(Path('/mnt/allyos-src/iso/release.json').read_text())['version']
assert os.geteuid() == 0 and image.is_file()
report = {'passed': False, 'image': image.name}
with tempfile.TemporaryDirectory(prefix='allyos-iso-audit-') as directory:
    media = Path(directory)
    subprocess.run(['mount', '-o', 'loop,ro', str(image), str(media)], check=True)
    try:
        filesystem = media / 'live/filesystem.squashfs'
        assert filesystem.is_file()

        def read(name):
            return subprocess.check_output(['unsquashfs', '-cat', str(filesystem), name])

        listing = subprocess.check_output(['unsquashfs', '-ll', str(filesystem)], text=True)
        assert 'startup-local.wav' not in listing
        assert 'vm-command-bridge.py' not in listing
        assert not re.search(r'squashfs-root/(?:usr/)?lib/firmware/b43(?:legacy)?(?:/|$)', listing, re.MULTILINE)
        report['restricted_b43_firmware_absent'] = True
        report['local_audio_absent'] = True
        identity = read('usr/lib/os-release').decode()
        assert 'ID=allyos\n' in identity and f'VERSION_ID="{version}"' in identity and 'ID_LIKE=debian' in identity
        report['identity'] = identity
        accounts = [line.split(':')[0] for line in read('etc/passwd').decode().splitlines()
                    if 1000 <= int(line.split(':')[2]) < 65534]
        assert not accounts, accounts
        report['personal_accounts_absent'] = True
        for name in ('applications.py', 'hardware_capabilities.py', 'diagnostics.py', 'system_ui.py'):
            assert read('usr/lib/roseshell/' + name) == (Path('/mnt/interface-src') / name).read_bytes(), name
        report['reviewed_runtime_matches_source'] = True
        statuses = {}
        for paragraph in read('var/lib/dpkg/status').decode().split('\n\n'):
            fields = dict(line.split(': ', 1) for line in paragraph.splitlines() if ': ' in line and not line.startswith(' '))
            if 'Package' not in fields:
                continue
            name = fields['Package']
            if fields.get('Architecture') == 'i386':
                name += ':i386'
            status = fields.get('Status', '')
            assert not status.startswith('install ') or status == 'install ok installed', (name, status)
            statuses[name] = fields
        for name in ('allyos-desktop', 'allyos-branding', 'allyos-apps', 'tux-manager', 'firefox-esr',
                     'wine64', 'wine32:i386', 'fastfetch', 'neofetch', 'hardinfo2', 'supertux'):
            assert statuses[name]['Status'] == 'install ok installed', name
        report['core_packages'] = {name: statuses[name]['Version'] for name in
                                  ('allyos-desktop', 'tux-manager', 'firefox-esr', 'wine64', 'wine32:i386')}
        cleanup = yaml.safe_load(read('etc/calamares/modules/packages.conf'))
        cleanup_packages = [name for operation in cleanup['operations'] for name in operation.get('remove', [])]
        for name in cleanup_packages:
            assert statuses.get(name, {}).get('Status') == 'install ok installed', ('installer cleanup', name)
        report['installer_cleanup_packages_installed'] = cleanup_packages
        assert (media / f'sources/allyos-source-{version}.tar.gz').is_file()
        pool = list((media / 'pool').rglob('*.deb'))
        assert any(path.name.startswith('grub-pc_') for path in pool)
        assert any(path.name.startswith('grub-efi_') for path in pool)
        report['offline_bootloader_packages'] = True
        report['passed'] = True
    finally:
        subprocess.run(['umount', str(media)], check=True)
with image.open('rb') as stream:
    report['image_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
