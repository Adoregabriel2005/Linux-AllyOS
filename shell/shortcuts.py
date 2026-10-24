"""Atalhos de aplicativos móveis, com posições relativas persistentes."""
from i18n import tr
import hashlib
import json
from pathlib import Path

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QFontMetrics
from PySide6.QtWidgets import QApplication, QWidget, QMenu
from icons import illustrated_icon
from applications import desktop_icon


def read_shortcuts(settings):
    try:
        value = json.loads(settings.value('desktop_shortcuts', '[]'))
        return [entry for entry in value if isinstance(entry, dict) and
                all(isinstance(entry.get(key), str) for key in ('path', 'name', 'icon'))]
    except (ValueError, TypeError):
        return []


def app_icon(app):
    name = app['name'].casefold()
    if any(word in name for word in ('pcman', 'thunar', 'arquivos')):
        return illustrated_icon('files')
    if any(word in name for word in ('featherpad', 'mousepad', 'texto')):
        return illustrated_icon('editor')
    if 'wine' in name:
        return illustrated_icon('wine')
    image = desktop_icon(app['icon'])
    return illustrated_icon('apps') if image.isNull() else image


class Shortcut(QWidget):
    def __init__(self, desktop, app):
        super().__init__(desktop)
        self.desktop = desktop
        self.app = app
        self.art = app_icon(app)
        self.icon_size = int(desktop.settings.value('desktop_icon_size', 48))
        self.icon_size = max(24, min(self.icon_size, 96))
        self.label_font = QFont('Sans Serif', 9)
        self.label_font.setBold(True)
        width = max(116, self.icon_size + 24)
        self.label_flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap
        label = QFontMetrics(self.label_font).boundingRect(0, 0, width - 8, 2000,
                                                         int(self.label_flags), app['name'])
        self.setFixedSize(width, self.icon_size + max(34, label.height()) + 12)
        self.setToolTip(app['name'] + tr('\nArraste para mover · duplo clique para abrir'))
        self.setAccessibleName(app['name'])
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.dragging = False
        self.origin = None
        identity = hashlib.sha256(app['path'].encode()).hexdigest()[:24]
        self.key = f'icon_positions/{desktop.screen.name()}/{identity}'

    def paintEvent(self, event):
        p = QPainter(self)
        if self.hasFocus():
            p.fillRect(self.rect(), QColor(25, 28, 30, 120))
            p.setPen(QColor('#c58f9d'))
            p.drawRect(self.rect().adjusted(0, 0, -1, -1))
        self.art.paint(p, (self.width() - self.icon_size) // 2, 3, self.icon_size, self.icon_size)
        p.setFont(self.label_font)
        rect = self.rect().adjusted(2, self.icon_size + 6, -2, -2)
        flags = self.label_flags
        text = self.app['name']
        p.setPen(QColor('#16191b'))
        p.drawText(rect.translated(1, 1), flags, text)
        p.setPen(QColor('#fff2de'))
        p.drawText(rect, flags, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            self.origin = event.position().toPoint()
            self.start = event.globalPosition().toPoint()
            self.dragging = False
            self.update()

    def mouseMoveEvent(self, event):
        if self.origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if (event.globalPosition().toPoint() - self.start).manhattanLength() >= QApplication.startDragDistance():
                self.dragging = True
            if self.dragging:
                position = self.desktop.mapFromGlobal(event.globalPosition().toPoint()) - self.origin
                self.move(self.desktop.clamp_icon(self, position))

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.save_position()
        self.origin = None
        self.dragging = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.desktop.panel.launch_shortcut(self.app)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.desktop.panel.launch_shortcut(self.app)
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            delta = {Qt.Key.Key_Left: QPoint(-10, 0), Qt.Key.Key_Right: QPoint(10, 0),
                     Qt.Key.Key_Up: QPoint(0, -10), Qt.Key.Key_Down: QPoint(0, 10)}[event.key()]
            self.move(self.desktop.clamp_icon(self, self.pos() + delta))
            self.save_position()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.update()

    def save_position(self):
        x = self.x() / max(1, self.desktop.width() - self.width())
        y = self.y() / max(1, self.desktop.height() - self.height())
        self.desktop.settings.setValue(self.key, json.dumps([x, y]))

    def restore_position(self, fallback):
        try:
            position = json.loads(self.desktop.settings.value(self.key, 'null'))
            if not isinstance(position, list) or len(position) != 2:
                raise ValueError()
            x, y = [max(0, min(1, float(value))) for value in position]
            point = QPoint(round(x * max(1, self.desktop.width() - self.width())),
                           round(y * max(1, self.desktop.height() - self.height())))
        except (ValueError, TypeError):
            point = fallback
        self.move(self.desktop.clamp_icon(self, point))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(tr('Abrir'), lambda: self.desktop.panel.launch_shortcut(self.app))
        monitors = menu.addMenu(tr('Mover para monitor'))
        for screen in QApplication.screens():
            monitors.addAction(screen.name(), lambda checked=False, name=screen.name():
                               self.desktop.panel.move_shortcut(self.app['path'], name))
        menu.addAction(tr('Remover atalho'), lambda: self.desktop.panel.remove_shortcut(self.app['path']))
        menu.exec(event.globalPos())
