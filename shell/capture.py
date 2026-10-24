"""Captura X11 por monitor, salva em arquivo ou copia para a área de transferência."""
from i18n import tr
import sys
import os
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QDateTime, QSettings
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QFileDialog, QComboBox, QMessageBox)


class Capture(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr('RoseShell — Captura de tela'))
        self.image = None
        layout = QVBoxLayout(self)
        self.screens = QComboBox()
        for screen in QApplication.screens():
            self.screens.addItem(screen.name(), screen)
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        self.screens.setCurrentIndex(QApplication.screens().index(screen))
        layout.addWidget(self.screens)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview, 1)
        row = QHBoxLayout()
        for text, action in [(tr('Nova captura'), self.take), (tr('Copiar'), self.copy), (tr('Salvar…'), self.save)]:
            button = QPushButton(text)
            button.clicked.connect(action)
            row.addWidget(button)
        layout.addLayout(row)
        rect = screen.availableGeometry()
        self.resize(min(760, rect.width() - 40), min(520, rect.height() - 40))
        QTimer.singleShot(200, self.take)

    def take(self):
        self.hide()
        QTimer.singleShot(250, self.grab_screen)

    def grab_screen(self):
        self.image = self.screens.currentData().grabWindow(0)
        if self.image.isNull():
            QMessageBox.warning(self, 'RoseShell', tr('A captura não está disponível nesta sessão gráfica.'))
        self.show()
        self.update_preview()

    def update_preview(self):
        if self.image is not None:
            self.preview.setPixmap(self.image.scaled(self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()

    def copy(self):
        if self.image is not None:
            QApplication.clipboard().setPixmap(self.image)

    def save(self):
        if self.image is None:
            return
        name = 'RoseShell-' + QDateTime.currentDateTime().toString('yyyyMMdd-HHmmss') + '.png'
        path, _ = QFileDialog.getSaveFileName(self, tr('Salvar captura'), str(Path.home() / name),
                                             'PNG (*.png);;JPEG (*.jpg);;WebP (*.webp)')
        if path and not self.image.save(path):
            QMessageBox.warning(self, 'RoseShell', tr('Não foi possível salvar a captura nesse formato ou caminho.'))


if __name__ == '__main__':
    os.environ.setdefault('QT_SCALE_FACTOR', str(QSettings('RoseShell', 'Desktop').value('scale', '1')))
    app = QApplication(sys.argv)
    window = Capture()
    sys.exit(app.exec())
