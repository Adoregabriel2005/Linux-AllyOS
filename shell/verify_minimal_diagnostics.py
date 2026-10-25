"""Optional diagnostics must not expose clickable dead actions in the minimal profile."""
import os
import shutil
import tempfile
from unittest.mock import patch

temporary = tempfile.TemporaryDirectory()
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['XDG_CONFIG_HOME'] = temporary.name
from PySide6.QtWidgets import QApplication, QPushButton
from main import Panel
from diagnostics import open_diagnostics
from i18n import tr

app = QApplication([])
panel = Panel()
panel.status.shutdown()
panel.tasks.shutdown()
original = shutil.which
absent = {'fastfetch', 'hardinfo2', 'tux-manager', 'nvtop', 'gsmartcontrol', 'inxi'}
with patch('diagnostics.shutil.which', side_effect=lambda name: None if name in absent else original(name)), \
     patch('diagnostics.nvtop_status', return_value=(False, 'NVTOP não está instalado neste perfil.')):
    open_diagnostics(panel)
    buttons = {button.text(): button for button in panel.diagnostics_dialog.findChildren(QPushButton)}
    for title in ('Resumo do sistema · Fastfetch', 'Informações de CPU, GPU e RAM · Hardinfo2',
                  'Uso da GPU · NVTOP', 'Saúde dos discos · GSmartControl', 'Relatório de hardware · inxi'):
        assert not buttons[tr(title)].isEnabled(), title
        assert buttons[tr(title)].toolTip(), title
    assert buttons[tr('Gerenciador de dispositivos')].isEnabled()
    assert buttons[tr('Gerenciador de tarefas')].isEnabled()
for widget in app.topLevelWidgets():
    widget.close()
app.processEvents()
print('MINIMAL DIAGNOSTICS OK: optional actions disabled with explanation; devices and fallback task manager available')
