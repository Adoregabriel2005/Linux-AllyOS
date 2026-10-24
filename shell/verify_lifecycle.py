"""Fechar as preferências não deve encerrar o shell."""
import os
import sys
import tempfile
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

temporary = tempfile.TemporaryDirectory()
os.environ['XDG_CONFIG_HOME'] = temporary.name
from main import Panel

app = QApplication([])
sys.argv.append('--session')
panel = Panel()
panel.show()
completed = []


def close_preferences():
    panel.open_preferences()
    panel.preferences.close()
    QTimer.singleShot(500, check)


def check():
    assert panel.isVisible()
    completed.append(True)
    print('LIFECYCLE OK: fechar configuracoes mantem RoseShell ativa', flush=True)
    app.quit()


QTimer.singleShot(400, close_preferences)
app.exec()
assert completed, 'O shell encerrou ao fechar as preferencias'
