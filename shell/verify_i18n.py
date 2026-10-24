"""Smoke de idioma real: widgets, catálogo XDG, Sobre, licença offline e diagnósticos."""
import os
import tempfile
from pathlib import Path
temporary = tempfile.TemporaryDirectory()
os.environ['XDG_CONFIG_HOME'] = temporary.name
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QTabWidget
from PySide6.QtCore import QSettings
from main import Panel
from i18n import language
from about import open_about
from diagnostics import open_diagnostics
from applications import installed_apps

app = QApplication([])
panel = Panel()
panel.show()
panel.open_preferences()
english = language() == 'en'
tabs = panel.preferences.findChild(QTabWidget)
assert tabs.tabText(0) == ('Appearance' if english else 'Aparência')
assert panel.preferences.windowTitle() == ('RoseShell — Settings' if english else 'RoseShell — Configurações')
panel.open_apps()
assert panel.library.search.placeholderText() == ('Search installed applications…' if english else 'Buscar nos aplicativos instalados…')
assert ' applications ' in panel.library.status.text() if english else ' aplicativos ' in panel.library.status.text()
open_about(panel)
assert 'gorigamia' in panel.about_dialog.findChild(QTabWidget).widget(0).toPlainText()
assert 'GNU GENERAL PUBLIC LICENSE' in panel.about_dialog.findChild(QTabWidget).widget(1).toPlainText()
open_diagnostics(panel)
assert panel.diagnostics_dialog.windowTitle() == ('Hardware diagnostics' if english else 'Diagnóstico de hardware')
names = [button.text() for button in panel.diagnostics_dialog.findChildren(QPushButton)]
assert any('Fastfetch' in name for name in names) and any('TuxManager' in name for name in names)
data = Path(temporary.name) / 'data'
(data / 'applications').mkdir(parents=True)
(data / 'applications' / 'fixture.desktop').write_text('[Desktop Entry]\nType=Application\nName=Hardware summary\nName[pt_BR]=Resumo do hardware\nExec=true\n', encoding='utf-8')
os.environ['XDG_DATA_HOME'] = str(data)
entry = next(a for a in installed_apps() if a['path'].endswith('fixture.desktop'))
assert entry['name'] == ('Hardware summary' if english else 'Resumo do hardware')
panel.status.shutdown()
panel.tasks.shutdown()
for widget in app.topLevelWidgets():
    widget.close()
app.processEvents()
print('I18N OK:', language(), 'catalogo, configuracoes, Sobre, GPL offline e diagnosticos', flush=True)
