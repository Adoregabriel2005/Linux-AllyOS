"""RoseShell: área de trabalho e integração EWMH para sessão X11."""
from i18n import tr
import ctypes
import ctypes.util
import os

from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QColor, QPainter, QPixmap, QFont, QImageReader
from PySide6.QtWidgets import QWidget
from wallpapers import wallpaper_variant
from shortcuts import Shortcut, read_shortcuts


def property32(window, name, values, kind='CARDINAL'):
    if os.environ.get('QT_QPA_PLATFORM') == 'offscreen' or not os.environ.get('DISPLAY'):
        return
    lib = ctypes.CDLL(ctypes.util.find_library('X11'))
    lib.XOpenDisplay.restype = ctypes.c_void_p
    lib.XOpenDisplay.argtypes = [ctypes.c_char_p]
    lib.XInternAtom.restype = ctypes.c_ulong
    lib.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.XChangeProperty.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong,
                                  ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
    lib.XCloseDisplay.argtypes = [ctypes.c_void_p]
    display = lib.XOpenDisplay(None)
    if not display:
        return
    try:
        atom = lambda text: lib.XInternAtom(display, text.encode(), 0)
        data = (ctypes.c_ulong * len(values))(*[
            atom(value) if isinstance(value, str) else value for value in values])
        lib.XChangeProperty(display, int(window), atom(name), atom(kind), 32, 0,
                            ctypes.cast(data, ctypes.POINTER(ctypes.c_ubyte)), len(values))
    finally:
        lib.XCloseDisplay(display)


class Desktop(QWidget):
    def __init__(self, screen, settings, panel=None):
        super().__init__()
        self.screen = screen
        self.settings = settings
        self.panel = panel
        self.image_path = None
        self.image = QPixmap()
        self.background = QPixmap()
        self.cache_key = None
        self.shortcut_widgets = []
        self.setWindowTitle(tr('RoseShell — área de trabalho'))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnBottomHint |
                            Qt.WindowType.Tool)
        self.setGeometry(screen.geometry())
        screen.geometryChanged.connect(self.setGeometry)

    def showEvent(self, event):
        super().showEvent(event)
        property32(self.winId(), '_NET_WM_WINDOW_TYPE', ['_NET_WM_WINDOW_TYPE_DESKTOP'], 'ATOM')
        property32(self.winId(), '_NET_WM_DESKTOP', [0xffffffff])
        self.lower()

    def contextMenuEvent(self, event):
        if self.panel is not None:
            self.panel.desktop_menu(event.globalPos())

    def rebuild_shortcuts(self):
        for widget in self.shortcut_widgets:
            widget.hide()
            widget.deleteLater()
        self.shortcut_widgets = []
        if self.panel is None or self.settings.value('show_desktop_icons', 'true') != 'true':
            return
        from PySide6.QtWidgets import QApplication
        names = [screen.name() for screen in QApplication.screens()]
        primary = QApplication.primaryScreen().name()
        for entry in read_shortcuts(self.settings):
            monitor = entry.get('monitor', primary)
            if monitor not in names:
                monitor = primary
            if monitor != self.screen.name():
                continue
            widget = Shortcut(self, entry)
            self.shortcut_widgets.append(widget)
        cell_width = max((w.width() for w in self.shortcut_widgets), default=116) + 8
        cell_height = max((w.height() for w in self.shortcut_widgets), default=100) + 8
        rows = max(1, (self.height() - 16) // cell_height)
        occupied = []
        for index, widget in enumerate(self.shortcut_widgets):
            def slot(number):
                return self.clamp_icon(widget, QPoint(68 + (number // rows) * cell_width,
                                                     8 + (number % rows) * cell_height))
            widget.restore_position(slot(index))
            if any(widget.geometry().intersects(rect) for rect in occupied):
                for number in range(max(1, self.width() // cell_width) * rows):
                    widget.move(slot(number))
                    if not any(widget.geometry().intersects(rect) for rect in occupied):
                        break
            occupied.append(widget.geometry())
            widget.show()

    def clamp_icon(self, widget, point):
        left, right = 8, self.width() - widget.width() - 8
        if self.panel is not None and self.screen == self.panel.screen():
            if self.panel.side == 'left':
                left += self.panel.width()
            else:
                right -= self.panel.width()
        return QPoint(max(left, min(point.x(), max(left, right))),
                      max(8, min(point.y(), max(8, self.height() - widget.height() - 8))))

    def arrange_shortcuts(self):
        width = max((w.width() for w in self.shortcut_widgets), default=116) + 8
        height = max((w.height() for w in self.shortcut_widgets), default=100) + 8
        for index, widget in enumerate(self.shortcut_widgets):
            rows = max(1, (self.height() - 16) // height)
            widget.move(self.clamp_icon(widget, QPoint(68 + (index // rows) * width,
                                                     8 + (index % rows) * height)))
            widget.save_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.rebuild_shortcuts()

    def paintEvent(self, event):
        light = self.settings.value('theme', 'dark') == 'light'
        path = str(wallpaper_variant(self.settings.value('wallpaper', ''), self.width(), self.height(),
                                    self.settings.value('wallpaper_aspect', 'auto')))
        mode = self.settings.value('wallpaper_mode', 'fit')
        economical = self.settings.value('performance', 'economy') == 'economy'
        key = (path, mode, light, economical, self.width(), self.height(), self.devicePixelRatioF())
        if key != self.cache_key:
            self.render_background(path, mode, light, economical)
            self.cache_key = key
        p = QPainter(self)
        p.drawPixmap(0, 0, self.background)
        p.end()

    def render_background(self, path, mode, light, economical):
        factor = self.devicePixelRatioF()
        self.background = QPixmap(round(self.width() * factor), round(self.height() * factor))
        self.background.setDevicePixelRatio(factor)
        p = QPainter(self.background)
        light = self.settings.value('theme', 'dark') == 'light'
        p.fillRect(self.rect(), QColor('#e5e1d8' if light else '#202527'))
        reader = QImageReader(path)
        original = reader.size()
        if mode != 'center' and original.isValid():
            target = QSize(round(self.width() * factor), round(self.height() * factor))
            ratio = Qt.AspectRatioMode.KeepAspectRatioByExpanding if mode == 'fill' else Qt.AspectRatioMode.KeepAspectRatio
            reader.setScaledSize(target if mode == 'stretch' else original.scaled(target, ratio))
        image = QPixmap.fromImage(reader.read())
        image.setDevicePixelRatio(factor)
        if not image.isNull():
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, not economical)
            if mode == 'stretch':
                target = self.size()
            elif mode == 'center':
                target = image.size() / image.devicePixelRatio()
            else:
                ratio = (Qt.AspectRatioMode.KeepAspectRatioByExpanding if mode == 'fill'
                         else Qt.AspectRatioMode.KeepAspectRatio)
                target = image.size().scaled(self.size(), ratio)
            rect = QRect(0, 0, int(target.width()), int(target.height()))
            rect.moveCenter(self.rect().center())
            p.drawPixmap(rect, image)
        else:
            # Composição vetorial original, sem assets de terceiros ou efeitos 3D.
            p.setPen(QColor('#b8b5aa' if light else '#394544'))
            for offset in range(0, self.width() + self.height(), 80):
                p.drawLine(offset, 0, 0, offset)
            p.fillRect(self.width() - 210, 70, 140, 5, QColor('#bc8c94'))
            p.setPen(QColor('#414a46' if light else '#b5c5ba'))
            p.setFont(QFont('Sans Serif', 30))
            p.drawText(self.rect().adjusted(85, 0, -70, -85),
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, 'RoseShell')
        p.end()
