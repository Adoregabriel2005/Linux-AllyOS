"""Biblioteca de wallpapers e preferências de rotação persistentes."""
from i18n import tr
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QListView, QCheckBox, QComboBox, QHBoxLayout, QPushButton)


def bundled_wallpapers():
    return sorted((Path(__file__).parent / 'assets' / 'wallpapers').glob('*.png'))


def wallpaper_variant(path, width, height, aspect='auto'):
    root = Path(__file__).parent / 'assets' / 'wallpapers'
    source = Path(path)
    try:
        source.resolve().relative_to(root.resolve())
    except ValueError:
        return source
    ratios = {'5x4': 5 / 4, '16x9': 16 / 9, '4x3': 4 / 3}
    selected = aspect if aspect in ratios else min(ratios, key=lambda key: abs(ratios[key] - width / max(height, 1)))
    variant = root / 'variants' / selected / source.name
    return variant if variant.is_file() else source


class WallpaperLibrary(QDialog):
    def __init__(self, panel):
        super().__init__(panel)
        self.panel = panel
        self.setWindowTitle(tr('RoseShell — Papéis de parede'))
        self.resize(760, 560)
        layout = QVBoxLayout(self)
        title = QLabel(tr('COLEÇÃO ROSESHELL'))
        title.setStyleSheet('font-size: 21px; font-weight: bold; padding: 12px; border-bottom: 3px solid #c58f9d;')
        layout.addWidget(title)
        description = QLabel(tr('Escolha uma ilustração para fixar ou ative a troca automática.'))
        description.setWordWrap(True)
        layout.addWidget(description)
        self.list = QListWidget()
        self.list.setViewMode(QListView.ViewMode.IconMode)
        self.list.setMovement(QListView.Movement.Static)
        self.list.setResizeMode(QListView.ResizeMode.Adjust)
        self.list.setIconSize(QSize(190, 108))
        self.list.setGridSize(QSize(220, 145))
        self.list.setWordWrap(True)
        for path in bundled_wallpapers():
            item = QListWidgetItem(QIcon(str(path)), path.stem[3:].replace('-', ' ').title())
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.list.addItem(item)
        self.list.itemClicked.connect(self.select)
        layout.addWidget(self.list, 1)
        row = QHBoxLayout()
        self.rotate = QCheckBox(tr('Trocar automaticamente'))
        self.rotate.setChecked(panel.settings.value('wallpaper_rotate', 'false') == 'true')
        self.rotate.toggled.connect(self.rotation)
        row.addWidget(self.rotate)
        self.interval = QComboBox()
        for minutes in (1, 5, 15, 30, 60):
            self.interval.addItem(tr(f'A cada {minutes} min'), minutes)
        current = int(panel.settings.value('wallpaper_minutes', 15))
        self.interval.setCurrentIndex(max(0, self.interval.findData(current)))
        self.interval.currentIndexChanged.connect(lambda _: self.rotation(self.rotate.isChecked()))
        row.addWidget(self.interval)
        layout.addLayout(row)
        button = QPushButton(tr('Escolher outra imagem…'))
        button.clicked.connect(panel.choose_wallpaper)
        layout.addWidget(button)
        mode = QComboBox()
        for key, label in [('fit', tr('Ajustar sem cortar')), ('fill', tr('Preencher a tela')),
                           ('center', tr('Centralizar')), ('stretch', tr('Esticar'))]:
            mode.addItem(label, key)
        mode.setCurrentIndex(max(0, mode.findData(panel.settings.value('wallpaper_mode', 'fit'))))
        mode.currentIndexChanged.connect(lambda _: panel.set_wallpaper_mode(mode.currentData()))
        layout.addWidget(mode)
        aspect = QComboBox()
        for key, label in [('auto', tr('Proporção automática por monitor')), ('5x4', tr('Versão 5:4')),
                           ('16x9', tr('Versão 16:9')), ('4x3', tr('Versão 4:3'))]:
            aspect.addItem(label, key)
        aspect.setCurrentIndex(max(0, aspect.findData(panel.settings.value('wallpaper_aspect', 'auto'))))
        aspect.currentIndexChanged.connect(lambda _: self.set_aspect(aspect.currentData()))
        layout.addWidget(aspect)

    def set_aspect(self, aspect):
        self.panel.settings.setValue('wallpaper_aspect', aspect)
        for desktop in self.panel.desktops:
            desktop.update()

    def select(self, item):
        self.rotate.setChecked(False)
        self.panel.settings.setValue('wallpaper_rotate', 'false')
        self.panel.set_wallpaper(item.data(Qt.ItemDataRole.UserRole))
        self.panel.configure_rotation()

    def rotation(self, enabled):
        self.panel.settings.setValue('wallpaper_rotate', 'true' if enabled else 'false')
        self.panel.settings.setValue('wallpaper_minutes', self.interval.currentData())
        self.panel.configure_rotation()
