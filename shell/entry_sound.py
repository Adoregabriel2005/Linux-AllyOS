"""Som de entrada; processo curto, sem repetir após falha da UI."""
import os
from pathlib import Path
import shutil
import subprocess
import time


def play():
    from PySide6.QtCore import QSettings
    if QSettings('RoseShell', 'Desktop').value('entry_sound', 'true') != 'true':
        return
    sounds = Path(__file__).parent / 'assets/sounds'
    source = sounds / 'startup-local.wav'
    if not source.is_file():
        source = sounds / 'rose-entry.wav'
    if not source.is_file() or not shutil.which('paplay'):
        return
    # PipeWire pode ainda estar iniciando no primeiro login.
    for _ in range(6):
        try:
            result = subprocess.run(['paplay', '--volume=22000', str(source)],
                                    timeout=30, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return
        except (OSError, subprocess.TimeoutExpired):
            return
        time.sleep(1)


if __name__ == '__main__':
    if not os.environ.get('ROSESHELL_NESTED'):
        play()
