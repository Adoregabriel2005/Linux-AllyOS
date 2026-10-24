"""Execute em um display Xephyr da resolução desejada; valida os limites da UI."""
import sys
import os
import tempfile
temporary_config = tempfile.TemporaryDirectory()
os.environ['XDG_CONFIG_HOME'] = temporary_config.name
from PySide6.QtCore import QTimer, QSettings
from PySide6.QtWidgets import QApplication
from main import Panel
from applications import installed_apps


app = QApplication(sys.argv)
sys.argv.append('--session')
panel = Panel()
panel.show()
for entry in installed_apps()[:6]:
    panel.add_shortcut(entry)
failures = []


def check():
    screen = panel.screen().availableGeometry()
    panel.open_apps()
    app.processEvents()
    for label, dialog in [('apps', panel.library)]:
        if dialog.width() > screen.width() or dialog.height() > screen.height():
            failures.append((label, dialog.width(), dialog.height()))
        dialog.hide()
    for opener in (panel.status.open_volume, panel.status.open_audio_devices,
                   panel.status.open_network, panel.status.open_devices):
        opener()
        app.processEvents()
        dialog = panel.status.dialogs[-1]
        if dialog.width() > screen.width() or dialog.height() > screen.height():
            failures.append((dialog.windowTitle(), dialog.width(), dialog.height()))
        dialog.hide()
    panel.open_wallpapers()
    app.processEvents()
    if panel.wallpaper_library.width() > screen.width() or panel.wallpaper_library.height() > screen.height():
        failures.append(('wallpapers', panel.wallpaper_library.width(), panel.wallpaper_library.height()))
    panel.wallpaper_library.hide()
    panel.open_preferences()
    app.processEvents()
    if panel.preferences.width() > screen.width() or panel.preferences.height() > screen.height():
        failures.append(('settings', panel.preferences.width(), panel.preferences.height()))
    panel.preferences.hide()
    from about import open_about
    from diagnostics import open_diagnostics
    for label, opener, attribute in [('about', open_about, 'about_dialog'),
                                     ('diagnostics', open_diagnostics, 'diagnostics_dialog')]:
        opener(panel)
        app.processEvents()
        dialog = getattr(panel, attribute)
        if dialog.width() > screen.width() or dialog.height() > screen.height():
            failures.append((label, dialog.width(), dialog.height()))
        dialog.hide()
    # O layout do painel deve caber, incluindo os indicadores inferiores.
    if panel.layout.minimumSize().height() > screen.height():
        failures.append(('panel-min-height', panel.layout.minimumSize().height()))
    for desktop in panel.desktops:
        for shortcut in desktop.shortcut_widgets:
            if not desktop.rect().contains(shortcut.geometry()):
                failures.append(('shortcut-outside-screen', shortcut.app['name']))
        for index, shortcut in enumerate(desktop.shortcut_widgets):
            if any(shortcut.geometry().intersects(other.geometry())
                   for other in desktop.shortcut_widgets[index + 1:]):
                failures.append(('shortcut-overlap', shortcut.app['name']))
    print(f'RESOLUTION {screen.width()}x{screen.height()} DPR={panel.devicePixelRatioF()} FAILURES={failures}', flush=True)
    QTimer.singleShot(2000, finish)


def finish():
    panel.status.shutdown()
    for desktop in panel.desktops:
        desktop.close()
    panel.close()
    app.exit(1 if failures else 0)


QTimer.singleShot(500, check)
sys.exit(app.exec())
