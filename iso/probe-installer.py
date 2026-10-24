"""Carrega o Calamares real sem iniciar instalação; exige Debian de teste."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import yaml
from installer import prepare_installer
from prepare import RELEASE

output = Path(sys.argv[1])
output.mkdir(parents=True, exist_ok=True)
prepare_installer(output, RELEASE['version'])
source = output / 'config/includes.chroot/etc/calamares'
for file in source.rglob('*'):
    if file.suffix in ('.conf', '.desc'):
        yaml.safe_load(file.read_text())
with tempfile.TemporaryDirectory(prefix='allyos-installer-probe-') as temporary:
    target = Path(temporary) / 'config'
    shutil.copytree(source, target)
    (target / 'qml').symlink_to('/usr/share/calamares/qml', target_is_directory=True)
    log = output / 'calamares-probe.log'
    with log.open('w') as stream:
        result = subprocess.run(['timeout', '20s', 'calamares', '-D6', '-c', str(target)],
                                env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'},
                                stdout=stream, stderr=subprocess.STDOUT)
    data = log.read_text()
    assert result.returncode == 124, data[-6000:]
    assert 'ERROR: FATAL' not in data and 'ERROR: Module' not in data, data[-6000:]
    assert 'ViewModule "packagechooser@packagechooser" loading complete' in data
    assert 'contextualprocess@allyos-profile' in data
print('CALAMARES LOAD OK: YAML, branding e módulos; nenhuma instalação iniciada')
