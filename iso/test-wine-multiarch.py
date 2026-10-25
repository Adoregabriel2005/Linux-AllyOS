"""Run Wine's own Windows executables in an isolated disposable prefix."""
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

with tempfile.TemporaryDirectory(prefix='allyos-wine-test-') as directory:
    prefix = Path(directory) / 'prefix'
    env = {**os.environ, 'WINEPREFIX': str(prefix), 'WINEDEBUG': '-all',
           'WINEDLLOVERRIDES': 'mscoree,mshtml='}
    try:
        subprocess.run(['wineboot', '--init'], env=env, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=100)
        results = {}
        for folder, machine, label in [('system32', 0x8664, '64'), ('syswow64', 0x14c, '32')]:
            executable = prefix / 'drive_c/windows' / folder / 'cmd.exe'
            data = executable.read_bytes()
            offset = struct.unpack_from('<I', data, 0x3c)[0]
            assert data[offset:offset + 4] == b'PE\0\0'
            assert struct.unpack_from('<H', data, offset + 4)[0] == machine
            result = subprocess.run(['wine', str(executable), '/c', 'echo ALLYOS_WINE_' + label],
                                    env=env, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=30)
            assert result.returncode == 0 and 'ALLYOS_WINE_' + label in result.stdout, result.stdout
            results[label] = {'pe_machine': hex(machine), 'output': result.stdout.strip()}
        print(json.dumps({'passed': True, 'wine': results}))
    finally:
        subprocess.run(['wineserver', '-k'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['wineserver', '-w'], env=env, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=20)
