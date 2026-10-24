"""Testes de atalhos: arraste, persistência, tamanho, visibilidade e cache."""
import json
import os
import tempfile
from pathlib import Path


def main():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['XDG_CONFIG_HOME'] = tmp
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PySide6.QtCore import QEvent, QPoint, QPointF, Qt, QCoreApplication
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtWidgets import QApplication
        from main import Panel
        import sys
        sys.argv.append('--session')
        app = QApplication([])
        panel = Panel()
        panel.show()
        source = Path(tmp) / 'demo.desktop'
        source.write_text('[Desktop Entry]\nType=Application\nName=Demo\nExec=true\n')
        entry = {'name': 'Demo', 'path': str(source), 'icon': ''}
        panel.add_shortcut(entry)
        desktop = next(d for d in panel.desktops if d.shortcut_widgets)
        widget = desktop.shortcut_widgets[0]
        start = widget.mapToGlobal(QPoint(10, 10))
        for event_type, local, global_point, button, buttons in [
            (QEvent.Type.MouseButtonPress, QPoint(10, 10), start, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton),
            (QEvent.Type.MouseMove, QPoint(110, 90), start + QPoint(100, 80), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton),
            (QEvent.Type.MouseButtonRelease, QPoint(110, 90), start + QPoint(100, 80), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton)]:
            event = QMouseEvent(event_type, QPointF(local), QPointF(global_point), button, buttons, Qt.KeyboardModifier.NoModifier)
            QApplication.sendEvent(widget, event)
        saved = json.loads(panel.settings.value(widget.key))
        assert all(0 <= value <= 1 for value in saved)
        original = widget.pos()
        desktop.rebuild_shortcuts()
        assert desktop.shortcut_widgets[0].pos() == original
        for size in (24, 96, 48):
            panel.set_desktop_icon_size(size)
            assert desktop.shortcut_widgets[0].icon_size == size
        panel.show_desktop_icons(False)
        assert not desktop.shortcut_widgets
        panel.show_desktop_icons(True)
        assert len(desktop.shortcut_widgets) == 1
        panel.arrange_shortcuts()
        desktop.grab()
        key = desktop.background.cacheKey()
        desktop.grab()
        assert desktop.background.cacheKey() == key, 'Wallpaper redesenhado sem necessidade'
        panel.remove_shortcut(str(source))
        assert not desktop.shortcut_widgets and source.exists()
        panel.status.shutdown()
        panel.timer.stop()
        panel.rotation_timer.stop()
        app.clipboard().clear()
        for dialog in panel.status.dialogs:
            dialog.close()
        for window in panel.desktops:
            window.close()
        panel.close()
        app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        print('SHORTCUTS OK: arraste, posicao salva, tamanhos 24-96px, mostrar/ocultar, remover e cache', flush=True)


if __name__ == '__main__':
    main()
