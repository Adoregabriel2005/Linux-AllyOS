"""Read-only acceptance checks in a newly installed AllyOS, not the Live image."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

profile = sys.argv[1]
assert profile in ('full', 'minimal')
checks = {}


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def installed(name):
    result = subprocess.run(['dpkg-query', '-W', '-f=${Status}', name],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.returncode == 0 and result.stdout == 'install ok installed'


release = dict(line.split('=', 1) for line in Path('/usr/lib/os-release').read_text().splitlines())
assert release['ID'] == 'allyos' and release['ID_LIKE'] == 'debian'
checks['version'] = release['VERSION_ID'].strip('"')
assert Path('/var/lib/allyos/install-profile').read_text().strip() == profile
assert command('findmnt', '-n', '-o', 'FSTYPE', '/') != 'overlay', 'Ainda no Live'
assert not Path('/usr/share/applications/allyos-install.desktop').exists()
assert not installed('calamares') and not installed('calamares-settings-debian')
for package in ('allyos-desktop', 'allyos-branding', 'linux-image-amd64', 'sddm',
                'openbox', 'thunar', 'xfce4-taskmanager', 'supertux', 'mate-polkit'):
    assert installed(package), package
if profile == 'full':
    for package in ('allyos-apps', 'firefox-esr', 'firefox-esr-l10n-pt-br', 'wine64',
                    'wine32:i386', 'tux-manager', 'hardinfo2', 'fastfetch', 'neofetch', 'lm-sensors'):
        assert installed(package), package
else:
    for package in ('allyos-apps', 'firefox-esr', 'wine64', 'wine32:i386', 'tux-manager', 'hardinfo2'):
        assert not installed(package), package
checks['profile'] = profile
checks['boot'] = 'UEFI' if Path('/sys/firmware/efi').exists() else 'BIOS'
assert Path('/boot/grub/grub.cfg').is_file()
assert 'roseshell' in command('pgrep', '-af', '/usr/lib/roseshell/main.py')
assert command('pgrep', '-x', 'openbox')
assert command('pgrep', '-f', '/usr/libexec/polkit-mate-authentication-agent-1')
checks['root_filesystem'] = command('findmnt', '-n', '-o', 'SOURCE,FSTYPE', '/')
checks['failed_units'] = command('systemctl', '--failed', '--no-legend', '--no-pager')
checks['audio_server'] = command('pactl', 'info')
checks['default_sink'] = command('pactl', 'get-default-sink')
assert checks['default_sink']
checks['accounts'] = [line.split(':')[0] for line in Path('/etc/passwd').read_text().splitlines()
                      if 1000 <= int(line.split(':')[2]) < 65534]
assert 'ally' not in checks['accounts'], 'Conta temporária Live permaneceu'
checks['passed'] = True
print(json.dumps(checks, ensure_ascii=False, indent=2))
