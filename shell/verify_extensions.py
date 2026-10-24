"""Verifica seleção de dispositivos sem trocar a saída real durante o teste."""
import json
import os
from pathlib import Path
import tempfile
import wave

temporary = tempfile.TemporaryDirectory()
os.environ['XDG_CONFIG_HOME'] = temporary.name
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication, QComboBox
from main import Panel
from icons import illustrated_icon

app = QApplication([])
panel = Panel()
panel.status.shutdown()
if __import__('shutil').which('tux-manager'):
    assert not panel.tasks.window_icon('tux-manager.TuxManager').pixmap(48, 48).isNull(), 'Ícone XDG do TuxManager'
calls = []


def fake_run(args, callback):
    calls.append(args)
    if args[:3] == ['pactl', '--format=json', 'list']:
        source = args[3] == 'sources'
        devices = [{'name': 'usb.input' if source else 'usb.output',
                    'description': 'USB Audio'}]
        if source:
            devices += [{'name': 'usb.output.monitor', 'description': 'Monitor'}]
        callback(True, json.dumps(devices))
    elif args[0] == 'pactl' and args[1].startswith('get-default-'):
        callback(True, 'usb.input' if args[1].endswith('source') else 'usb.output')
    else:
        callback(True, '')


panel.status.run = fake_run
panel.status.open_volume()
dialog = panel.status.dialogs[-1]
choices = dialog.findChildren(QComboBox)
assert len(choices) == 2 and all(choice.count() == 1 for choice in choices)
assert not any('set-default' in ' '.join(call) for call in calls), 'Consultar não altera dispositivos'
choices[0].activated.emit(0)
choices[1].activated.emit(0)
assert ['pactl', 'set-default-sink', 'usb.output'] in calls
assert ['pactl', 'set-default-source', 'usb.input'] in calls
for kind in ('wine', 'jewel'):
    assert not illustrated_icon(kind).pixmap(128, 128).isNull()
with wave.open(str(Path(__file__).parent / 'assets/sounds/rose-entry.wav')) as sound:
    assert sound.getnchannels() == 1 and sound.getframerate() == 22050
    assert sound.getnframes() / sound.getframerate() < 2
dialog.close()
panel.tasks.shutdown()
for widget in app.topLevelWidgets():
    widget.close()
app.processEvents()
print('EXTENSIONS OK: consulta sem alterações, saída/entrada corretas, ícones e áudio original')
