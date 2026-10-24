"""Preferências funcionais da interface RoseShell."""
from i18n import tr
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QFormLayout,
    QComboBox, QPushButton, QScrollArea, QWidget, QMessageBox, QTabWidget)
from PySide6.QtWidgets import QCheckBox


def fit_dialog(dialog, panel, width=720, height=540):
    rect = panel.screen().availableGeometry()
    dialog.setMinimumSize(260, 220)
    dialog.resize(min(width, rect.width() - 70), min(height, rect.height() - 45))
    dialog.move(rect.center() - dialog.rect().center())


class Preferences(QDialog):
    def __init__(self, panel):
        super().__init__(panel)
        self.panel = panel
        self.setWindowTitle(tr('RoseShell — Configurações'))
        fit_dialog(self, panel)
        layout = QVBoxLayout(self)
        title = QLabel(tr('PERSONALIZAR ROSESHELL'))
        title.setStyleSheet('font-size: 19px; font-weight: bold; padding: 8px; border-bottom: 2px solid #bd8b9a;')
        layout.addWidget(title)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        form = QFormLayout(body)
        theme = QComboBox()
        theme.addItems([tr('Grafite'), tr('Claro')])
        theme.setCurrentIndex(1 if panel.light else 0)
        theme.currentIndexChanged.connect(lambda index: panel.switch_theme() if (index == 1) != panel.light else None)
        form.addRow(tr('Tema'), theme)
        side = QComboBox()
        side.addItems([tr('Esquerda'), tr('Direita')])
        side.setCurrentIndex(1 if panel.side == 'right' else 0)
        side.currentIndexChanged.connect(lambda index: panel.switch_side() if (index == 1) != (panel.side == 'right') else None)
        form.addRow(tr('Painel'), side)
        monitors = QComboBox()
        from PySide6.QtWidgets import QApplication
        for index, screen in enumerate(QApplication.screens()):
            monitors.addItem(f'{index + 1} — {screen.name()}', index)
        monitors.setCurrentIndex(panel.screen_index)
        monitors.currentIndexChanged.connect(panel.select_screen)
        form.addRow(tr('Monitor do painel'), monitors)
        scale = QComboBox()
        scale.addItems(['100%', '125%'])
        scale.setCurrentIndex(1 if panel.settings.value('scale', '1') == '1.25' else 0)
        scale.currentIndexChanged.connect(self.scale)
        form.addRow(tr('Escala da RoseShell'), scale)
        show_icons = QCheckBox(tr('Mostrar atalhos na área de trabalho'))
        show_icons.setChecked(panel.settings.value('show_desktop_icons', 'true') == 'true')
        show_icons.toggled.connect(panel.show_desktop_icons)
        form.addRow(show_icons)
        icon_size = QComboBox()
        for value in (24, 32, 48, 64, 96):
            icon_size.addItem(f'{value} px', value)
        icon_size.setCurrentIndex(max(0, icon_size.findData(int(panel.settings.value('desktop_icon_size', 48)))))
        icon_size.currentIndexChanged.connect(lambda _: panel.set_desktop_icon_size(icon_size.currentData()))
        form.addRow(tr('Tamanho dos ícones'), icon_size)
        performance = QComboBox()
        performance.addItem(tr('Econômico · GPUs antigas'), 'economy')
        performance.addItem(tr('Equilibrado'), 'balanced')
        performance.setCurrentIndex(max(0, performance.findData(panel.settings.value('performance', 'economy'))))
        performance.currentIndexChanged.connect(lambda _: panel.set_performance(performance.currentData()))
        form.addRow(tr('Perfil de desenho'), performance)
        note = QLabel(tr('A escala será aplicada ao entrar novamente na sessão.\nAplicativos externos podem ter seus próprios ajustes de escala.'))
        note.setWordWrap(True)
        form.addRow(note)
        scroll.setWidget(body)
        tabs.addTab(scroll, tr('Aparência'))
        system_scroll = QScrollArea()
        system_scroll.setWidgetResizable(True)
        system_body = QWidget()
        form = QFormLayout(system_body)
        language = QComboBox()
        language.addItem('Português (Brasil)', 'pt_BR')
        language.addItem('English', 'en')
        from i18n import language as current_language
        language.setCurrentIndex(max(0, language.findData(current_language())))
        language.currentIndexChanged.connect(lambda _: self.set_language(language.currentData()))
        form.addRow(tr('Idioma da interface'), language)
        entry_sound = QCheckBox(tr('Tocar som ao entrar na sessão'))
        entry_sound.setChecked(panel.settings.value('entry_sound', 'true') == 'true')
        entry_sound.toggled.connect(lambda enabled: panel.settings.setValue('entry_sound', 'true' if enabled else 'false'))
        form.addRow(entry_sound)
        controllers = QPushButton(tr('Testar controle de jogo…'))
        import shutil
        controllers.setEnabled(shutil.which('jstest-gtk') is not None)
        controllers.clicked.connect(lambda: panel.launch([['jstest-gtk']]))
        form.addRow(controllers)
        from diagnostics import open_diagnostics, task_manager
        diagnostics = QPushButton(tr('Diagnóstico de hardware…'))
        diagnostics.clicked.connect(lambda: open_diagnostics(panel))
        form.addRow(diagnostics)
        for title, callback in [(tr('Papéis de parede e rotação…'), panel.open_wallpapers),
                                (tr('Gerenciador de dispositivos…'), panel.status.open_devices),
                                (tr('Som…'), panel.status.open_volume), (tr('Rede…'), panel.status.open_network),
                                (tr('Idioma e teclado…'), panel.status.open_language), (tr('Captura de tela…'), panel.capture)]:
            button = QPushButton(title)
            button.setMinimumHeight(30)
            button.clicked.connect(callback)
            form.addRow(button)
        tasks = QPushButton(tr('Gerenciador de tarefas · Ctrl+Shift+Esc'))
        tasks.clicked.connect(lambda: task_manager(panel))
        form.addRow(tasks)
        system_scroll.setWidget(system_body)
        tabs.addTab(system_scroll, tr('Sistema'))
        from about import open_about
        about = QPushButton(tr('Sobre a RoseShell'))
        about.clicked.connect(lambda: open_about(panel))
        layout.addWidget(about)
        close = QPushButton(tr('Fechar'))
        close.clicked.connect(self.close)
        layout.addWidget(close)

    def scale(self, index):
        self.panel.set_scale('1.25' if index else '1')

    def set_language(self, value):
        self.panel.settings.setValue('language', value)
        QMessageBox.information(self, 'RoseShell', 'Idioma salvo. Entre novamente na sessão para aplicar.\nLanguage saved. Sign in again to apply.')
