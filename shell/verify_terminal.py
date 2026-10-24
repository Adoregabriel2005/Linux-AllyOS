"""Relatório em janela real: posição e tamanho cabem no monitor da prévia."""
import os
from pathlib import Path
import shlex
import subprocess
import time

root = Path(__file__).resolve().parent
command = shlex.join(['sh', str(root / 'diagnostic-terminal.sh'), 'fastfetch'])
process = subprocess.Popen(['qterminal', '-e', command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(2)
    assert process.poll() is None, 'Relatorio fechou antes de poder ser lido'
    rows = subprocess.check_output(['wmctrl', '-lpG'], text=True).splitlines()
    row = next(line.split(None, 8) for line in rows if line.split()[2] == str(process.pid))
    x, y, width, height = map(int, row[3:7])
    geometry = subprocess.check_output(['xwininfo', '-root'], text=True)
    screen_width = int(next(line.split(':')[1] for line in geometry.splitlines() if line.strip().startswith('Width:')))
    screen_height = int(next(line.split(':')[1] for line in geometry.splitlines() if line.strip().startswith('Height:')))
    assert 0 <= x and 0 <= y and x + width <= screen_width and y + height <= screen_height, row
    print('TERMINAL OK: Fastfetch permanece aberto e cabe na tela', x, y, width, height, flush=True)
finally:
    process.terminate()
    process.wait(timeout=3)
