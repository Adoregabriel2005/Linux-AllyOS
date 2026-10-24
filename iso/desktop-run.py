"""Comando de teste no X11 da conta descartável; nunca instalado na sessão."""
import os
from pathlib import Path
import re
import subprocess
import sys

environment = dict(os.environ)
found = False
for process in Path('/proc').glob('[0-9]*'):
    try:
        if process.stat().st_uid != os.getuid():
            continue
        if b'/usr/lib/roseshell/main.py' not in (process / 'cmdline').read_bytes():
            continue
        for value in (process / 'environ').read_bytes().split(bytes([0])):
            key, sep, data = value.partition(b'=')
            if sep and key in (b'DISPLAY', b'XAUTHORITY', b'DBUS_SESSION_BUS_ADDRESS',
                               b'QT_QPA_PLATFORMTHEME', b'GTK_THEME', b'QT_SCALE_FACTOR',
                               b'XDG_CURRENT_DESKTOP', b'XDG_SESSION_DESKTOP',
                               b'XDG_SESSION_TYPE', b'LANG', b'LC_ALL', b'LC_MESSAGES', b'PATH'):
                environment[key.decode()] = data.decode()
        found = True
        break
    except OSError:
        continue
assert found and environment.get('DISPLAY'), 'Sessão RoseShell da conta de teste ausente'
arguments = sys.argv[1:]
if arguments and arguments[0] == '--detach':
    arguments = arguments[1:]
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', Path(arguments[0]).name)
    with open('/mnt/allyos-output/' + name + '-desktop.log', 'w') as log:
        process = subprocess.Popen(arguments, env=environment, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    print('PID', process.pid)
else:
    os.execvpe(arguments[0], arguments, environment)
