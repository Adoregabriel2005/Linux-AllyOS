"""Integração real com Openbox: listar, ativar e fechar janelas sem encerrar o desktop."""
import os
import sys
import subprocess
import tempfile
import ctypes
import ctypes.util
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget

temporary = tempfile.TemporaryDirectory()
os.environ['XDG_CONFIG_HOME'] = temporary.name
from main import Panel

app = QApplication([])
sys.argv.append('--session')
panel = Panel()
panel.show()
windows = [QWidget(), QWidget()]
for index, window in enumerate(windows):
    window.setWindowTitle(f'Rose integration {index}')
    window.resize(250, 180)
    window.show()
completed = []

def check():
    ids = [f'0x{int(w.winId()):08x}' for w in windows]
    for identity in ids:
        assert identity in panel.tasks.buttons, (identity, panel.tasks.buttons)
    panel.tasks.command(['-ia', ids[0]])
    QTimer.singleShot(500, lambda: activated(ids))

def activated(ids):
    active = subprocess.check_output(['xprop', '-root', '_NET_ACTIVE_WINDOW'], text=True)
    assert int(active.split()[-1], 16) == int(ids[0], 16), active
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
    alt = x11.XKeysymToKeycode(display, 0xffe9)
    tab = x11.XKeysymToKeycode(display, 0xff09)
    for key, pressed in [(alt, 1), (tab, 1), (tab, 0), (alt, 0)]:
        xtest.XTestFakeKeyEvent(display, key, pressed, 0)
        x11.XFlush(display)
        time.sleep(0.12)
    x11.XFlush(display)
    x11.XCloseDisplay(display)
    QTimer.singleShot(600, lambda: switched(ids))

def switched(ids):
    active = subprocess.check_output(['xprop', '-root', '_NET_ACTIVE_WINDOW'], text=True)
    assert int(active.split()[-1], 16) == int(ids[1], 16), (active, ids)
    for window in windows:
        window.close()
    QTimer.singleShot(1800, closed)

def closed():
    assert panel.isVisible() and all(d.isVisible() for d in panel.desktops)
    assert not any('Rose integration' in b.toolTip() for b in panel.tasks.buttons.values())
    panel.open_preferences()
    panel.preferences.close()
    QTimer.singleShot(500, finish)

def finish():
    assert panel.isVisible()
    print('TASKS OK: duas janelas, ativacao, Alt+Tab, remocao ao fechar, desktop e configuracoes ativos', flush=True)
    completed.append(True)
    app.quit()

QTimer.singleShot(2200, check)
QTimer.singleShot(12000, app.quit)
app.exec()
assert completed, 'Teste de janelas nao completou'
