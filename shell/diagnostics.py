"""Ferramentas de diagnóstico; nenhuma sondagem invasiva ou teste de estresse automático."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QPlainTextEdit
from preferences import fit_dialog
from i18n import tr
from pathlib import Path
import shlex


def task_manager(panel):
    panel.launch([['tux-manager'], ['xfce4-taskmanager']])


def terminal_tool(panel, command):
    args = ['sh', str(Path(__file__).with_name('diagnostic-terminal.sh')), *command]
    panel.launch([['qterminal', '-e', shlex.join(args)], ['x-terminal-emulator', '-e', *args]])


def open_diagnostics(panel):
    previous = getattr(panel, 'diagnostics_dialog', None)
    if previous is not None:
        previous.close()
        previous.deleteLater()
    dialog = QDialog(panel)
    dialog.setWindowTitle(tr('Diagnóstico de hardware'))
    fit_dialog(dialog, panel)
    layout = QVBoxLayout(dialog)
    note = QLabel(tr('CPU, GPU, memória, temperaturas e armazenamento. Sensores disponíveis dependem do hardware e do driver; máquinas virtuais podem não expor temperaturas ou SMART.'))
    note.setWordWrap(True)
    layout.addWidget(note)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    body = QWidget()
    rows = QVBoxLayout(body)
    choices = [
        ('Resumo do sistema · Fastfetch', lambda: terminal_tool(panel, ['fastfetch'])),
        ('Informações de CPU, GPU e RAM · Hardinfo2', lambda: panel.launch([['hardinfo2']])),
        ('Gerenciador de tarefas · TuxManager', lambda: task_manager(panel)),
        ('Uso da GPU · NVTOP', lambda: terminal_tool(panel, ['nvtop'])),
        ('Saúde dos discos · GSmartControl', lambda: panel.launch([['gsmartcontrol-root'], ['gsmartcontrol']])),
        ('Relatório de hardware · inxi', lambda: terminal_tool(panel, ['inxi', '-F', '-z'])),
        ('Gerenciador de dispositivos', panel.status.open_devices),
    ]
    for title, callback in choices:
        button = QPushButton(tr(title))
        button.setMinimumHeight(32)
        button.clicked.connect(callback)
        rows.addWidget(button)
    rows.addWidget(QLabel(tr('Temperaturas detectadas')))
    temperatures = QPlainTextEdit()
    temperatures.setReadOnly(True)
    temperatures.setMinimumHeight(100)
    rows.addWidget(temperatures)
    def refresh():
        panel.status.run(['sensors'], lambda ok, out: temperatures.setPlainText(
            out.strip() if ok and out.strip() else tr('Nenhum sensor disponível nesta máquina ou VM.')))
    refresh_button = QPushButton(tr('Atualizar temperaturas'))
    refresh_button.clicked.connect(refresh)
    rows.addWidget(refresh_button)
    scroll.setWidget(body)
    layout.addWidget(scroll)
    close = QPushButton(tr('Fechar'))
    close.clicked.connect(dialog.close)
    layout.addWidget(close)
    panel.diagnostics_dialog = dialog
    dialog.show()
    refresh()
