"""Verifica o atalho Print real do Openbox em display Xephyr isolado."""
import ctypes
import ctypes.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
session = subprocess.Popen([sys.executable, str(root / 'session.py')], start_new_session=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(1.5)
    x11 = ctypes.CDLL(ctypes.util.find_library('X11'))
    xtest = ctypes.CDLL(ctypes.util.find_library('Xtst'))
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x11.XKeysymToKeycode.restype = ctypes.c_uint
    x11.XFlush.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    xtest.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    display = x11.XOpenDisplay(None)
    assert display
    key = x11.XKeysymToKeycode(display, 0xff61)
    xtest.XTestFakeKeyEvent(display, key, 1, 0)
    xtest.XTestFakeKeyEvent(display, key, 0, 0)
    x11.XFlush(display)
    x11.XCloseDisplay(display)
    time.sleep(1.5)
    result = subprocess.run(['pgrep', '-f', str(root / 'capture.py')], capture_output=True)
    assert result.returncode == 0, 'Print não iniciou a ferramenta de captura'
    print('PRINT OK: Openbox iniciou roseshell-capture', flush=True)
finally:
    os.killpg(session.pid, signal.SIGTERM)
    session.wait(timeout=5)
