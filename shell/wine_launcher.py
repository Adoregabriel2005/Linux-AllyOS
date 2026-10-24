"""Entrada Wine: execução escolhida pelo usuário, sem shell nem instalação automática."""
from pathlib import Path
import shutil
import sys
from PySide6.QtCore import QProcess, QSettings
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from i18n import tr
from icons import illustrated_icon


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    if QSettings('RoseShell', 'Desktop').value('theme', 'dark') != 'light':
        palette = app.palette()
        for role, color in [(QPalette.ColorRole.Window, '#191c1e'),
                            (QPalette.ColorRole.WindowText, '#eee7dc'),
                            (QPalette.ColorRole.Button, '#303537'),
                            (QPalette.ColorRole.ButtonText, '#eee7dc')]:
            palette.setColor(role, QColor(color))
        app.setPalette(palette)
    dialog = QDialog()
    dialog.setWindowTitle('Wine · RoseShell')
    dialog.setWindowIcon(illustrated_icon('wine'))
    dialog.resize(440, 230)
    layout = QVBoxLayout(dialog)
    image = QLabel()
    image.setPixmap(illustrated_icon('wine').pixmap(64, 64))
    layout.addWidget(image)
    text = QLabel(tr('Escolha um programa Windows ou abra a configuração do Wine.'))
    text.setWordWrap(True)
    layout.addWidget(text)

    def launch(path):
        target = Path(path)
        if not target.is_file() or target.suffix.lower() not in ('.exe', '.msi'):
            return
        wine = shutil.which('wine')
        if not wine:
            QMessageBox.information(dialog, 'Wine', tr('Wine não está instalado neste perfil.'))
            return
        arguments = ['msiexec', '/i', str(target)] if target.suffix.lower() == '.msi' else [str(target)]
        ok, _ = QProcess.startDetached(wine, arguments, str(target.parent))
        if not ok:
            QMessageBox.warning(dialog, 'Wine', tr('Não foi possível iniciar o Wine.'))

    def choose():
        path, _ = QFileDialog.getOpenFileName(dialog, tr('Abrir programa Windows'), str(Path.home()),
                                            'Windows (*.exe *.EXE *.msi *.MSI)')
        if path:
            launch(path)

    button = QPushButton(tr('Abrir programa Windows…'))
    button.clicked.connect(choose)
    layout.addWidget(button)
    config = QPushButton(tr('Configurar Wine…'))
    config.setEnabled(shutil.which('winecfg') is not None)
    config.clicked.connect(lambda: QProcess.startDetached('winecfg', []))
    layout.addWidget(config)
    dialog.show()
    if len(sys.argv) == 2:
        launch(str(Path(sys.argv[1]).resolve()))
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
