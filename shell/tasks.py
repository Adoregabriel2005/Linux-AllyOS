"""Lista de janelas EWMH; consultas assíncronas, sem compositor ou captura de telas."""
from i18n import tr
import shutil
import os
import re
from pathlib import Path
from PySide6.QtCore import QProcess, QSize, Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QMenu, QSizePolicy
from icons import illustrated_icon


def parse_windows(output):
    windows = {}
    for line in output.splitlines():
        fields = line.split(None, 4)
        if len(fields) != 5:
            continue
        identity, desktop, wmclass, host, title = fields
        try:
            int(identity, 16)
            if int(desktop) < 0:  # docks e desktops ficam em todos os espaços
                continue
        except ValueError:
            continue
        windows[identity] = (wmclass, title)
    return windows


class TaskList(QScrollArea):
    def __init__(self, panel):
        super().__init__(panel)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumHeight(0)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        body = QWidget()
        self.rows = QVBoxLayout(body)
        self.rows.setContentsMargins(0, 0, 0, 0)
        self.rows.setSpacing(3)
        self.rows.addStretch()
        self.setWidget(body)
        self.buttons = {}
        self.icon_cache = {}
        self.commands = set()
        self.query = QProcess(self)
        self.query.finished.connect(self.received)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self.query.kill)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        if shutil.which('wmctrl') and os.environ.get('QT_QPA_PLATFORM') != 'offscreen':
            self.timer.start(1200)
            self.refresh()
        else:
            self.setToolTip(tr('Instale wmctrl para mostrar janelas abertas.'))

    def refresh(self):
        if self.query.state() == QProcess.ProcessState.NotRunning:
            self.query.start('wmctrl', ['-lx'])
            self.deadline.start(1500)

    def received(self, code, status):
        self.deadline.stop()
        if code or status != QProcess.ExitStatus.NormalExit:
            return
        windows = parse_windows(bytes(self.query.readAllStandardOutput()).decode('utf-8', 'replace'))
        for identity in list(self.buttons):
            if identity not in windows:
                self.buttons.pop(identity).deleteLater()
        for identity, (wmclass, title) in windows.items():
            if identity not in self.buttons:
                button = QPushButton()
                button.setFixedSize(40, 34)
                button.setIconSize(QSize(28, 28))
                button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                button.clicked.connect(lambda checked=False, wid=identity: self.command(['-ia', wid]))
                button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                button.customContextMenuRequested.connect(lambda pos, wid=identity: self.menu(wid, pos))
                self.rows.insertWidget(self.rows.count() - 1, button)
                self.buttons[identity] = button
            button = self.buttons[identity]
            icon = self.window_icon(wmclass)
            if 'thunar' in wmclass.lower():
                icon = illustrated_icon('files')
            elif 'wine' in wmclass.lower() or '.exe' in wmclass.lower():
                icon = illustrated_icon('wine')
            elif 'featherpad' in wmclass.lower():
                icon = illustrated_icon('editor')
            elif 'qterminal' in wmclass.lower():
                icon = illustrated_icon('terminal')
            button.setIcon(illustrated_icon('apps') if icon.isNull() else icon)
            button.setToolTip(title)
            button.setAccessibleName(title)

    def window_icon(self, wmclass):
        if wmclass in self.icon_cache:
            return self.icon_cache[wmclass]
        icon = QIcon.fromTheme(wmclass.rsplit('.', 1)[-1].lower())
        if icon.isNull():
            # Muitos programas usam uma WM_CLASS diferente do nome do arquivo
            # do ícone. Resolver pelos metadados XDG, sem adivinhar esse nome.
            from applications import installed_apps, desktop_icon
            normalize = lambda text: re.sub(r'[^a-z0-9]', '', text.casefold())
            targets = {normalize(part) for part in wmclass.split('.') if part}
            for entry in installed_apps():
                aliases = {normalize(entry['name']), normalize(entry.get('wmclass', '')),
                           normalize(Path(entry['path']).stem.rsplit('.', 1)[-1])}
                if targets.intersection(aliases - {''}):
                    candidate = desktop_icon(entry['icon'])
                    if not candidate.isNull():
                        icon = candidate
                        break
        self.icon_cache[wmclass] = icon
        return icon

    def command(self, args):
        process = QProcess(self)
        self.commands.add(process)
        def done(*_):
            self.commands.discard(process)
            process.deleteLater()
        process.finished.connect(done)
        process.errorOccurred.connect(lambda error: done() if error == QProcess.ProcessError.FailedToStart else None)
        process.start('wmctrl', args)

    def menu(self, identity, position):
        button = self.buttons.get(identity)
        if button is None:
            return
        menu = QMenu(self)
        menu.addAction(tr('Restaurar / ativar'), lambda: self.command(['-ia', identity]))
        menu.addAction(tr('Maximizar / restaurar'), lambda: self.command(['-ir', identity, '-b', 'toggle,maximized_vert,maximized_horz']))
        menu.addAction(tr('Fechar'), lambda: self.command(['-ic', identity]))
        menu.exec(button.mapToGlobal(position))

    def shutdown(self):
        self.timer.stop()
        self.deadline.stop()
        for process in [self.query, *self.commands]:
            process.kill()
            process.waitForFinished(300)
