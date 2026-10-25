"""Indicadores reais do Linux e controles assíncronos, sem privilégios root."""
from i18n import tr
import json
import locale
import os
from pathlib import Path
import re
import shutil

from PySide6.QtCore import QProcess, QTimer, Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QGridLayout, QPushButton, QDialog,
    QVBoxLayout, QLabel, QSlider, QPlainTextEdit, QHBoxLayout, QComboBox, QMessageBox, QScrollArea)
from icons import illustrated_icon
from shiboken6 import isValid


def read(path):
    try:
        return Path(path).read_text(errors='replace').strip()
    except OSError:
        return ''


def network_state():
    interfaces = []
    for path in sorted(Path('/sys/class/net').glob('*')):
        if path.name == 'lo':
            continue
        kind = 'Wi-Fi' if (path / 'wireless').exists() else tr('Cabo')
        interfaces.append((path.name, kind, read(path / 'operstate')))
    active = [entry for entry in interfaces if entry[2] == 'up']
    return active, interfaces


def usb_devices():
    devices = []
    for path in sorted(Path('/sys/bus/usb/devices').glob('*')):
        if ':' in path.name or path.name.startswith('usb'):
            continue  # Excluir interfaces e hubs raiz.
        if (path / 'idVendor').exists():
            devices.append(' '.join(filter(None, [read(path / 'manufacturer'), read(path / 'product')])) or path.name)
    return devices


class StatusArea(QWidget):
    def __init__(self, panel):
        super().__init__(panel)
        self.panel = panel
        self.processes = []
        self.volume = None
        self.audio_backend = None
        self.disks = []
        self.dialogs = []
        self.stopping = False
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.buttons = {}
        actions = [('volume', self.open_volume), ('network', self.open_network),
                   ('usb', self.open_devices), ('disk', self.open_devices),
                   ('language', self.open_language), ('capture', panel.capture)]
        for index, (kind, callback) in enumerate(actions):
            button = QPushButton()
            button.setIcon(illustrated_icon(kind))
            button.setIconSize(QSize(21, 21))
            button.setFixedSize(23, 25)
            button.clicked.connect(callback)
            layout.addWidget(button, index // 2, index % 2)
            self.buttons[kind] = button
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(10000 if panel.settings.value('performance', 'economy') == 'economy' else 5000)
        self.refresh()

    def run(self, args, callback):
        if self.stopping:
            return
        if not shutil.which(args[0]):
            callback(False, tr(f'{args[0]} indisponível'))
            return
        process = QProcess(self)
        self.processes.append(process)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        timer = QTimer(process)
        timer.setSingleShot(True)
        timer.timeout.connect(process.kill)
        process.finished.connect(lambda code, status: finished(code))
        settled = False
        def finished(code):
            nonlocal settled
            if settled or not isValid(process):
                return
            settled = True
            timer.stop()
            output = bytes(process.readAllStandardOutput()).decode(errors='replace').strip()
            try:
                if not self.stopping:
                    callback(code == 0, output)
            except RuntimeError:
                pass  # O usuário pode ter fechado o diálogo durante a consulta.
            finally:
                if process in self.processes:
                    self.processes.remove(process)
                process.deleteLater()
        process.errorOccurred.connect(lambda error: finished(-1)
            if error == QProcess.ProcessError.FailedToStart else None)
        process.start(args[0], args[1:])
        timer.start(4000)

    def shutdown(self):
        self.stopping = True
        self.timer.stop()
        for process in list(self.processes):
            if isValid(process):
                process.finished.disconnect()
                if process.state() != QProcess.ProcessState.NotRunning:
                    process.kill()
                    process.waitForFinished(300)
                process.deleteLater()
        self.processes.clear()

    def refresh(self):
        active, interfaces = network_state()
        self.buttons['network'].setToolTip(tr('Rede: ') + (', '.join(f'{kind} · {name}' for name, kind, _ in active) or tr('sem enlace ativo')))
        self.buttons['network'].setIcon(illustrated_icon(('wifi' if any(kind == 'Wi-Fi' for _, kind, _ in active) else 'network') if active else 'network-off'))
        devices = usb_devices()
        self.buttons['usb'].setToolTip(tr(f'USB: {len(devices)} dispositivos\n') + '\n'.join(devices))
        self.buttons['usb'].setProperty('connected', bool(devices))
        self.buttons['usb'].setIcon(illustrated_icon('usb' if devices else 'usb-off'))
        from i18n import language as interface_language
        language = interface_language()
        self.buttons['language'].setToolTip(tr('Idioma: ') + language)
        self.buttons['language'].setIcon(QIcon())
        self.buttons['language'].setText('EN' if language == 'en' else 'BR')
        self.buttons['capture'].setToolTip(tr('Captura de tela · Print Screen'))
        self.run(['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,TRAN,MODEL,MOUNTPOINTS,RM'], self.disk_result)
        if shutil.which('wpctl'):
            self.run(['wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'], self.wp_volume)
        else:
            self.pulse_volume()

    def disk_result(self, ok, output):
        try:
            self.disks = json.loads(output).get('blockdevices', []) if ok else []
        except ValueError:
            self.disks = []
        disks = [disk for disk in self.disks if disk.get('type') == 'disk']
        self.buttons['disk'].setToolTip(tr(f'Discos conectados: {len(disks)}\n') + '\n'.join(
            f'{disk["name"]} · {disk.get("size", "")} · {disk.get("model") or ""}' for disk in disks))
        self.buttons['disk'].setIcon(illustrated_icon('disk' if disks else 'disk-off'))

    def wp_volume(self, ok, output):
        match = re.search(r'Volume:\s*([0-9.]+)', output) if ok else None
        if match:
            self.audio_backend = 'wpctl'
            self.volume = round(float(match[1]) * 100)
            self.buttons['volume'].setToolTip(f'Volume: {self.volume}%' + (tr(' · mudo') if 'MUTED' in output else ''))
            self.buttons['volume'].setIcon(illustrated_icon('volume-off' if 'MUTED' in output else 'volume'))
        else:
            self.pulse_volume()

    def pulse_volume(self):
        self.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], self.pulse_result)

    def pulse_result(self, ok, output):
        match = re.search(r'(\d+)%', output) if ok else None
        self.audio_backend = 'pactl' if match else None
        self.volume = int(match[1]) if match else None
        self.buttons['volume'].setToolTip(f'Volume: {self.volume}%' if match else tr('Áudio: nenhuma saída disponível'))
        self.buttons['volume'].setIcon(illustrated_icon('volume' if match else 'volume-off'))
        if match:
            self.run(['pactl', 'get-sink-mute', '@DEFAULT_SINK@'], lambda ok, out: self.buttons['volume'].setIcon(
                illustrated_icon('volume-off' if ok and re.search(r'(yes|sim|true)$', out) else 'volume')))

    def dialog(self, title):
        dialog = QDialog(self.panel)
        dialog.setWindowTitle('RoseShell — ' + title)
        rect = self.panel.screen().availableGeometry()
        dialog.resize(min(650, rect.width() - 70), min(440, rect.height() - 45))
        self.dialogs.append(dialog)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.destroyed.connect(lambda: self.dialogs.remove(dialog) if dialog in self.dialogs else None)
        outer = QVBoxLayout(dialog)
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        body = QWidget(scroll)
        layout = QVBoxLayout(body)
        scroll.setWidget(body)
        outer.addWidget(scroll)
        heading = QLabel(title)
        heading.setStyleSheet('font-size: 19px; font-weight: bold; padding: 8px; border-bottom: 2px solid #bf8a9a;')
        layout.addWidget(heading)
        return dialog, layout

    def open_volume(self):
        dialog, layout = self.dialog('Volume')
        label = QLabel(f'{self.volume}%' if self.volume is not None else tr('Nenhuma saída de áudio disponível'))
        layout.addWidget(label)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(min(self.volume or 0, 100))
        slider.setEnabled(self.audio_backend is not None)
        debounce = QTimer(dialog)
        debounce.setSingleShot(True)
        debounce.timeout.connect(lambda: self.audio_action('volume', str(slider.value()) + '%', label))
        slider.valueChanged.connect(lambda value: (label.setText(f'{value}%'), debounce.start(150)))
        layout.addWidget(slider)
        mute = QPushButton(tr('Ativar / desativar mudo'))
        mute.setEnabled(self.audio_backend is not None)
        mute.clicked.connect(lambda: self.audio_action('mute', 'toggle', label))
        layout.addWidget(mute)
        for facility, title in [('sinks', tr('Saída de som')), ('sources', tr('Entrada / microfone'))]:
            layout.addWidget(QLabel(title))
            choice = QComboBox(dialog)
            choice.setEnabled(False)
            layout.addWidget(choice)
            def loaded(ok, output, combo=choice, kind=facility):
                if not isValid(combo):
                    return
                combo.blockSignals(True)
                combo.clear()
                try:
                    devices = json.loads(output) if ok else []
                    for device in devices:
                        name = device.get('name', '')
                        if name and not (kind == 'sources' and name.endswith('.monitor')):
                            combo.addItem(device.get('description') or name, name)
                except (ValueError, TypeError, AttributeError):
                    combo.clear()
                combo.setEnabled(combo.count() > 0)
                combo.blockSignals(False)
                def selected(ok, name):
                    if isValid(combo):
                        combo.blockSignals(True)
                        combo.setCurrentIndex(max(0, combo.findData(name.strip())))
                        combo.blockSignals(False)
                self.run(['pactl', 'get-default-sink' if kind == 'sinks' else 'get-default-source'], selected)
            self.run(['pactl', '--format=json', 'list', facility], loaded)
            def activate(index, combo=choice, kind=facility):
                name = combo.itemData(index)
                if name:
                    self.run(['pactl', 'set-default-sink' if kind == 'sinks' else 'set-default-source', name],
                             lambda ok, out: label.setText(tr('Aplicado') if ok else out))
            choice.activated.connect(activate)
        advanced = QPushButton(tr('Mixer, perfis e áudio dos aplicativos…'))
        advanced.setEnabled(shutil.which('pavucontrol') is not None)
        advanced.clicked.connect(lambda: self.panel.launch([['pavucontrol']]))
        layout.addWidget(advanced)
        devices = QPushButton(tr('Dispositivos de áudio e drivers…'))
        devices.clicked.connect(self.open_audio_devices)
        layout.addWidget(devices)
        layout.addStretch()
        dialog.show()

    def open_audio_devices(self):
        dialog, layout = self.dialog(tr('Dispositivos de áudio e drivers'))
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(tr('Interfaces USB compatíveis usam ALSA, PipeWire e WirePlumber. A detecção abaixo informa os dispositivos presentes; não confirma compatibilidade de modelos ausentes.'))
        layout.addWidget(text)
        self.run(['aplay', '-l'], lambda ok, out: text.appendPlainText('\nALSA — playback\n' + out))
        self.run(['arecord', '-l'], lambda ok, out: text.appendPlainText('\nALSA — capture\n' + out))
        self.run(['lsusb', '-t'], lambda ok, out: text.appendPlainText('\nUSB / drivers\n' + out))
        self.run(['lsusb'], lambda ok, out: text.appendPlainText('\nUSB IDs\n' + out))
        dialog.show()

    def audio_action(self, action, value, label):
        if self.audio_backend == 'wpctl':
            args = ['wpctl', 'set-volume' if action == 'volume' else 'set-mute', '@DEFAULT_AUDIO_SINK@', value]
        else:
            args = ['pactl', 'set-sink-volume' if action == 'volume' else 'set-sink-mute', '@DEFAULT_SINK@', value]
        self.run(args, lambda ok, output: label.setText(tr('Aplicado') if ok else output))
        QTimer.singleShot(300, self.refresh)

    def open_network(self):
        dialog, layout = self.dialog(tr('Conexões de rede'))
        text = QPlainTextEdit()
        text.setReadOnly(True)
        _, interfaces = network_state()
        text.setPlainText('\n'.join(f'{name} · {kind} · {state}' for name, kind, state in interfaces) or tr('Nenhuma interface encontrada'))
        layout.addWidget(text)
        self.run(['ip', '-brief', 'address'], lambda ok, out: text.appendPlainText('\n' + out))
        button = QPushButton(tr('Configurar conexões…'))
        button.setEnabled(shutil.which('nm-connection-editor') is not None)
        button.setToolTip(tr('Editor de conexões do NetworkManager'))
        button.clicked.connect(lambda: self.panel.launch([['nm-connection-editor']]))
        layout.addWidget(button)
        dialog.show()

    def open_devices(self):
        dialog, layout = self.dialog(tr('Gerenciador de dispositivos'))
        text = QPlainTextEdit()
        text.setReadOnly(True)
        layout.addWidget(text)
        def refresh():
            text.setPlainText('USB\n' + ('\n'.join(usb_devices()) or tr('Nenhum dispositivo USB externo detectado')) + tr('\n\nDISCOS E PARTIÇÕES\n'))
            def disks_done(ok, out):
                text.appendPlainText(out + tr('\n\nDISPOSITIVOS PCI / DRIVERS\n'))
                self.run(['lspci', '-nnk'], lambda ok, out: text.appendPlainText(out))
            self.run(['lsblk', '-o', 'NAME,SIZE,TYPE,TRAN,MODEL,MOUNTPOINTS'],
                     disks_done)
        button = QPushButton(tr('Atualizar dispositivos'))
        button.clicked.connect(refresh)
        layout.addWidget(button)
        refresh()
        dialog.show()

    def open_language(self):
        dialog, layout = self.dialog(tr('Idioma e teclado'))
        from i18n import language
        choice = QComboBox()
        choice.addItem('Português (Brasil)', 'pt_BR')
        choice.addItem('English', 'en')
        choice.setCurrentIndex(max(0, choice.findData(language())))
        def save_language():
            self.panel.settings.setValue('language', choice.currentData())
            QMessageBox.information(dialog, 'RoseShell',
                'Idioma salvo. Entre novamente na sessão para aplicar.\nLanguage saved. Sign in again to apply.')
        choice.currentIndexChanged.connect(save_language)
        layout.addWidget(QLabel(tr('Idioma da interface')))
        layout.addWidget(choice)
        label = QLabel(tr('Idioma do sistema: ') + (locale.getlocale()[0] or os.environ.get('LANG', 'C')))
        layout.addWidget(label)
        info = QPlainTextEdit()
        info.setReadOnly(True)
        layout.addWidget(info)
        self.run(['setxkbmap', '-query'], lambda ok, out: info.setPlainText(out))
        row = QHBoxLayout()
        for layout_name, title in [('br', tr('Teclado brasileiro')), ('us', tr('Teclado americano'))]:
            button = QPushButton(title)
            button.clicked.connect(lambda checked=False, name=layout_name: self.set_keyboard(name, info))
            row.addWidget(button)
        layout.addLayout(row)
        dialog.show()

    def set_keyboard(self, name, info):
        self.run(['setxkbmap', name], lambda ok, out: info.setPlainText(tr('Teclado aplicado: ') + name if ok else out))
        self.panel.settings.setValue('keyboard', name)
