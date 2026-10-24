"""Mantém texto, URLs e imagens copiados disponíveis enquanto RoseShell roda."""
from PySide6.QtCore import QObject, QMimeData, QTimer
from PySide6.QtWidgets import QApplication


class ClipboardKeeper(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.clipboard = QApplication.clipboard()
        self.generation = 0
        self.clipboard.dataChanged.connect(self.remember)

    def remember(self):
        if self.clipboard.ownsClipboard():
            return
        mime = self.clipboard.mimeData()
        if mime is None:
            return
        stored = QMimeData()
        if mime.hasText():
            stored.setText(mime.text())
        if mime.hasHtml():
            stored.setHtml(mime.html())
        if mime.hasUrls():
            stored.setUrls(mime.urls())
        if mime.hasImage():
            stored.setImageData(mime.imageData())
        if not stored.formats():
            return
        self.generation += 1
        generation = self.generation
        QTimer.singleShot(0, lambda: self.keep(stored, generation))

    def keep(self, stored, generation):
        if generation == self.generation:
            self.clipboard.setMimeData(stored)

    def release(self):
        self.generation += 1
        self.clipboard.dataChanged.disconnect(self.remember)
        if self.clipboard.ownsClipboard():
            self.clipboard.clear()
