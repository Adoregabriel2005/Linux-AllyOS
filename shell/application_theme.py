"""Paleta padrão dos aplicativos nativos, sem compositor ou processos extras."""
import os
from pathlib import Path
import shutil
from PySide6.QtCore import QSettings


def configure_external_theme(light=False):
    root = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    try:
        for toolkit in ('qt6ct', 'gtk-3.0'):
            (root / toolkit).mkdir(parents=True, exist_ok=True)
        qt = QSettings(str(root / 'qt6ct/qt6ct.conf'), QSettings.Format.IniFormat)
        qt.setValue('Appearance/style', 'Fusion')
        qt.setValue('Appearance/icon_theme', 'Adwaita')
        qt.setValue('Appearance/custom_palette', not light)
        qt.setValue('Appearance/color_scheme_path', '/usr/share/qt6ct/colors/darker.conf')
        qt.sync()
        gtk = QSettings(str(root / 'gtk-3.0/settings.ini'), QSettings.Format.IniFormat)
        gtk.setValue('Settings/gtk-theme-name', 'Adwaita' if light else 'Adwaita-dark')
        gtk.setValue('Settings/gtk-application-prefer-dark-theme', not light)
        gtk.sync()
        os.environ['GTK_THEME'] = 'Adwaita' if light else 'Adwaita:dark'
        if shutil.which('qt6ct'):
            os.environ['QT_QPA_PLATFORMTHEME'] = 'qt6ct'
        return qt.status() == QSettings.Status.NoError and gtk.status() == QSettings.Status.NoError
    except OSError:
        return False
