"""RoseShell: painel e área de trabalho próprios sobre X11."""
from i18n import tr
import shutil
import sys
import os
import json
from pathlib import Path

from PySide6.QtCore import QDateTime, QProcess, QSettings, QSize, Qt, QTimer, QStandardPaths
from PySide6.QtGui import QImageReader
from PySide6.QtWidgets import (
    QApplication, QLabel, QMenu, QMessageBox, QPushButton, QVBoxLayout, QWidget,
    QFileDialog,
)
from desktop import Desktop, property32
from applications import ApplicationLibrary
from wallpapers import WallpaperLibrary, bundled_wallpapers
from icons import illustrated_icon
from system_ui import StatusArea
from preferences import Preferences
from clipboard import ClipboardKeeper
from shortcuts import read_shortcuts
from tasks import TaskList




class Panel(QWidget):
    def __init__(self):
        super().__init__()
        QApplication.instance().setQuitOnLastWindowClosed(False)
        self.settings = QSettings('RoseShell', 'Desktop')
        self.session_mode = '--session' in sys.argv
        self.desktops = []
        self.library = None
        self.wallpaper_library = None
        self.preferences = None
        self.copy_processes = []
        self.clipboard_keeper = ClipboardKeeper(self) if self.session_mode else None
        collection = bundled_wallpapers()
        if collection and not self.settings.value('wallpaper', ''):
            self.settings.setValue('wallpaper', str(collection[0]))
        self.side = self.settings.value('side', 'left')
        self.light = self.settings.value('theme', 'dark') == 'light'
        self.screen_index = int(self.settings.value('screen', 0))
        self.watched_screens = []
        self.setWindowTitle('RoseShell')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint |
                            Qt.WindowType.Tool)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 12, 6, 12)
        self.layout.setSpacing(10)
        self.buttons = []
        self.add_button('apps', tr('Aplicativos instalados'), self.open_apps)
        self.add_button('files', tr('Arquivos'), lambda: self.launch([
            ['thunar'], ['pcmanfm-qt'], ['xdg-open', str(Path.home())]]))
        self.add_button('editor', tr('Editor de texto'), lambda: self.launch([
            ['featherpad'], ['mousepad'], ['kate']]))
        self.add_button('terminal', 'Terminal', lambda: self.launch([
            ['qterminal'], ['xfce4-terminal'], ['x-terminal-emulator']]))
        self.add_button('web', tr('Navegador'), lambda: self.launch([
            ['x-www-browser'], ['firefox-esr'], ['firefox']]))
        self.tasks = TaskList(self)
        self.layout.addWidget(self.tasks, 1)
        self.status = StatusArea(self)
        self.layout.addWidget(self.status)
        self.add_button('settings', tr('Preferências da RoseShell'), self.open_preferences)
        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.clock)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.next_wallpaper)
        self.configure_rotation()
        self.tick()
        self.apply_theme()
        app = QApplication.instance()
        app.aboutToQuit.connect(self.status.shutdown)
        app.aboutToQuit.connect(self.tasks.shutdown)
        if self.clipboard_keeper is not None:
            app.aboutToQuit.connect(self.clipboard_keeper.release)
        app.screenAdded.connect(lambda _: self.watch_screens())
        app.screenRemoved.connect(lambda _: self.reposition())
        self.watch_screens()
        if self.session_mode:
            self.refresh_desktops()
            app.screenAdded.connect(lambda _: self.refresh_desktops())
            app.screenRemoved.connect(lambda _: self.refresh_desktops())

    def refresh_desktops(self):
        for desktop in self.desktops:
            desktop.close()
            desktop.deleteLater()
        self.desktops = [Desktop(screen, self.settings, self) for screen in QApplication.screens()]
        for desktop in self.desktops:
            desktop.show()

    def showEvent(self, event):
        super().showEvent(event)
        property32(self.winId(), '_NET_WM_WINDOW_TYPE', ['_NET_WM_WINDOW_TYPE_DOCK'], 'ATOM')
        property32(self.winId(), '_NET_WM_DESKTOP', [0xffffffff])
        self.reposition()

    def add_button(self, kind, label, callback):
        button = QPushButton()
        button.setFixedSize(44, 44)
        button.setIconSize(QSize(40, 40))
        button.setToolTip(label)
        button.setAccessibleName(label)
        button.clicked.connect(callback)
        self.layout.addWidget(button)
        self.buttons.append((button, kind))

    def tick(self):
        now = QDateTime.currentDateTime()
        self.clock.setText(now.toString('HH:mm\ndd/MM'))
        self.clock.setToolTip(now.toString('dd/MM/yyyy HH:mm'))

    def apply_theme(self):
        bg, fg, border, hover = (
            ('#e9e7e2', '#242629', '#a8aaa6', '#d0d7d3') if self.light else
            ('#191c1e', '#e3e4df', '#42494c', '#343e40'))
        self.setStyleSheet(f'''
            QWidget {{ background: {bg}; color: {fg}; font-family: sans-serif;
                       font-size: 13px; }}
            QPushButton {{ border: 1px solid {border}; border-radius: 0px; }}
            QPushButton:hover, QPushButton:focus {{ background: {hover};
                                                  border-color: #83b3a1; }}
            QMenu {{ border: 1px solid {border}; padding: 5px; }}
            QMenu::item {{ padding: 8px 14px; }}
            QMenu::item:selected {{ background: {hover}; }}
            QLineEdit {{ border: 1px solid {border}; border-bottom: 2px solid #bd8b9a;
                         padding: 10px; background: {hover}; }}
            QListWidget {{ border: 1px solid {border}; padding: 8px; }}
            QListWidget::item {{ border: 1px solid transparent; padding: 7px; }}
            QListWidget::item:hover, QListWidget::item:selected {{ background: {hover};
                         border: 1px solid #bd8b9a; color: {fg}; }}
            QComboBox {{ padding: 7px; border: 1px solid {border}; }}
        ''')
        for button, kind in self.buttons:
            button.setIcon(illustrated_icon(kind))

    def watch_screens(self):
        for screen in QApplication.screens():
            if screen not in self.watched_screens:
                screen.availableGeometryChanged.connect(self.reposition)
                self.watched_screens.append(screen)
        self.reposition()

    def reposition(self, *_):
        screens = QApplication.screens()
        self.screen_index = min(max(self.screen_index, 0), len(screens) - 1)
        rect = screens[self.screen_index].geometry()
        compact = rect.height() < 600
        size = 32 if compact else 44
        self.layout.setContentsMargins(4, 5 if compact else 12, 4, 5 if compact else 12)
        self.layout.setSpacing(3 if compact else 10)
        for button, _ in self.buttons:
            button.setFixedSize(size, size)
            button.setIconSize(QSize(size - 4, size - 4))
        width = 56
        x = rect.left() if self.side == 'left' else rect.right() - width + 1
        self.setGeometry(x, rect.top(), width, rect.height())
        if self.isVisible():
            # EWMH struts usam coordenadas da janela raiz. Reservar somente na
            # borda externa; bordas internas não são expressáveis por struts.
            left = min(s.geometry().left() for s in screens)
            right = max(s.geometry().right() for s in screens)
            top = min(s.geometry().top() for s in screens)
            factor = self.devicePixelRatioF()
            l = round(width * factor) if self.side == 'left' and rect.left() == left else 0
            r = round(width * factor) if self.side == 'right' and rect.right() == right else 0
            start, end = round((rect.top() - top) * factor), round((rect.bottom() - top + 1) * factor) - 1
            values = [l, r, 0, 0, start if l else 0, end if l else 0,
                      start if r else 0, end if r else 0, 0, 0, 0, 0]
            property32(self.winId(), '_NET_WM_STRUT_PARTIAL', values)
            property32(self.winId(), '_NET_WM_STRUT', values[:4])

    def launch(self, candidates):
        for command in candidates:
            executable = shutil.which(command[0])
            if executable:
                started, _pid = QProcess.startDetached(executable, command[1:])
                if started:
                    return
        QMessageBox.information(self, tr('Aplicativo indisponível'),
                                tr('Não foi possível abrir o aplicativo.\n'
                                'Verifique se há um programa compatível instalado.'))

    def open_menu(self):
        menu = QMenu(self)
        menu.addAction(tr('RoseShell · desenvolvimento')).setEnabled(False)
        menu.addSeparator()
        menu.addAction(tr('Aplicativos instalados'), self.open_apps)
        menu.addAction(tr('Configurações da interface…'), self.open_preferences)
        menu.addAction(tr('Gerenciador de dispositivos…'), self.status.open_devices)
        from diagnostics import open_diagnostics
        from about import open_about
        menu.addAction(tr('Diagnóstico de hardware…'), lambda: open_diagnostics(self))
        menu.addAction(tr('Sobre a RoseShell'), lambda: open_about(self))
        menu.addAction(tr('Mover para ') + (tr('direita') if self.side == 'left' else tr('esquerda')),
                       self.switch_side)
        menu.addAction(tr('Usar tema ') + (tr('escuro') if self.light else tr('claro')), self.switch_theme)
        menu.addAction(tr('Coleção de papéis de parede…'), self.open_wallpapers)
        wallpaper = menu.addMenu(tr('Ajuste do papel de parede'))
        for key, label in [('fit', tr('Inteiro, sem cortar')), ('center', tr('Centralizado')), ('fill', tr('Preencher')), ('stretch', tr('Esticar'))]:
            action = wallpaper.addAction(label)
            action.setCheckable(True)
            action.setChecked(self.settings.value('wallpaper_mode', 'fit') == key)
            action.triggered.connect(lambda checked=False, mode=key: self.set_wallpaper_mode(mode))
        monitors = menu.addMenu('Monitor')
        for index, screen in enumerate(QApplication.screens()):
            action = monitors.addAction(f'{index + 1} — {screen.name()}')
            action.setCheckable(True)
            action.setChecked(index == self.screen_index)
            action.triggered.connect(lambda checked=False, i=index: self.select_screen(i))
        menu.addSeparator()
        menu.addAction(tr('Sair da sessão') if self.session_mode else tr('Encerrar painel'), self.exit_shell)
        menu.exec(self.buttons[0][0].mapToGlobal(self.buttons[0][0].rect().bottomRight()))

    def open_apps(self):
        if self.library is None:
            self.library = ApplicationLibrary(self)
        self.library.open_library()

    def open_preferences(self):
        if self.preferences is not None:
            self.preferences.close()
            self.preferences.deleteLater()
        self.preferences = Preferences(self)
        self.preferences.show()

    def capture(self):
        QProcess.startDetached(sys.executable, [str(Path(__file__).parent / 'capture.py')])

    def desktop_folder(self):
        return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation) or str(Path.home() / 'Desktop'))

    def desktop_menu(self, position):
        menu = QMenu(self)
        clipboard = QApplication.clipboard()
        menu.addAction(tr('Copiar caminho da área de trabalho'), lambda: clipboard.setText(str(self.desktop_folder())))
        paste = menu.addAction(tr('Colar arquivos ou imagem'), self.paste_desktop)
        mime = clipboard.mimeData()
        paste.setEnabled(mime.hasUrls() or mime.hasImage())
        menu.addSeparator()
        icons = menu.addMenu(tr('Ícones da área de trabalho'))
        show = icons.addAction(tr('Mostrar ícones'))
        show.setCheckable(True)
        show.setChecked(self.settings.value('show_desktop_icons', 'true') == 'true')
        show.triggered.connect(self.show_desktop_icons)
        for size in (24, 32, 48, 64, 96):
            action = icons.addAction(tr(f'Tamanho {size} px'))
            action.setCheckable(True)
            action.setChecked(int(self.settings.value('desktop_icon_size', 48)) == size)
            action.triggered.connect(lambda checked=False, value=size: self.set_desktop_icon_size(value))
        icons.addAction(tr('Organizar ícones'), self.arrange_shortcuts)
        personalize = menu.addMenu(tr('Personalizar'))
        personalize.addAction(tr('Papéis de parede…'), self.open_wallpapers)
        scale = personalize.addMenu(tr('Escala da RoseShell'))
        for value, label in [('1', '100%'), ('1.25', '125%')]:
            action = scale.addAction(label + tr(' · próxima sessão'))
            action.setCheckable(True)
            action.setChecked(self.settings.value('scale', '1') == value)
            action.triggered.connect(lambda checked=False, factor=value: self.set_scale(factor))
        menu.addAction(tr('Configurações da interface…'), self.open_preferences)
        menu.addAction(tr('Capturar tela…'), self.capture)
        menu.addAction(tr('Abrir pasta da área de trabalho'), lambda: self.launch([['xdg-open', str(self.desktop_folder())]]))
        menu.exec(position)

    def refresh_shortcuts(self):
        for desktop in self.desktops:
            desktop.rebuild_shortcuts()

    def add_shortcut(self, app):
        entries = read_shortcuts(self.settings)
        if not any(entry['path'] == app['path'] for entry in entries):
            entries.append({key: app[key] for key in ('path', 'name', 'icon')})
            entries[-1]['monitor'] = self.screen().name()
        self.settings.setValue('desktop_shortcuts', json.dumps(entries))
        self.settings.setValue('show_desktop_icons', 'true')
        self.refresh_shortcuts()

    def remove_shortcut(self, path):
        entries = [entry for entry in read_shortcuts(self.settings) if entry['path'] != path]
        self.settings.setValue('desktop_shortcuts', json.dumps(entries))
        self.refresh_shortcuts()

    def move_shortcut(self, path, monitor):
        entries = read_shortcuts(self.settings)
        for entry in entries:
            if entry['path'] == path:
                entry['monitor'] = monitor
        self.settings.setValue('desktop_shortcuts', json.dumps(entries))
        self.refresh_shortcuts()

    def launch_shortcut(self, app):
        if self.library is None:
            self.library = ApplicationLibrary(self)
        self.library.launch_entry(app)

    def set_desktop_icon_size(self, size):
        self.settings.setValue('desktop_icon_size', max(24, min(96, int(size))))
        self.refresh_shortcuts()

    def show_desktop_icons(self, enabled):
        self.settings.setValue('show_desktop_icons', 'true' if enabled else 'false')
        self.refresh_shortcuts()

    def arrange_shortcuts(self):
        for desktop in self.desktops:
            desktop.arrange_shortcuts()

    def set_performance(self, profile):
        self.settings.setValue('performance', profile)
        self.status.timer.setInterval(10000 if profile == 'economy' else 5000)
        for desktop in self.desktops:
            desktop.update()

    def set_scale(self, value):
        if value in ('1', '1.25'):
            self.settings.setValue('scale', value)

    def paste_desktop(self):
        destination = self.desktop_folder()
        try:
            destination.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            QMessageBox.warning(self, 'RoseShell', str(error))
            return
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                if not url.isLocalFile():
                    continue
                source = Path(url.toLocalFile())
                target = destination / source.name
                if not source.is_file() or target.exists():
                    QMessageBox.information(self, 'RoseShell', tr(f'Arquivo já existente ou não é arquivo comum: {source.name}'))
                    continue
                process = QProcess(self)
                self.copy_processes.append(process)
                process.finished.connect(lambda code, status, p=process: self.copy_finished(p, code))
                process.start('cp', ['-n', '--', str(source), str(target)])
        elif mime.hasImage():
            path = destination / ('Imagem-' + QDateTime.currentDateTime().toString('yyyyMMdd-HHmmss-zzz') + '.png')
            if not clipboard.image().save(str(path)):
                QMessageBox.warning(self, 'RoseShell', tr('Falha ao salvar a imagem.'))

    def copy_finished(self, process, code):
        if code:
            QMessageBox.warning(self, 'RoseShell', bytes(process.readAllStandardError()).decode(errors='replace'))
        if process in self.copy_processes:
            self.copy_processes.remove(process)
        process.deleteLater()

    def open_wallpapers(self):
        if self.wallpaper_library is not None:
            self.wallpaper_library.close()
            self.wallpaper_library.deleteLater()
        self.wallpaper_library = WallpaperLibrary(self)
        from preferences import fit_dialog
        fit_dialog(self.wallpaper_library, self)
        self.wallpaper_library.show()

    def configure_rotation(self):
        self.rotation_timer.stop()
        if self.settings.value('wallpaper_rotate', 'false') == 'true':
            minutes = max(1, int(self.settings.value('wallpaper_minutes', 15)))
            self.rotation_timer.start(minutes * 60000)

    def next_wallpaper(self):
        collection = bundled_wallpapers()
        if not collection:
            return
        current = self.settings.value('wallpaper', '')
        paths = [str(path) for path in collection]
        index = (paths.index(current) + 1) % len(paths) if current in paths else 0
        self.set_wallpaper(paths[index])

    def set_wallpaper(self, path):
        self.settings.setValue('wallpaper', path)
        for desktop in self.desktops:
            desktop.update()

    def switch_side(self):
        self.side = 'right' if self.side == 'left' else 'left'
        self.settings.setValue('side', self.side)
        self.reposition()
        self.refresh_shortcuts()

    def switch_theme(self):
        self.light = not self.light
        self.settings.setValue('theme', 'light' if self.light else 'dark')
        if self.session_mode and not os.environ.get('ROSESHELL_NESTED'):
            from application_theme import configure_external_theme
            configure_external_theme(self.light)
        self.apply_theme()
        for desktop in self.desktops:
            desktop.update()

    def choose_wallpaper(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('RoseShell — papel de parede'), str(Path.home()),
                                             tr('Imagens (*.png *.jpg *.jpeg *.webp *.bmp)'))
        if path:
            if not QImageReader(path).canRead():
                QMessageBox.warning(self, 'RoseShell', tr('Não foi possível ler essa imagem. Verifique o formato e o arquivo.'))
                return
            self.settings.setValue('wallpaper_rotate', 'false')
            self.configure_rotation()
            self.set_wallpaper(path)

    def set_wallpaper_mode(self, mode):
        self.settings.setValue('wallpaper_mode', mode)
        for desktop in self.desktops:
            desktop.update()

    def exit_shell(self):
        if self.session_mode:
            answer = QMessageBox.question(self, 'RoseShell', tr('Encerrar a sessão? Salve seus arquivos antes de sair.'))
            if answer != QMessageBox.StandardButton.Yes:
                return
        QApplication.quit()

    def select_screen(self, index):
        self.screen_index = index
        self.settings.setValue('screen', index)
        self.reposition()
        self.refresh_shortcuts()


if __name__ == '__main__':
    os.environ.setdefault('QT_SCALE_FACTOR', str(QSettings('RoseShell', 'Desktop').value('scale', '1')))
    app = QApplication(sys.argv)
    app.setApplicationName('RoseShell')
    panel = Panel()
    panel.show()
    if '--apps' in sys.argv:
        QTimer.singleShot(100, panel.open_apps)
    if '--wallpapers' in sys.argv:
        QTimer.singleShot(100, panel.open_wallpapers)
    if '--preferences' in sys.argv:
        QTimer.singleShot(100, panel.open_preferences)
    if '--about' in sys.argv:
        from about import open_about
        QTimer.singleShot(100, lambda: open_about(panel))
    if '--diagnostics' in sys.argv:
        from diagnostics import open_diagnostics
        QTimer.singleShot(100, lambda: open_diagnostics(panel))
    sys.exit(app.exec())
