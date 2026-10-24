"""Clique de teste dentro do X11 convidado; coordenadas obtidas da captura da VM."""
import ctypes
import ctypes.util
import sys

x, y = map(int, sys.argv[1:3])
assert 0 <= x < 16384 and 0 <= y < 16384
x11 = ctypes.CDLL(ctypes.util.find_library('X11'))
test = ctypes.CDLL(ctypes.util.find_library('Xtst'))
x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
x11.XOpenDisplay.restype = ctypes.c_void_p
x11.XFlush.argtypes = [ctypes.c_void_p]
x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
test.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
test.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
display = x11.XOpenDisplay(None)
assert display
try:
    assert test.XTestFakeMotionEvent(display, -1, x, y, 0)
    assert test.XTestFakeButtonEvent(display, 1, 1, 0)
    assert test.XTestFakeButtonEvent(display, 1, 0, 0)
    x11.XFlush(display)
finally:
    x11.XCloseDisplay(display)
