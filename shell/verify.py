"""Verificações de integração: catálogo XDG, ícones, busca e wallpapers."""
import os
from pathlib import Path
import tempfile


def main():
    from applications import installed_apps
    actual = installed_apps()
    assert actual, 'Catálogo real vazio'
    print(f'Catalogo Debian: {len(actual)} aplicativos', flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        user, system = root / 'user/applications', root / 'system/applications'
        user.mkdir(parents=True)
        system.mkdir(parents=True)
        base = '[Desktop Entry]\nType=Application\nName=Demo\nExec=true\n'
        (system / 'demo.desktop').write_text(base)
        (user / 'demo.desktop').write_text(base + 'Hidden=true\n')
        (system / 'shown.desktop').write_text(base + 'Name[pt_BR]=Visivel\n')
        (system / 'hidden.desktop').write_text(base + 'NoDisplay=true\n')
        os.environ['XDG_DATA_HOME'] = str(root / 'user')
        os.environ['XDG_DATA_DIRS'] = str(root / 'system')
        assert len(installed_apps()) == 1, 'Precedência ou visibilidade XDG incorreta'
        os.environ['XDG_CONFIG_HOME'] = str(root / 'config')
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from main import Panel, QApplication
        from icons import illustrated_icon
        from wallpapers import bundled_wallpapers
        app = QApplication([])
        panel = Panel()
        for kind in ('files', 'editor', 'terminal', 'web', 'apps', 'settings'):
            assert not illustrated_icon(kind).isNull()
        panel.open_apps()
        assert panel.library.list.count() == 1
        panel.library.filter('NO-SUCH-APPLICATION')
        assert panel.library.list.item(0).isHidden()
        panel.library.close()
        paths = bundled_wallpapers()
        assert len(paths) == 7, f'Esperados sete wallpapers; encontrados {len(paths)}'
        panel.set_wallpaper(str(paths[0]))
        panel.next_wallpaper()
        assert panel.settings.value('wallpaper') == str(paths[1])
        panel.settings.setValue('wallpaper_rotate', 'true')
        panel.configure_rotation()
        assert panel.rotation_timer.isActive()
        panel.settings.setValue('wallpaper_rotate', 'false')
        panel.configure_rotation()
        assert not panel.rotation_timer.isActive()
        panel.open_wallpapers()
        assert panel.wallpaper_library.list.count() == 7
        panel.wallpaper_library.close()
        from PySide6.QtGui import QImage, QImageReader, QColor
        image = QImage(32, 24, QImage.Format.Format_RGB32)
        image.fill(QColor('#c58f9d'))
        for suffix in ('png', 'jpg', 'webp'):
            target = root / ('photo.' + suffix)
            assert image.save(str(target)), suffix
            assert QImageReader(str(target)).canRead(), suffix
        panel.desktop_folder = lambda: root / 'desktop'
        app.clipboard().setImage(image)
        panel.paste_desktop()
        assert len(list((root / 'desktop').glob('*.png'))) == 1
        from PySide6.QtCore import QMimeData, QUrl
        (root / 'source').mkdir()
        source = root / 'source/copied.txt'
        source.write_text('RoseShell copy test')
        copied = QMimeData()
        copied.setUrls([QUrl.fromLocalFile(str(source))])
        app.clipboard().setMimeData(copied)
        panel.paste_desktop()
        panel.open_preferences()
        assert panel.preferences.isVisible()
        panel.preferences.close()
        from PySide6.QtCore import QEventLoop, QTimer
        wait = QEventLoop()
        QTimer.singleShot(2000, wait.quit)
        wait.exec()
        assert (root / 'desktop/copied.txt').read_text() == 'RoseShell copy test'
        assert panel.status.buttons['network'].toolTip()
        assert panel.status.buttons['disk'].toolTip()
        panel.status.open_devices()
        wait = QEventLoop()
        QTimer.singleShot(1000, wait.quit)
        wait.exec()
        from PySide6.QtWidgets import QPlainTextEdit
        device_dialog = panel.status.dialogs[-1]
        assert 'DISPOSITIVOS PCI' in device_dialog.findChild(QPlainTextEdit).toPlainText()
        device_dialog.close()
        QTimer.singleShot(100, lambda: app.activePopupWidget().close() if app.activePopupWidget() else None)
        panel.desktop_menu(panel.mapToGlobal(panel.rect().center()))
        print(f'Audio backend: {panel.status.audio_backend}; volume: {panel.status.volume}; discos: {len(panel.status.disks)}', flush=True)
        app.clipboard().clear()
        panel.status.shutdown()
        panel.timer.stop()
        panel.rotation_timer.stop()
        print('Formatos PNG/JPG/WEBP, colagem de imagem, preferencias e indicadores OK', flush=True)
        panel.close()
        app.processEvents()
        from PySide6.QtCore import QCoreApplication, QEvent
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        print('OK: catalogo XDG, icones, busca, sete wallpapers, troca e modo fixo.', flush=True)


if __name__ == '__main__':
    main()
