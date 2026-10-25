"""Testa limites de tela em X11 real aninhado, sem mudar o monitor do usuário."""
import os
from pathlib import Path
import subprocess
import sys
import time

source = Path('/mnt/interface-src')
environment = dict(os.environ)
for process in Path('/proc').glob('[0-9]*'):
    try:
        command = (process / 'cmdline').read_bytes()
        if b'/usr/lib/roseshell/main.py' in command:
            for value in (process / 'environ').read_bytes().split(b'\0'):
                key, sep, data = value.partition(b'=')
                if sep and key in (b'DISPLAY', b'XAUTHORITY', b'DBUS_SESSION_BUS_ADDRESS'):
                    environment[key.decode()] = data.decode()
            break
    except (OSError, PermissionError):
        continue
assert environment.get('DISPLAY'), 'Entrar na sessão gráfica de teste antes de executar'
environment.update(ROSESHELL_NESTED='1', ROSESHELL_LANGUAGE='pt_BR')
for size, scale in [('640x480', '1'), ('640x480', '1.25'), ('800x600', '1'),
                    ('1024x768', '1'), ('1280x720', '1'), ('1280x1024', '1'),
                    ('1366x768', '1'), ('1600x900', '1'), ('1920x1080', '1'),
                    ('2560x1440', '1'), ('3840x2160', '1')]:
    with open('/mnt/allyos-output/xephyr-resolution.log', 'w') as log:
        server = subprocess.Popen(['Xephyr', ':12', '-screen', size, '-ac', '-nolisten', 'tcp'],
                                  env=environment, stdout=log, stderr=subprocess.STDOUT)
        try:
            time.sleep(1)
            assert server.poll() is None, 'Xephyr não iniciou'
            result = subprocess.run(['python3', str(source / 'verify_resolution.py')],
                                    env={**environment, 'DISPLAY': ':12', 'QT_SCALE_FACTOR': scale},
                                    timeout=40)
            assert result.returncode == 0, (size, scale)
        finally:
            server.terminate()
            server.wait(timeout=5)
print('X11 RESOLUTIONS OK: 640x480 a 4K, 5:4 e 125%, incluindo som e dispositivos')
