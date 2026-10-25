"""Read-only GPU capability checks; never install drivers or request elevation."""
from functools import lru_cache
from pathlib import Path
import re
import shutil
import subprocess
import time


def live_session():
    try:
        return 'boot=live' in Path('/proc/cmdline').read_text().split()
    except OSError:
        return False


def gpu_drivers():
    drivers = set()
    for device in Path('/sys/class/drm').glob('card[0-9]*/device/driver'):
        if re.fullmatch(r'card\d+', device.parent.parent.name):
            try:
                drivers.add(device.resolve(strict=True).name)
            except OSError:
                continue
    return tuple(sorted(drivers))


@lru_cache(maxsize=4)
def _probe_nvtop(executable, drivers, refresh_bucket):
    if not executable:
        return False, 'NVTOP não está instalado neste perfil.'
    virtual = {'vmwgfx', 'vboxvideo', 'virtio_gpu', 'bochs-drm', 'qxl', 'hyperv_drm'}
    if drivers and set(drivers).issubset(virtual):
        return False, 'A GPU virtual desta máquina não fornece métricas ao NVTOP. Consulte a GPU em Informações de hardware.'
    try:
        result = subprocess.run([executable, '--snapshot'], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, timeout=2)
    except (OSError, subprocess.TimeoutExpired):
        return False, 'Não foi possível consultar a GPU neste momento.'
    output = result.stdout.strip()
    # NVTOP 3.2 returns 0 even when there is no GPU. Exit status alone is insufficient.
    if result.returncode or not output or re.search(r'no\s+gpu', output, re.IGNORECASE):
        return False, 'O driver da GPU não forneceu métricas ao NVTOP. Consulte a GPU em Informações de hardware.'
    return True, ''


def nvtop_status():
    return _probe_nvtop(shutil.which('nvtop'), gpu_drivers(), int(time.monotonic() // 60))
