"""Regression cases: installed vs Live, missing tools and NVTOP's false success."""
import configparser
import os
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from applications import entry_is_available, installed_apps
from hardware_capabilities import _probe_nvtop, nvtop_status


def entry(command='true', extra=''):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string('[Desktop Entry]\nType=Application\nName=Demo\nExec=' + command + '\n' + extra)
    return parser['Desktop Entry']


with patch('hardware_capabilities.live_session', return_value=False):
    for name in ('qt6ct.desktop', 'qt5ct.desktop', 'obconf.desktop', 'kdesystemsettings.desktop',
                 'allyos-install.desktop', 'calamares-install-debian.desktop', 'debian-installer-launcher.desktop'):
        assert not entry_is_available(name, entry()), name
    assert entry_is_available('my-app.desktop', entry())
    assert not entry_is_available('missing.desktop', entry('allyos-program-that-does-not-exist'))
    assert not entry_is_available('missing.desktop', entry(extra='TryExec=allyos-program-that-does-not-exist\n'))
with patch('hardware_capabilities.live_session', return_value=True), patch('applications.shutil.which', return_value='/bin/true'):
    assert entry_is_available('allyos-install.desktop', entry())
    assert not entry_is_available('calamares-install-debian.desktop', entry())
with patch('hardware_capabilities.subprocess.run') as run:
    _probe_nvtop.cache_clear()
    assert not _probe_nvtop('/usr/bin/nvtop', ('vmwgfx',), 0)[0]
    run.assert_not_called()
    run.return_value = subprocess.CompletedProcess([], 0, 'No GPU to monitor.\n')
    assert not _probe_nvtop('/usr/bin/nvtop', ('nouveau',), 0)[0]
    run.return_value = subprocess.CompletedProcess([], 0, 'GPU 0: NVIDIA sample metrics\n')
    assert _probe_nvtop('/usr/bin/nvtop', ('nvidia',), 0)[0]
    run.side_effect = subprocess.TimeoutExpired('nvtop', 2)
    assert not _probe_nvtop('/usr/bin/nvtop', ('amdgpu',), 0)[0]
_probe_nvtop.cache_clear()
with tempfile.TemporaryDirectory() as directory:
    folder = Path(directory) / 'applications'
    folder.mkdir()
    for name, command in [('qt6ct', 'true'), ('calamares-install-debian', 'true'), ('ordinary', 'true'),
                          ('missing', 'allyos-program-that-does-not-exist')]:
        (folder / (name + '.desktop')).write_text('[Desktop Entry]\nType=Application\nName=' + name + '\nExec=' + command + '\n')
    with patch.dict(os.environ, XDG_DATA_HOME=directory, XDG_DATA_DIRS=directory):
        assert [app['name'] for app in installed_apps()] == ['ordinary']
available, reason = nvtop_status()
print('APPLICATION AVAILABILITY OK: one Live installer, no installed installer, no toolkit settings, missing executables excluded')
print('ACTUAL NVTOP:', available, reason)
