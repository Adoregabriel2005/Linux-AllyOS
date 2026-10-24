"""Verifica captura real, salvamento e clipboard no display X11 de teste."""
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from capture import Capture

app = QApplication(sys.argv)
window = Capture()


def check():
    assert window.image is not None and not window.image.isNull(), 'Captura vazia'
    assert window.image.save('/tmp/roseshell-capture-test.png')
    window.copy()
    assert not QApplication.clipboard().pixmap().isNull()
    print(f'CAPTURE OK: {window.image.width()}x{window.image.height()}, PNG e clipboard', flush=True)
    window.close()
    app.quit()


QTimer.singleShot(1000, check)
sys.exit(app.exec())
