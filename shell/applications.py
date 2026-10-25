"""Catálogo XDG e lançador de aplicativos da RoseShell."""
from i18n import tr
import configparser
import locale
import os
from pathlib import Path
import shutil
import shlex

from PySide6.QtCore import QSize, Qt, QProcess, QProcessEnvironment
from PySide6.QtGui import QIcon, QFontMetrics
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QListView, QPushButton, QMessageBox)


def desktop_icon(name):
    if Path(name).is_file():
        return QIcon(name)
    icon = QIcon.fromTheme(name)
    if icon.isNull() and name and '/' not in name:
        # Alguns pacotes, incluindo TuxManager, usam o diretório legado.
        for directory in ('/usr/share/pixmaps', '/usr/local/share/pixmaps'):
            for suffix in ('.svg', '.png', '.xpm'):
                source = Path(directory) / (name + suffix)
                if source.is_file():
                    return QIcon(str(source))
    return icon


def entry_is_available(identity, entry):
    from hardware_capabilities import live_session, nvtop_status
    if entry.get('TryExec') and not shutil.which(entry['TryExec']):
        return False
    internal = {'qt6ct.desktop', 'qt5ct.desktop', 'obconf.desktop', 'obconf-qt.desktop',
                'kdesystemsettings.desktop', 'systemsettings.desktop', 'org.kde.systemsettings.desktop'}
    if identity in internal:
        return False
    try:
        executable = shlex.split(entry['Exec'])[0]
    except (ValueError, IndexError):
        return False
    if not shutil.which(executable):
        return False
    installer = {'allyos-install.desktop', 'calamares-install-debian.desktop',
                 'calamares.desktop', 'debian-installer-launcher.desktop', 'debian-installer.desktop'}
    if identity in installer or Path(executable).name.startswith(('calamares', 'debian-installer')):
        return identity == 'allyos-install.desktop' and live_session() and bool(shutil.which('calamares'))
    if identity == 'nvtop.desktop' or Path(executable).name == 'nvtop':
        return nvtop_status()[0]
    if identity == 'xfce4-taskmanager.desktop' and shutil.which('tux-manager'):
        return False
    return True


def installed_apps():
    from i18n import language
    lang = 'en' if language() == 'en' else 'pt_BR'
    roots = [Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))]
    roots += [Path(p) for p in os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if p]
    seen, result = set(), []
    for root in roots:
        folder = root / 'applications'
        for path in sorted(folder.rglob('*.desktop')):
            identity = str(path.relative_to(folder)).replace(os.sep, '-')
            if identity in seen:
                continue
            seen.add(identity)
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                parser.read(path, encoding='utf-8')
                entry = parser['Desktop Entry']
                if entry.get('Type') != 'Application' or not entry.get('Exec'):
                    continue
                if any(entry.get(key, '').lower() == 'true' for key in ('Hidden', 'NoDisplay')):
                    continue
                only = entry.get('OnlyShowIn', '').split(';')
                excluded = entry.get('NotShowIn', '').split(';')
                if (only != [''] and 'RoseShell' not in only) or 'RoseShell' in excluded:
                    continue
                if entry.get('TryExec') and not shutil.which(entry['TryExec']):
                    continue
                if not entry_is_available(identity, entry):
                    continue
                name = entry.get(f'Name[{lang}]', entry.get(f'Name[{lang.split("_")[0]}]', entry.get('Name', path.stem)))
                result.append({'name': name, 'path': str(path), 'icon': entry.get('Icon', ''),
                               'wmclass': entry.get('StartupWMClass', ''),
                               'search': name + ' ' + entry.get('GenericName', '') + ' ' + entry.get('Keywords', '')})
            except (configparser.Error, OSError, KeyError, UnicodeError):
                continue
    return sorted(result, key=lambda app: app['name'].casefold())


class ApplicationLibrary(QDialog):
    def __init__(self, panel):
        super().__init__(panel)
        self.panel = panel
        self.processes = []
        self.setWindowTitle(tr('RoseShell — Aplicativos'))
        self.setMinimumSize(260, 220)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        header = QHBoxLayout()
        title = QLabel(tr('APLICATIVOS'))
        title.setStyleSheet('font-size: 22px; font-weight: bold; border-bottom: 3px solid #c58f9d; padding-bottom: 8px;')
        header.addWidget(title, 1)
        close = QPushButton(tr('Fechar'))
        close.clicked.connect(self.hide)
        header.addWidget(close)
        layout.addLayout(header)
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr('Buscar nos aplicativos instalados…'))
        self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName(tr('Buscar aplicativos'))
        layout.addWidget(self.search)
        self.list = QListWidget()
        self.list.setViewMode(QListView.ViewMode.IconMode)
        self.list.setResizeMode(QListView.ResizeMode.Adjust)
        self.list.setMovement(QListView.Movement.Static)
        self.list.setGridSize(QSize(148, 110))
        self.list.setIconSize(QSize(48, 48))
        self.list.setWordWrap(True)
        self.list.setSpacing(6)
        layout.addWidget(self.list, 1)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.search.textChanged.connect(self.filter)
        self.search.returnPressed.connect(self.activate_first)
        self.list.itemActivated.connect(self.launch)
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.context_menu)
        shortcut = QPushButton(tr('Adicionar selecionado à área de trabalho'))
        shortcut.clicked.connect(self.add_selected_shortcut)
        layout.addWidget(shortcut)

    def add_selected_shortcut(self):
        item = self.list.currentItem()
        if item is not None:
            self.panel.add_shortcut(item.data(Qt.ItemDataRole.UserRole))
            self.status.setText(tr('Atalho adicionado. Arraste na área de trabalho para posicionar.'))

    def context_menu(self, position):
        from PySide6.QtWidgets import QMenu
        item = self.list.itemAt(position)
        if item is None:
            return
        menu = QMenu(self)
        menu.addAction(tr('Abrir'), lambda: self.launch(item))
        menu.addAction(tr('Adicionar à área de trabalho'), lambda:
                       self.panel.add_shortcut(item.data(Qt.ItemDataRole.UserRole)))
        menu.exec(self.list.mapToGlobal(position))

    def open_library(self):
        self.apps = installed_apps()
        self.list.clear()
        metrics = QFontMetrics(self.list.font())
        label_height = max((metrics.boundingRect(0, 0, 132, 2000,
                           int(Qt.TextFlag.TextWordWrap), app['name']).height()
                           for app in self.apps), default=metrics.height())
        self.list.setGridSize(QSize(148, 48 + label_height + 28))
        from icons import illustrated_icon
        for app in self.apps:
            name = app['name'].lower()
            if any(key in name for key in ('pcman', 'thunar', 'files', 'arquivos')):
                art = illustrated_icon('files')
            elif any(key in name for key in ('featherpad', 'mousepad', 'texto')):
                art = illustrated_icon('editor')
            elif 'wine' in name:
                art = illustrated_icon('wine')
            else:
                art = desktop_icon(app['icon'])
                if art.isNull():
                    art = illustrated_icon('apps')
            item = QListWidgetItem(art, app['name'])
            item.setData(Qt.ItemDataRole.UserRole, app)
            item.setToolTip(app['name'])
            self.list.addItem(item)
        self.search.clear()
        self.filter('')
        screen = self.panel.screen().availableGeometry()
        self.resize(min(850, screen.width() - 80), min(640, screen.height() - 70))
        self.move(screen.center() - self.rect().center())
        self.show()
        self.raise_()
        self.activateWindow()
        self.search.setFocus()

    def filter(self, text):
        visible = 0
        for index in range(self.list.count()):
            item = self.list.item(index)
            match = text.casefold() in item.data(Qt.ItemDataRole.UserRole)['search'].casefold()
            item.setHidden(not match)
            visible += int(match)
        self.status.setText(tr(f'{visible} aplicativos • duplo clique ou Enter para abrir • Esc para fechar'))

    def activate_first(self):
        for index in range(self.list.count()):
            item = self.list.item(index)
            if not item.isHidden():
                self.launch(item)
                return

    def launch(self, item):
        self.launch_entry(item.data(Qt.ItemDataRole.UserRole))

    def launch_entry(self, app):
        # Re-check stale desktop shortcuts after uninstalling an app or leaving Live.
        parser = configparser.ConfigParser(interpolation=None, strict=False)
        try:
            parser.read(app['path'], encoding='utf-8')
            entry = parser['Desktop Entry']
            if not entry_is_available(Path(app['path']).name, entry):
                raise ValueError('Unavailable application')
        except (OSError, KeyError, ValueError, UnicodeError, configparser.Error):
            QMessageBox.information(self.panel, tr('Aplicativo indisponível'),
                                    tr('Este aplicativo não está disponível nesta sessão. Atualize ou remova o atalho.'))
            return
        gio = shutil.which('gio')
        if not gio:
            QMessageBox.information(self, 'RoseShell', tr('Instale libglib2.0-bin para abrir aplicativos.'))
            return
        process = QProcess(self)
        self.processes.append(process)
        process.finished.connect(lambda code, status, p=process: self.launch_finished(p, code))
        process.errorOccurred.connect(lambda error, p=process: self.launch_finished(p, -1)
            if error == QProcess.ProcessError.FailedToStart else None)
        if ('supertux' in Path(app['path']).name.lower() and
                self.panel.settings.value('performance', 'economy') == 'economy' and
                Path('/usr/games/supertux2').is_file()):
            environment = QProcessEnvironment.systemEnvironment()
            if not environment.contains('ALSOFT_DRIVERS') and not shutil.which('wpctl') and shutil.which('pactl'):
                environment.insert('ALSOFT_DRIVERS', 'pulse,alsa')
            process.setProcessEnvironment(environment)
            process.start('/usr/games/supertux2', ['--renderer', 'sdl'])
        else:
            process.start(gio, ['launch', app['path']])
        self.hide()

    def launch_finished(self, process, code):
        if process not in self.processes:
            return
        if code:
            QMessageBox.warning(self.panel, tr('RoseShell — falha ao abrir'),
                                bytes(process.readAllStandardError()).decode(errors='replace')[:600]
                                or tr('Não foi possível iniciar este aplicativo.'))
        if process in self.processes:
            self.processes.remove(process)
        process.deleteLater()
