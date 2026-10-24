"""Clipboard X11 continua disponível após o aplicativo de origem encerrar."""
import subprocess
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from clipboard import ClipboardKeeper

app = QApplication(sys.argv)
keeper = ClipboardKeeper(app)
child = subprocess.Popen([sys.executable, '-c',
    'from PySide6.QtWidgets import QApplication; from PySide6.QtCore import QTimer; '
    'a=QApplication([]); a.clipboard().setText("RoseShell clipboard test"); '
    'QTimer.singleShot(1200,a.quit); a.exec()'])


def check():
    assert child.poll() is not None
    assert app.clipboard().text() == 'RoseShell clipboard test'
    print('CLIPBOARD OK: conteudo preservado apos fechar origem', flush=True)
    app.quit()


QTimer.singleShot(2000, check)
sys.exit(app.exec())
